# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import BaseHTTPServer
from urlparse import urlparse, parse_qs
from mimetypes import types_map
import urllib2
from PIL import Image, ImageDraw, ImageFont

URL   = "http://fjas.no:8181/messages"
WHITE = 1
BLACK = 0

default_messages = [
        { 'x': 25, 'y': 70, 'text':'hei på deg', 'fontsize': 22 }
]
messages = default_messages

fonts = {
        36: ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSerif-Italic.ttf', 36),
        22: ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSerif-Italic.ttf', 22),
        20: ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSerif-Italic.ttf', 20),
}

def getImage(size, messages):
    image = Image.new('1', size, WHITE)
    draw = ImageDraw.Draw(image)

    #print 'messages %r' % messages
    for msg in messages:
        #print '(%r, %r), %r, %r' % (msg['x'],  msg['y'], msg['text'], msg['fontsize'])
        try:
            draw.text(( msg['x'],  msg['y']), msg['text'].decode('utf-8'), fill=BLACK, font=fonts[msg['fontsize']])
        except:
            draw.text(( msg['x'],  msg['y']), msg['text'],                 fill=BLACK, font=fonts[msg['fontsize']])

    return image

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global messages

        #print self.path
        if self.path == '/' or self.path.startswith('/?'):
            qs = parse_qs(urlparse(self.path).query)
            if qs.has_key('messages'):
                messages = json.loads(qs['messages'][0])
                for msg in messages:
                    msg['text'] = msg['text'].encode('utf-8')
            # TODO: Add reset button to go back to default
            #else:
            #    messages = default_messages
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            messages_string = '[\n    %s\n]' % ',\n    '.join(
                    ['{"x": %d, "y": %d, "fontsize": %d, "text": "%s"}'
                        % (msg['x'],  msg['y'], msg['fontsize'], msg['text']) for msg in messages])
            #print "1: %r" % (messages_string)
            self.wfile.write(INDEX_HTML.replace('MESSAGES', messages_string))
            #self.wfile.write(INDEX_HTML.replace('MESSAGES', repr(messages)))
        elif self.path == '/messages':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            json.dump(messages, self.wfile)
        elif self.path == '/fisken.png':
            image = getImage((264,176), messages)
            img_type = 'png'
            self.send_response(200)
            self.send_header('Content-type', types_map['.' + img_type])
            self.end_headers()
            image.save(self.wfile, img_type)
            #print 'image saved'
        else:
            self.send_error(404)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
  </style>
</head>
<body>

<div class="container">
    <h2>hei</h2>
    <form name='fisk' action=''>
        <p><textarea name='messages' rows='8' cols='80'>MESSAGES</textarea></p>
        <p><input type='submit' /></p>
    </form>
    <img border="1px solid black" src="fisken.png"/>
</div> <!-- end container -->

</body>

<script type="text/javascript">
    console.log("hei");
</script>

</html>
"""

def listsDifferent(messages, previous_messages):
    if not len(messages) == len(previous_messages): return True
    for i in range(len(messages)):
        if not messages[i]       ['x'] == previous_messages[i]['x']: return True
        if not messages[i]       ['y'] == previous_messages[i]['y']: return True
        if not messages[i][    'text'] == previous_messages[i]['text']: return True
        if not messages[i]['fontsize'] == previous_messages[i]['fontsize']: return True
    return False

def main_display():
    from EPD import EPD
    epd = EPD()
    #epd.clear()

    previous_messages = []
    while True:
        try:
            messages = json.loads(urllib2.urlopen("http://fjas.no:8181/messages").read())
        except: #urllib2.URLError:
            print "Got problems, sleeping 13s"
            time.sleep(13)
            continue
        #messages = [ { 'x': 25, 'y': 70, 'text':'hei på deg', 'fontsize': 22 } ]
        if not listsDifferent(messages, previous_messages):
            print "No change, sleeping 1.3s"
            time.sleep(1.300)
            continue
        previous_messages = messages

        print "Got new message, updating screen"
        image = getImage(epd.size, messages)

        epd.display(image)
        epd.update()

def main_server():
    httpd = BaseHTTPServer.HTTPServer(('', 8181), MyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if "__main__" == __name__:
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        main_server()
    else:
        main_display()

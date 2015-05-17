# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import BaseHTTPServer
from urlparse import urlparse, parse_qs
from mimetypes import types_map
from PIL import Image, ImageDraw, ImageFont

WHITE = 1
BLACK = 0

default_messages = [
        { 'x': 25, 'y': 70, 'text':'hei på deg', 'fontsize': 22 }
]
messages = default_messages

fonts = {
        36: ImageFont.truetype('/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf', 36),
        22: ImageFont.truetype('/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf', 22),
        20: ImageFont.truetype('/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf', 20),
}

def getImage(size, messages):
    image = Image.new('1', size, WHITE)
    draw = ImageDraw.Draw(image)

    #print 'messages %r' % messages
    for msg in messages:
        #print '(%r, %r), %r, %r' % (msg['x'],  msg['y'], msg['text'], msg['fontsize'])
        draw.text(( msg['x'],  msg['y']), msg['text'].decode('utf-8'), fill=WHITE, font=fonts[msg['fontsize']])

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
            else:
                messages = default_messages
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
        <textarea name='messages' rows='5' cols='80'>MESSAGES</textarea>
        <input type='submit' />
    </form>
    <img src="fisken.png"/>
</div> <!-- end container -->

</body>

<script type="text/javascript">
    console.log("hei");
</script>

</html>
"""

if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(('', 8181), MyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


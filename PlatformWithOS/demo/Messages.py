# -*- coding: utf-8 -*-

import json
import time
import urllib2
from PIL import Image, ImageDraw, ImageFont
from EPD import EPD

URL   = "http://fjas.no:8181/messages"
WHITE = 1
BLACK = 0

fonts = {
        #36: ImageFont.truetype('/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf', 36),
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
        draw.text(( msg['x'],  msg['y']), msg['text'], fill=BLACK, font=fonts[msg['fontsize']])

    return image

def listsDifferent(messages, previous_messages):
    if not len(messages) == len(previous_messages): return True
    for i in range(len(messages)):
        if not messages[i]['x'] == previous_messages[i]['x']: return True
    return False

def main():
    epd = EPD()
    #epd.clear()

    previous_messages = []
    while True:
        try:
            messages = json.loads(urllib2.urlopen("http://fjas.no:8181/messages").read())
        except: #urllib2.URLError:
            time.sleep(3)
            continue
        #messages = [ { 'x': 25, 'y': 70, 'text':'hei på deg', 'fontsize': 22 } ]
        if not listsDifferent(messages, previous_messages):
            time.sleep(1.300)
            continue
        previous_messages = messages

        image = getImage(epd.size, messages)

        epd.display(image)
        epd.update()

if "__main__" == __name__:
    main()

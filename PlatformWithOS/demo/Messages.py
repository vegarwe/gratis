# -*- coding: latin-1 -*-

# Copyright 2013 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

from PIL import Image, ImageDraw, ImageFont
from EPD import EPD

WHITE = 1
BLACK = 0

def main():
    epd = EPD()
    #epd.clear()
    image = Image.new('1', epd.size, WHITE)
    draw = ImageDraw.Draw(image)

    font_large   = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSerif-Italic.ttf', 36)
    font_smaller = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSerif-Italic.ttf', 22)
    font_small   = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSerif-Regular.ttf', 20)
    #draw.text(( 20,  20), 'Hei Shnupp!', fill=BLACK, font=font_large)
    draw.text(( 25,  70), '... glad i deg også!', fill=BLACK, font=font_smaller)
    #draw.text(( 20, 100), 'deg, du er en knupp!', fill=BLACK, font=font_smaller)
    #draw.text((155, 130), 'Raiom', fill=BLACK, font=font_small)

    epd.display(image)
    epd.update()

if "__main__" == __name__:
    main()

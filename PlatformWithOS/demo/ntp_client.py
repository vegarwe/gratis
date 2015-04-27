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

from PIL      import Image, ImageDraw, ImageFont
from EPD      import EPD
from optparse import OptionParser

import datetime
import socket
import struct
import time
import math

EPOCH = 2208988800L

WHITE = 1
BLACK = 0

# https://www.ietf.org/rfc/rfc5905.txt

class NTPSample(object):
    def __init__(self, li, vn, mode, stratum, poll, prec, root_delay, root_disp, ref_clock_id, ref_time_int, ref_time_frac, orig_time_int, orig_time_frac, recv_time_int, recv_time_frac, trans_time_int, trans_time_frac):
        self.li              = li
        self.vn              = vn
        self.mode            = mode
        self.stratum         = stratum
        self.poll            = poll
        self.prec            = prec
        self.root_delay      = root_delay
        self.root_disp       = root_disp
        self.ref_clock_id    = ref_clock_id
        self.ref_time_int    = ref_time_int
        self.ref_time_frac   = ref_time_frac
        self.orig_time_int   = orig_time_int
        self.orig_time_frac  = orig_time_frac
        self.recv_time_int   = recv_time_int
        self.recv_time_frac  = recv_time_frac
        self.trans_time_int  = trans_time_int
        self.trans_time_frac = trans_time_frac

    def get_leap(self):
        if self.li ==  0: return 'no leap second'
        if self.li ==  1: return 'last minute of the day has 61 seconds'
        if self.li ==  2: return 'last minute of the day has 59 seconds'
        if self.li ==  3: return 'unknown (clock unsynchronized)'

    def get_mode(self):
        if self.mode ==  0: return 'reserved'
        if self.mode ==  1: return 'symmetric active'
        if self.mode ==  2: return 'symmetric passive'
        if self.mode ==  3: return 'client'
        if self.mode ==  4: return 'server'
        if self.mode ==  5: return 'broadcast'
        if self.mode ==  6: return 'NTP control message'
        if self.mode ==  7: return 'reserved for private use'

    def get_stratum(self):
        if self.stratum ==  0: return 'unspecified or invalid'
        if self.stratum ==  1: return 'primary server (e.g., equipped with a GPS receiver)'
        if 2 <= self.stratum and self.stratum <= 15:
                               return 'secondary server (via NTP)'
        if self.stratum == 16: return 'unsynchronized'
        if self.stratum >= 17: return 'reserved'

    def get_ref_clock(self):
        if self.stratum < 2:   return  ''.join([chr(i) for i in self.ref_clock_id])
        else:                  return '.'.join([str(i) for i in self.ref_clock_id])

    def _get_time(self, time_int, time_frac):
        return (time_int-EPOCH) + (time_frac / 2.**32)

    def get_orig_time(self):
        return self._get_time(self.orig_time_int, self.orig_time_frac)

    def get_rec_time(self):
        return self._get_time(self.recv_time_int, self.recv_time_frac)

    def get_xmt_time(self):
        return self._get_time(self.trans_time_int, self.trans_time_frac)

    @staticmethod
    def from_binary(data):
        args = []
        msg = struct.unpack('!2B2b2I4B8I', data) # 2x unsigned char, signed char, 2x unsigned int, 4x unsigned char, 8x unsigned int
        args = (
                (msg[ 0] >> 6) & 0b011,  # li
                (msg[ 0] >> 3) & 0b111,  # vn
                (msg[ 0] >> 0) & 0b111,  # mode
                 msg[ 1],                # stratum
                 msg[ 2],                # poll
                 msg[ 3],                # prec
                 msg[ 4],                # root delay
                 msg[ 5],                # root_disp
                 msg[6:10],              # ref_clock_id
                 msg[10],                # ref_time_int
                 msg[11],                # ref_time_frac
                 msg[12],                # orig_time_int
                 msg[13],                # orig_time_frac
                 msg[14],                # recv_time_int
                 msg[15],                # recv_time_frac
                 msg[16],                # trans_time_int
                 msg[17],                # trans_time_frac
            )
        return NTPSample(*args)


def demo(now):
    epd = EPD('/tmp/epd')
    #print('panel = {p:s} {w:d} x {h:d}  version={v:s} COG={g:d}'.format(p=epd.panel, w=epd.width, h=epd.height, v=epd.version, g=epd.cog))
    #epd.clear()

    #font = ImageFont.truetype("freesansbold.ttf", 12)
    font = ImageFont.truetype('/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf', 56)
    image = Image.new('1', epd.size, WHITE)
    draw  = ImageDraw.Draw(image)

    draw.text((30, 30), '%s' % now.strftime('%H:%M'), fill=BLACK, font=font)

    epd.display(image)
    epd.update()

def get_sample(options, args):
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    client.settimeout(1)
    o_time = time.time()
    o_frac, o_int = math.modf( o_time + EPOCH )
    o_int  = int(o_int)               # Origin time integer part
    o_frac = int(o_frac*0x100000000L) # Origin time fractional part
    data   = '\x1b' + 23 * '\0' + struct.pack('!2I', o_int, o_frac) +  16 * '\0'

    try:
        client.sendto( data, ( options.server, 123 ))
        data, address = client.recvfrom( 1024 )
        dest = time.time()
    except socket.gaierror:
        print "Network error"
        return
    except socket.timeout:
        print "timeout"
        return
    except socket.error:
        print "Error"
        return

    s = NTPSample.from_binary(data)

    try:
        org = datetime.datetime.fromtimestamp(o_time)
        rec = datetime.datetime.fromtimestamp(s.get_rec_time())
        xmt = datetime.datetime.fromtimestamp(s.get_xmt_time())
        dst = datetime.datetime.fromtimestamp(dest)
    except:
        # '\xdc\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00RATE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        print repr(data)
        return

   # print '\tFrom        %s:%s,' % ( '.'.join(map(str, address[:-1])), address[-1])
   # print '\tmode:       %s,' % (s.get_mode())
   # print '\tref clock:  %s,' % (s.get_ref_clock())
   # print '\tstratum:    %s,' % (s.get_stratum())
   ##print '\tleap:       %s,    version: %s' % (s.get_leap(), s.vn)
   ##print '\troot delay: %s,      root disperison: %s,' % (s.root_delay, s.root_disp)
   ##print '\tpoll:       %s,               precision: %s,' % (s.poll, s.prec)
    print '\trec_time_d: %s %s'    % (s.get_rec_time(), s.get_xmt_time())
   ##print '\torg_time:   %s'       %  org
   ##print '\trec_time:   %s'       %  rec
   ##print '\txmt_time:   %s'       %  xmt
   ##print '\tdst_time:   %s'       %  dst
   # print '\tdelta:      %r'       %(((rec - org) + (xmt - dst)).total_seconds() / 2)
   # print '\tdelay:      %r'       %(((dst - org) - (xmt - rec)).total_seconds() / 2)
   # #print '%s %s %s' % (s.recv_time_frac, s.recv_time_frac / 2.**32, int(s.recv_time_frac * 1e9) >> 32)

    return xmt

def run(options, args):
    prev = datetime.datetime.fromtimestamp(0)
    while True:
        now = get_sample(options, args)
        if now == None:
            time.sleep(10)
            continue
        if now.minute != prev.minute:
            prev = now
            demo(now)
        time.sleep(10)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s","--server", dest="server", help="NTP server to contact", default="0.fedora.pool.ntp.org")
    (options,args) = parser.parse_args()

    run(options, args)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import pigpio
import sys
import argparse
import os

TXGPIO = 4  # 433.42 MHz emitter on GPIO 4
frame = bytearray(7)

def button(x):
    return {
        'open': 2,
        'close': 4,
        'stop': 1,
        'prog': 8
    }.get(x, 1)    # 1 is default if x not found

def send_command(blindId, button):  # Sending a frame
   checksum = 0
   data_path = os.path.dirname(os.path.abspath(__file__)) + "/blinds/"

   with open(data_path + blindId + ".txt", 'r') as file:  # the files are un a subfolder "blinds"
      data = file.readlines()

   teleco = int(data[0], 16)
   code = int(data[1])
   data[1] = str(code + 1)

   print hex(teleco)
   print code

   with open(data_path + blindId + ".txt", 'w') as file:
      file.writelines(data)

   pi = pigpio.pi()  # connect to Pi

   if not pi.connected:
      exit()

   pi.wave_add_new()
   pi.set_mode(TXGPIO, pigpio.OUTPUT)

   print "Remote  :      " + "0x%0.2X" % teleco
   print "Button  :      " + "0x%0.2X" % button
   print "Rolling code : " + str(code)
   print ""

   frame[0] = 0xA7;       # Encryption key. Doesn't matter much
   # Which button did  you press? The 4 LSB will be the checksum
   frame[1] = button << 4
   frame[2] = code >> 8               # Rolling code (big endian)
   frame[3] = (code & 0xFF)           # Rolling code
   frame[4] = teleco >> 16            # Remote address
   frame[5] = ((teleco >> 8) & 0xFF)  # Remote address
   frame[6] = (teleco & 0xFF)         # Remote address

   print "Frame  :    ",
   for octet in frame:
      print "0x%0.2X" % octet,
   print ""

   for i in range(0, 7):
      checksum = checksum ^ frame[i] ^ (frame[i] >> 4)

   checksum &= 0b1111;  # We keep the last 4 bits only

   frame[1] |= checksum;

   print "With cks  : ",
   for octet in frame:
      print "0x%0.2X" % octet,
   print ""

   for i in range(1, 7):
      frame[i] ^= frame[i - 1];

   print "Obfuscated :",
   for octet in frame:
      print "0x%0.2X" % octet,
   print ""

#This is where all the awesomeness is happening. You're telling the daemon what you wana send
   wf = []
   wf.append(pigpio.pulse(1 << TXGPIO, 0, 9415))
   wf.append(pigpio.pulse(0, 1 << TXGPIO, 89565))
   for i in range(2):
      wf.append(pigpio.pulse(1 << TXGPIO, 0, 2560))
      wf.append(pigpio.pulse(0, 1 << TXGPIO, 2560))
   wf.append(pigpio.pulse(1 << TXGPIO, 0, 4550))
   wf.append(pigpio.pulse(0, 1 << TXGPIO,  640))

   for i in range(0, 56):
      if ((frame[i / 8] >> (7 - (i % 8))) & 1):
         wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))
         wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
      else:
         wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
         wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

   wf.append(pigpio.pulse(0, 1 << TXGPIO, 30415))

   #2
   for i in range(7):
      wf.append(pigpio.pulse(1 << TXGPIO, 0, 2560))
      wf.append(pigpio.pulse(0, 1 << TXGPIO, 2560))
   wf.append(pigpio.pulse(1 << TXGPIO, 0, 4550))
   wf.append(pigpio.pulse(0, 1 << TXGPIO,  640))

   for i in range(0, 56):
      if ((frame[i / 8] >> (7 - (i % 8))) & 1):
         wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))
         wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
      else:
         wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
         wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

   wf.append(pigpio.pulse(0, 1 << TXGPIO, 30415))

   #2
   for i in range(7):
      wf.append(pigpio.pulse(1 << TXGPIO, 0, 2560))
      wf.append(pigpio.pulse(0, 1 << TXGPIO, 2560))
   wf.append(pigpio.pulse(1 << TXGPIO, 0, 4550))
   wf.append(pigpio.pulse(0, 1 << TXGPIO,  640))

   for i in range(0, 56):
      if ((frame[i / 8] >> (7 - (i % 8))) & 1):
         wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))
         wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
      else:
         wf.append(pigpio.pulse(1 << TXGPIO, 0, 640))
         wf.append(pigpio.pulse(0, 1 << TXGPIO, 640))

   wf.append(pigpio.pulse(0, 1 << TXGPIO, 30415))

   pi.wave_add_generic(wf)
   wid = pi.wave_create()
   pi.wave_send_once(wid)
   while pi.wave_tx_busy():
      pass
   pi.wave_delete(wid)

   pi.stop()

def parse_args():
    parser = argparse.ArgumentParser(
        description='SomFy Blinds controller')
    parser.add_argument('--blind', type=str, required=True, default='0',
                        help='Blind ID to control')
    parser.add_argument('--action', type=str, required=True, default='stop',
                        choices=['open', 'close', 'stop', 'prog'],
                        help='Blind button (open, close, stop, prog)')
    return parser.parse_args()

def main(blind, action):
    """Main entry point for the script."""
    print "Blind %s %s" % (blind, action)
    try:
        send_command(blind, button(action))
    except:
        print "Error on Blind %s" % blind
        print traceback.format_exc()
        return -1
    return 0

if __name__ == '__main__':
    args = parse_args()
    sys.exit(main(blind=args.blind, action=args.action))

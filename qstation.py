import math
import struct
import urllib.request
import wave
from collections import deque
from time import sleep

import numpy as np
import pyaudio

import audioop
from qstation_wrapper import *

delay = .01

def list_lights():
   # get_lights()
   pass

def set_color(color, sn):
    """ Sets the color of an LED to the given color tuple. """
    # Note: Sets brightness to max, along with other light_ctrl options to 
    # defaults, as light_ctrl requires setting all params at once and there is
    # no bulb state to read for preserving previous settings.
    light_ctrl(color, 9, 255, 1, 0, [sn])
    sleep(delay)

def set_brightness(brightness, sn, color):
    """ Sets the brightness of an LED. Brightness should be an integer from 0 to 100 """
    # Note: See note for set_color above. I've opted to set the bulb to the color of choice mode
    # while we don't have a means for preserving the bulb's color
    if brightness > 255:
        brightness = 255
    if brightness < 0:
        brightness = 0
    light_ctrl(color, 9, brightness, 1, 0, [sn])
    sleep(delay)

def set_white_mode(sn):
    light_ctrl((0,0,0), 8, 100, 1, 0, [sn])
    sleep(delay)

def set_color_mode(sn):
    light_ctrl((0,0,0), 9, 100, 1, 0, [sn])
    sleep(delay)

def turn_on(sn):
    light_ctrl((0,0,0), 8, 100, "1", 0, [sn])
    sleep(delay)

def turn_off(sn):
    light_ctrl((0, 0, 0), 8, 100, "0", 0, [sn])
    sleep(delay)

def read_page(word,url):
    count = 0
    word = word.lower()
    while True:
        if count > 5:
            return False
        html = urllib.request.urlopen(url).read()
        html = html.lower()
        if word in str(html):
            return True
        sleep(1)
        count = count + 1

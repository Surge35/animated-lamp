import tkinter as tk
import numpy as np
import sounddevice as sd
import librosa
import time
from PIL import Image,ImageTk

import keyboard
from random import randint
from time import sleep
import os

from qstation import *
from qstation_wrapper import *

connect('172.16.0.1')

# ============================================================
# LED LIGHT SERIAL NUMBERS
# ============================================================
light0_sn = 'MD1AC44200001978'
light1_sn = 'MD1AC44200002461'
light2_sn = 'MD1AC44200002097'
light3_sn = 'MD2AC44400002185'
light4_sn = 'MD2AC52400001760'
light5_sn = 'MD1AC44200002052'

# ============================================================
# 1. LOAD AUDIO FILE
# ============================================================
AUDIO_FILE = "wetrynastayalivestayinaliverevisedFINALMAYBE.mp3"
audio, rate = librosa.load(AUDIO_FILE, sr=None, mono=True)

#Librosa actively puts chunks of mp3 into an array. We replaced pyaudio w Librosa bcuz
#pyaudio does not have this functionality, in addition to Librosa's capability to define 
#a sampling rate. Songs that are a few minutes in length typically have several million
#chunks to go through

print(len(audio))
print(rate)

#chunk_size = 128; Below is a chunk counter variable (which chunk we are on until we get to the last)    

audio_pos = 0

# ============================================================
# 2. EQ FREQUENCY BANDS
# ============================================================

#Below, we define the ranges of sound frequencies, from low to high, as tuples. 

sub_range = (0, 60)
bass_range = (60, 250)
lowmid_range = (250, 500)
mid_range = (500, 4000)
uppermid_range = (4000, 8000)
high_range = (8000, 20000)

#Get energy function: 
def get_energy(data, rate):
    """
    Perform FFT on audio chunk, divide into 6 frequency bands,
    return normalized band energies (0–1). We take the totals and 
    
    """
    fft = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), 1 / rate)
    #print(freqs)
    sub = np.sum(fft[(freqs >= sub_range[0]) & (freqs < sub_range[1])])
    bass = np.sum(fft[(freqs >= bass_range[0]) & (freqs < bass_range[1])])
    lowmids = np.sum(fft[(freqs >= lowmid_range[0]) & (freqs < lowmid_range[1])])
    mids = np.sum(fft[(freqs >= mid_range[0]) & (freqs < mid_range[1])])
    uppermids = np.sum(fft[(freqs >= uppermid_range[0]) & (freqs < uppermid_range[1])])
    highs = np.sum(fft[(freqs >= high_range[0]) & (freqs < high_range[1])])

    total = sub + bass + lowmids + mids + uppermids + highs + 1e-6

    print(
        sub / total,
        bass / total,
        lowmids / total,
        mids / total,
        uppermids / total,
        highs / total
    )

    return (
        sub / total,
        bass / total,
        lowmids / total,
        mids / total,
        uppermids / total,
        highs / total
    )



# ============================================================
# 3. TKINTER GUI SETUP
# ============================================================
WIDTH = 400
HEIGHT = 300
BAR_WIDTH = WIDTH // 6

root = tk.Tk()
root.title("6-Bar EQ Visualizer")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

img= ImageTk.PhotoImage(Image.open("nyancat.png"))
id = canvas.create_image(175,150,image=img,anchor='center') 
# ============================================================
# 4. COLOR DEFINITIONS
# ============================================================
color_tuples = [
    (255, 52, 52),     # Sub 
    (255, 122, 52),   # Bass 
    (255, 168, 52),     # Lowmid 
    (255, 255, 52),   # Mid 
    (186, 255, 52),     # Uppermid 
    (52, 255, 125)    # High 
]


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


bars = []
for i in range(6):
    bar = canvas.create_rectangle(
        i * BAR_WIDTH, HEIGHT,
        (i + 1) * BAR_WIDTH, HEIGHT,
        fill=rgb_to_hex(color_tuples[i]),
        outline=""
    )
    bars.append(bar)

# ============================================================
# 5. INTENSITY VARIABLES
# ============================================================
sub_intensity = bass_intensity = lowmid_intensity = 0
mid_intensity = uppermid_intensity = high_intensity = 0

# ============================================================
# 6. AUDIO CALLBACK
# ============================================================
def audio_callback(outdata, frames, time_info, status):
    global audio_pos
    global sub_intensity, bass_intensity, lowmid_intensity
    global mid_intensity, uppermid_intensity, high_intensity

    chunk = audio[audio_pos:audio_pos + frames]

    if len(chunk) < frames:
        outdata[:len(chunk)] = chunk.reshape(-1, 1)
        outdata[len(chunk):] = 0
        raise sd.CallbackStop()
    else:
        outdata[:] = chunk.reshape(-1, 1)

    (
        sub_intensity,
        bass_intensity,
        lowmid_intensity,
        mid_intensity,
        uppermid_intensity,
        high_intensity
    ) = get_energy(chunk, rate)

    audio_pos += frames


# ============================================================
# 7. GUI UPDATE LOOP
# ============================================================
def update_gui():
    global sub_intensity, bass_intensity, lowmid_intensity
    global mid_intensity, uppermid_intensity, high_intensity

    intensities = [
        sub_intensity,
        bass_intensity,
        lowmid_intensity,
        mid_intensity,
        uppermid_intensity,
        high_intensity
    ]

    # Update visual bars
    for i, value in enumerate(intensities):
        bar_height = value * HEIGHT
        canvas.coords(
            bars[i],
            i * BAR_WIDTH,
            HEIGHT - bar_height,
            (i + 1) * BAR_WIDTH,
            HEIGHT
        )

    # Corrected: use each band's real color
    sub_light_color = tuple(int(c * sub_intensity) for c in color_tuples[0])
    bass_light_color = tuple(int(c * bass_intensity) for c in color_tuples[1])
    lowmid_light_color = tuple(int(c * lowmid_intensity) for c in color_tuples[2])
    mid_light_color = tuple(int(c * mid_intensity) for c in color_tuples[3])
    uppermid_light_color = tuple(int(c * uppermid_intensity) for c in color_tuples[4])
    high_light_color = tuple(int(c * high_intensity) for c in color_tuples[5])

    '''print(
        "Sub:", sub_light_color,
        "Bass:", bass_light_color,
        "Lowmid:", lowmid_light_color,
        "Mid:", mid_light_color,
        "Uppermid:", uppermid_light_color,
        "High:", high_light_color
    )'''

    # Send to lights
    
    set_color(sub_light_color, light0_sn)
    #sleep(0.01)
    set_color(bass_light_color, light1_sn)
    #sleep(0.01)
    set_color(lowmid_light_color, light2_sn)
    #sleep(0.01)
    set_color(mid_light_color, light3_sn)
    #sleep(0.01)
    set_color(uppermid_light_color, light4_sn)
    #sleep(0.01)
    set_color(high_light_color, light5_sn)
    #sleep(0.01)
    '''
    set_color(bass_light_color, light0_sn)
    sleep(0.01)
    set_color(bass_light_color, light1_sn)
    sleep(0.01)
    set_color(bass_light_color, light2_sn)
    sleep(0.01)
    set_color(bass_light_color, light3_sn)
    sleep(0.01)
    set_color(bass_light_color, light4_sn)
    sleep(0.01)
    set_color(bass_light_color, light5_sn)
    sleep(0.01)
    '''
    root.after(30, update_gui)


# ============================================================
# 8. START STREAM + GUI
# ============================================================
stream = sd.OutputStream(
    samplerate=rate,
    channels=1,
    callback=audio_callback
)

stream.start()
update_gui()
root.mainloop()

if not root.running:
    set_color((0,0,0), light0_sn)
    set_color((0,0,0), light1_sn)
    set_color((0,0,0), light2_sn)
    set_color((0,0,0), light3_sn)
    set_color((0,0,0), light4_sn)
    set_color((0,0,0), light5_sn)

'''
WHAT IS HAPPENING HERE?

My name is Basil, and today I will be presenting my live equalizer-synced light show. 
In this project, used a 6-band equalizer, which separates my song choice for this project
into 6 different frequencies on screen, as well as on the lights. 
I chose [this song] because it is very dynamic and varied in its frequency ranges, so most 
if not all the lights will get to showcase high volume ranges.  

* Connect to the QStation with the given IP, and assign lights with serial numbers to 
  corresponding light values with frequencies from low to high (left to right respectively).
  

1. Load audio file using the librosa package

    - This is specifically to allow mp3 files to be read, since librosa is a much more 
    advanced library than pyaudio for audio analysis, while pyaudio is for simple tasks
    such as sole audio I/O. 
    - There are two variables assigned to the load function from librosa, where audio is 
    a large one-dimensional array (15 million elements or audio chunks), and rate is the 
    sampling rate of the music. Pyaudio will not be able to store this information as an array. 
    
2. Stream audio in small chunks

    - 

3. For each chunk, run FFT

    -

4. Split FFT magnitudes into frequency bands: 

    - 

5. Normalize band energy: 

6. Send intensity values to GUI + lights
'''

'''
1. Load audio file using librosa package
'''
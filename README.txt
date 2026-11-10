Audio-Reactive Light Show Using Python & FFT

A Python-based audio-reactive lighting system that uses Fast Fourier Transform (FFT) to analyze music frequencies and generate dynamic lighting effects in response to sound.

Overview

This project explores the relationship between audio signal processing and visual effects by translating musical frequencies into real-time lighting responses. Using Python and FFT, the system analyzes incoming audio signals, separates frequency components, and maps them to different lighting behaviors.

Tools & Technologies
Python
NumPy
SciPy
FFT (Fast Fourier Transform)
QStation, LED lightbulbs (compatible with QStation)

Methodology
Audio Input: Capture or load an audio signal for analysis.
Frequency Analysis: Apply FFT to transform the audio signal from the time domain into the frequency domain.
Frequency Mapping: Separate frequency ranges (bass, midrange, and treble) to visualize different characteristics of the music.
Lighting Control: Map frequency amplitudes to lighting parameters such as color, brightness, and intensity.
Visual Output: Generate dynamic lighting effects that respond to changes in the audio.
Frequency Mapping
Frequency Range	Audio Component	Lighting Response
Low	Bass:	bulbs 1-2
Mid	Midrange: bulbs 3-4	
High	Treble: bulbs 5-6	
Results

Include images, videos, or GIFs demonstrating how the lighting responds to different musical frequencies.

!Light Show Preview

Project Structure
text
audio-reactive-lightshow/
├── README.md
├── lightshow-6band.py
├── qstation.py
├── qstation_wrapper.py
├── videos/
│   └── .mp4
├── requirements.txt
└── wetrynastayalivestayinaliverevisedFINALMAYBE.mp3



Running the Project

Install dependencies:
##
bash
pip install -r requirements.txt


Run the program:

bash
python main.py

Future Improvements
Improve real-time frequency detection.
Experiment with more complex frequency-to-color mappings.
Incorporate additional lighting patterns and transitions.
Author

B!aze

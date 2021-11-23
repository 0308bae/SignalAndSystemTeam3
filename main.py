import copy
import os
import time
import wave

import numpy as np
import scipy.fftpack
import soundfile

# General settings that can be changed by the user
SAMPLE_RATE = 48000
WINDOW = 28137
NUM_HPS = 5  # max number of harmonic product spectrum
CONCERT_PITCH = 440  # defining a1
ALL_NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
ALL_NOTES_KOR = ["라", "라#", "시", "도", "도#", "레", "레#", "미", "파", "파#", "솔", "솔#"]

HANN_WINDOW = np.hanning(SAMPLE_RATE)


def get_duration(audio_path):
  audio = wave.open(audio_path)
  frames = audio.getnframes()
  rate = audio.getframerate()
  duration = frames / float(rate)
  return duration


def find_pitch(in_data):
  hann_samples = in_data * HANN_WINDOW
  magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[:len(hann_samples) // 2])

  mag_spec_ipol = np.interp(np.arange(0, len(magnitude_spec), 1 / NUM_HPS), np.arange(0, len(magnitude_spec)), magnitude_spec)
  mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)  # normalize it

  hps_spec = copy.deepcopy(mag_spec_ipol)

  for i in range(NUM_HPS):
    tmp_hps_spec = np.multiply(hps_spec[:int(np.ceil(len(mag_spec_ipol) / (i + 1)))], mag_spec_ipol[::(i + 1)])
    if not any(tmp_hps_spec):
      break
    hps_spec = tmp_hps_spec

  max_ind = np.argmax(hps_spec)
  max_freq = max_ind * (SAMPLE_RATE / SAMPLE_RATE) / NUM_HPS

  return max_freq



data, fs = soundfile.read('plane.wav')
data = data[:, 0]
length = len(data)
length_iter = length // WINDOW

ArrayNote = []
ArrayNote_KOR = []
ArrayNote_HZ = []

tmp_data = np.empty(shape=SAMPLE_RATE)
for j in range(length_iter):
  for k in range(SAMPLE_RATE):
    if ((WINDOW * j + k) >= length):
      break
    tmp_data[k] = data[WINDOW * j + k]
  pitch = find_pitch(tmp_data)
  if(pitch == 0.0):
    continue
  i = int(np.round(np.log2(pitch / CONCERT_PITCH) * 12))
  closest_note = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12)
  closest_note_KOR = ALL_NOTES_KOR[i % 12] + str(4 + (i + 9) // 12)
  ArrayNote.append(closest_note)
  ArrayNote_KOR.append(closest_note_KOR)
  ArrayNote_HZ.append(pitch)
  print('{:<6} : '.format(j) + '{}Hz'.format(pitch), closest_note_KOR)

# count = 0 #todo
# for j in range(len(ArrayNote)-1):
#   j += count
#   if(j==len(ArrayNote)):
#     break
#   count = 0
#   while(ArrayNote[j] == ArrayNote[j+1]):
#     count += 1
#     j += 1
#   print(ArrayNote[j], count)

# for j in ArrayNote:
#   print(j)
#   os.system("start {}.wav".format(j))
#   time.sleep(0.25)
from kivy.app import App
from kivy.uix.button import Button
class TutorialApp(App):
    def build(self):
        return Button(text="Hello World!")
TutorialApp().run()
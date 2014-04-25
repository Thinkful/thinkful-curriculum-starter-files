from __future__ import division

import math

import numpy
import librosa
import scipy.spatial.distance
import scipy.signal

CHORDS = numpy.array([
    [1,0,0,0,1,0,0,1,0,0,0,0],
    [1,0,0,1,0,0,0,1,0,0,0,0],
    [0,1,0,0,0,1,0,0,1,0,0,0],
    [0,1,0,0,1,0,0,0,1,0,0,0],
    [0,0,1,0,0,0,1,0,0,1,0,0],
    [0,0,1,0,0,1,0,0,0,1,0,0],
    [0,0,0,1,0,0,0,1,0,0,1,0],
    [0,0,0,1,0,0,1,0,0,0,1,0],
    [0,0,0,0,1,0,0,0,1,0,0,1],
    [0,0,0,0,1,0,0,1,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0],
    [1,0,0,0,0,1,0,0,1,0,0,0],
    [0,1,0,0,0,0,1,0,0,0,1,0],
    [0,1,0,0,0,0,1,0,0,1,0,0],
    [0,0,1,0,0,0,0,1,0,0,0,1],
    [0,0,1,0,0,0,0,1,0,0,1,0],
    [1,0,0,1,0,0,0,0,1,0,0,0],
    [0,0,0,1,0,0,0,0,1,0,0,1],
    [0,1,0,0,1,0,0,0,0,1,0,0],
    [1,0,0,0,1,0,0,0,0,1,0,0],
    [0,0,1,0,0,1,0,0,0,0,1,0],
    [0,1,0,0,0,1,0,0,0,0,1,0],
    [0,0,0,1,0,0,1,0,0,0,0,1],
    [0,0,1,0,0,0,1,0,0,0,0,1]
])

CHORD_NAMES = ["C", "Cm",
               "C#", "C#m",
               "D", "Dm",
               "D#", "D#m",
               "E", "Em",
               "F", "Fm",
               "F#", "F#m",
               "G", "Gm",
               "G#", "G#m",
               "A", "Am",
               "A#", "A#m",
               "B", "Bm"]

def calculate_chords(filename):
    samples, sampleRate = librosa.load(filename)
    length = len(samples) / sampleRate
    stft = numpy.abs(librosa.stft(samples, n_fft=8192, hop_length=1024))
    length = int(stft.shape[-1] / 8)
    hps = (stft[:, :length] *
            scipy.signal.decimate(stft, 2, axis=-1)[:, :length] *
            scipy.signal.decimate(stft, 4, axis=-1)[:, :length] *
            scipy.signal.decimate(stft, 8, axis=-1)[:, :length])
    chromagram = librosa.feature.chromagram(S=hps)
    chromagram = numpy.transpose(chromagram)

    distances = scipy.spatial.distance.cdist(chromagram, CHORDS, "cosine")
    chords = distances.argmin(axis=1)
    chords = scipy.signal.medfilt(chords, 11)


    output = []
    current = None
    lastTime = -1
    for index, chord in enumerate(chords):
        if chord == current:
            continue

        time = index / len(chords)

        item = {}
        item["chord"] = CHORD_NAMES[int(round(chord))]
        item["time"] = time
        output.append(item)
        current = chord
    return output

if __name__ == "__main__":
    calculate_chords('/home/joe/Music/Ooberman/Carried Away/01 Carried Away 06b.mp3')


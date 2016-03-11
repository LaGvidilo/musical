#!/usr/bin/env python3

import collections
import sys

from PIL import Image, ImageDraw

import pysong
from cellular import cellular


def make_song(ca_params, notes, n_notes=60, sample_size=(2,2), sample_spacing=(0,0), 
        threshold=None, unit_time=0.3, decimates=0, skip=50, note_lens=4):
    rh, rw = [sum(i) for i in (zip(sample_size, sample_spacing))]

    total_width, total_height = rw*len(notes), skip+rh*n_notes
    ca = cellular.TotalisticCellularAutomaton(total_width+100, **ca_params)

    for _ in range(decimates):
        ca.decimate()

    print(ca)

    ca.run(total_height)

    image = ca.draw()
    image.show()

    song = pysong.Song()

    region_sums = []
    for t in range(n_notes):
        sr = skip + t*rh
        for note_i in range(len(notes)):
            sc = note_i * rw
            region_sum = 0

            for i in range(sample_size[0]):
                for j in range(sample_size[1]):
                    region_sum += ca.history[sr+i][sc+j]
            region_sums.append(region_sum)

    region_sums.sort()
    max_sum = region_sums[-1]
    if threshold is None:
        threshold = region_sums[int(len(region_sums)*0.9)] 
        print(threshold)
    else:
        threshold = int(threshold * max_sum)


    song_img = Image.new('RGB', (total_width, total_height))
    draw = ImageDraw.Draw(song_img)
    draw.rectangle([(0, 0), (total_width, total_height)], fill='white')

    for t in range(n_notes):
        sr = skip + t*rh
        for note_i in range(len(notes)):
            sc = note_i * rw
            region_sum = 0

            for i in range(sample_size[0]):
                for j in range(sample_size[1]):
                    region_sum += ca.history[sr+i][sc+j]

            if region_sum > threshold:
                activation = float(region_sum - threshold) / float(max_sum - threshold)
                note_len = unit_time * 2**int(activation * note_lens) 
                note = notes[note_i]
                song.add_note(note, 0.5, unit_time*t/2.0, note_len)

                color = (255-int(activation*200), 0, 0)
                draw.rectangle([sc, sr, sc+rw, sr+rh], fill=color)

    song_img.show()

    return ca, song
    

def main():
    colors = ['black', 'blue', 'yellow', 'orange', 'red']

    rules = None
    if len(sys.argv) > 1:
        rules = [int(r) for r in sys.argv[1].split('-')]
        decimates = 0

    scale = [3, 5, 7, 10, 12]
    notes = []
    for octave in range(-3, 3):
        notes += [note+octave*12 for note in scale]

    ca_params = dict(
        radius=1,
        rules=rules,
        states=5,
        colors=None,
    )

    if rules is None:
        decimates = 6

    ca, song = make_song(ca_params, notes,
        decimates=decimates,
        sample_size=(5,5),
        sample_spacing=(0,0), 
        threshold=None
    )

    song.write_wav('{}.wav'.format(ca))


if __name__ == '__main__':
    main()


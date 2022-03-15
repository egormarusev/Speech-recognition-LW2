from tkinter import *
from tkinter import filedialog as fd
from tkinter import scrolledtext
import tkinter as tk

from vosk import Model, KaldiRecognizer
import wave
import shlex
import pipes
import json
from subprocess import check_call


def transcription():
    inputfile = fd.askopenfilename()
    wavfile = inputfile.split(".", 1)[0] + '.wav'

    command = 'ffmpeg -y -i {} -ar 48000 -ac 1 {}'.format(pipes.quote(inputfile), pipes.quote(wavfile))
    check_call(shlex.split(command))

    wf = wave.open(wavfile, "rb")
    rcgn_fr = wf.getframerate() * wf.getnchannels()
    rec = KaldiRecognizer(model, rcgn_fr)
    result = ''
    last_n = False
    # read_block_size = 4000
    read_block_size = wf.getnframes()
    while True:  # Можно читать файл блоками, тогда можно выводить распознанный текст частями, но слова на границе блоков могут быть распознаны некорректно
        data = wf.readframes(read_block_size)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())

            if res['text'] != '':
                result += f" {res['text']}"
                if read_block_size < 200000:
                    print(res['text'] + " \n")

                last_n = False
            elif not last_n:
                result += '\n'
                last_n = True

    res = json.loads(rec.FinalResult())
    result += f" {res['text']}"

    text.delete('1.0', END)
    text.insert(1.0, result)


if __name__ == "__main__":
    model = Model("vosk-model-ru-0.22")
    root = Tk()
    text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30, font=("Times New Roman", 15))
    text.pack(expand=YES, fill=BOTH)
    b1 = Button(text="Транскрибация", command=transcription, width=20)
    b1.pack()

    root.mainloop()

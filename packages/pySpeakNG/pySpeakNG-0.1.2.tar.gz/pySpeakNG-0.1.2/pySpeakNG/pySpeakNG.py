# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2022 David E. Lambert
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Main package module.

Functions:
    speak(text, language='en-us', voice='f1', pitch=50, speed=125,
          gap=10, amplitude=50, fp=None)

Attributes:
    VOICES (list): eSpeak-NG voice models.
    LANGUAGES (dict): eSPeak-NG language codes and descriptions.
"""

import json
import subprocess
import shlex
from pathlib import Path

HERE = Path(__file__).parent.resolve()

with open(HERE/'voices.json', 'r') as f:
    VOICES = json.load(f)

with open(HERE/'langs.json', 'r') as f:
    LANGUAGES = json.load(f)


def speak(text: str, language='en-us', voice='f1', pitch=50,
          speed=125, gap=10, amplitude=50, fp=None) -> None:
    """Play or save text-to-speech using off-line speech synthesis.

    :param text:  A string for eSpeak-NG to synthesize.
    :type text: str
    :param language: Language code for synth voice, defaults to 'en-us'.
        See LANGUAGES for options.
    :type language: str, optional
    :param voice: Synth voice model, defaults to 'f1'.
    :type voice: str, optional
    :param pitch: Pitch adjustment, 0-99. The default of 50 is the
        default pitch for the selected voice.
    :type pitch: int, optional
    :param speed: 25-250 words per minute, defaults to 125.
    :type speed: int, optional
    :param gap: Pause between words, in units of 10ms at the default
        speed. Defaults to 10 as 175wpm.
    :type gap: int, optional
    :param amplitude: 0-100, defaults to 50. Don't blow a speaker.
    :type amplitude: int, optional
    :param fp: Location to save .wav file output of the synthesized
        speech, defaults to None. When present, audio is not played.
    :type fp: path-like, optional
    """
    if language not in list(LANGUAGES):
        print("ERROR: 'language' must be a valid eSpeak-NG language key.")
        print("See pySpeakNG.LANGUAGES for valid keys and descriptions.")

    if voice not in VOICES:
        print("ERROR: 'voice' must be a valid eSpeak-NG voice name.")
        print("See pySpeakNG.VOICES for options.")

    if pitch < 0:
        pitch = 0
    elif pitch > 99:
        pitch = 99

    if speed < 25:
        speed = 25
    elif speed > 250:
        speed = 250

    if gap < 0:
        gap = 10
    elif gap > 40:
        gap = 10

    if amplitude < 0:
        amplitude = 50
    elif amplitude > 100:
        amplitude = 50

    if fp:
        try:
            fp = str(Path(fp).absolute())
        except Exception as e:
            print(e)
            print("ERROR: 'fp' must be a valid path-like object or string.")
    else:
        fp = ' '

    command = shlex.split(
        "espeak-ng -v{}+{} -p {} -s {} -g {} -a {} {} \"{}\""
        .format(language, voice, pitch, speed, gap, amplitude, fp, text)
    )

    subprocess.run(command)

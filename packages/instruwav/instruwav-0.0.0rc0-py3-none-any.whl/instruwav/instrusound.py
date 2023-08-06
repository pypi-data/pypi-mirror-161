#!/usr/bin/env python
# -*-encoding:utf-8-*-

import argparse
import glob
import codecs
import os
import re
import shutil
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

import keyboardlayout as kl
import keyboardlayout.pygame as klp
import librosa
import numpy
import pygame
import soundfile

from instruwav.Core import __config__
from instruwav.Core import Exceptions

ANCHOR_INDICATOR = " anchor"
ANCHOR_NOTE_REGEX = re.compile(r"\s[abcdefg]$")
DESCRIPTION = 'Use your computer keyboard as a "piano"'
DESCRIPTOR_32BIT = "FLOAT"
BITS_32BIT = 32
AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED = 0
SOUND_FADE_MILLISECONDS = 50
CYAN = (0, 255, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

AUDIO_ASSET_PREFIX = "audio_files/"
KEYBOARD_ASSET_PREFIX = "keyboards/"
CURRENT_WORKING_DIR = Path(__file__).parent.absolute()
ALLOWED_EVENTS = {pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT}
BLACK_INDICES_C_SCALE = [1, 3, 6, 8, 10]
LETTER_KEYS_TO_INDEX = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}

class engine():
    def __init__(self):
        self._path="."
        self.instrumentlist=__config__.__STRC__["DEFAULT_INSTRUMENTS"]
        self.filename=self.instrumentlist[0]
        self.__conf={"filename":self.instrumentlist[0],"LIST":self.instrumentlist}
        
    
    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=DESCRIPTION)
        default_wav_file = __config__.PATH+"audio_files\\"+self.filename
        parser.add_argument(
            "--wav",
            "-w",
            metavar="FILE",
            type=str,
            default=default_wav_file,
            help="WAV file (default: {})".format(default_wav_file),
        )
        default_keyboard_file = "keyboards/qwerty_piano.txt"
        parser.add_argument(
            "--keyboard",
            "-k",
            metavar="FILE",
            type=str,
            default=default_keyboard_file,
            help="keyboard file (default: {})".format(default_keyboard_file),
        )
        parser.add_argument(
            "--clear-cache",
            "-c",
            default=False,
            action="store_true",
            help="deletes stored transposed audio files and recalculates them",
        )
        parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode")
    
        return parser
    
    
    def get_or_create_key_sounds(
        self,
        wav_path: str,
        sample_rate_hz: int,
        channels: int,
        tones: List[int],
        clear_cache: bool,
        keys: List[str],
    ) -> Generator[pygame.mixer.Sound, None, None]:
        sounds = []
        y, sr = librosa.load(wav_path, sr=sample_rate_hz, mono=channels == 1)
        file_name = os.path.splitext(os.path.basename(wav_path))[0]
        folder_containing_wav = Path(wav_path).parent.absolute()
        cache_folder_path = Path(folder_containing_wav, file_name)
        if clear_cache and cache_folder_path.exists():
            shutil.rmtree(cache_folder_path)
        if not cache_folder_path.exists():
            os.mkdir(cache_folder_path)
        for i, tone in enumerate(tones):
            cached_path = Path(cache_folder_path, "{}.wav".format(tone))
            if Path(cached_path).exists():
                sound, sr = librosa.load(cached_path, sr=sample_rate_hz, mono=channels == 1)
                if channels > 1:
                    # the shape must be [length, 2]
                    sound = numpy.transpose(sound)
            else:
                if channels == 1:
                    sound = librosa.effects.pitch_shift(y, sr, n_steps=tone)
                else:
                    new_channels = [
                        librosa.effects.pitch_shift(y[i], sr, n_steps=tone)
                        for i in range(channels)
                    ]
                    sound = numpy.ascontiguousarray(numpy.vstack(new_channels).T)
                soundfile.write(cached_path, sound, sample_rate_hz, DESCRIPTOR_32BIT)
            sounds.append(sound)
        sounds = map(pygame.sndarray.make_sound, sounds)
        return sounds
    
    
    
    def __get_black_key_indices(self,key_name: str) -> set:
        letter_key_index = LETTER_KEYS_TO_INDEX[key_name]
        black_key_indices = set()
        for ind in BLACK_INDICES_C_SCALE:
            new_index = ind - letter_key_index
            if new_index < 0:
                new_index += 12
            black_key_indices.add(new_index)
        return black_key_indices
    
    
    def get_keyboard_info(self,keyboard_file: str):
        with codecs.open(keyboard_file, encoding="utf-8") as k_file:
            lines = k_file.readlines()
        keys = []
        anchor_index = -1
        black_key_indices = set()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            match = ANCHOR_NOTE_REGEX.search(line)
            if match:
                anchor_index = i
                black_key_indices = engine.__get_black_key_indices(self,line[-1])
                key = kl.Key(line[: match.start(0)])
            elif line.endswith(ANCHOR_INDICATOR):
                anchor_index = i
                key = kl.Key(line[: -len(ANCHOR_INDICATOR)])
            else:
                key = kl.Key(line)
            keys.append(key)
        if anchor_index == -1:
            raise ValueError(
                "Invalid keyboard file, one key must have an anchor note or the "
                "word anchor written next to it.\n"
                "For example 'm c OR m anchor'.\n"
                "That tells the program that the wav file will be used for key m, "
                "and all other keys will be pitch shifted higher or lower from "
                "that anchor. If an anchor note is used then keys are colored black "
                "and white like a piano. If the word anchor is used, then the "
                "highest key is white, and keys get darker as they descend in pitch."
            )
        tones = [i - anchor_index for i in range(len(keys))]
        color_to_key = defaultdict(list)
        if black_key_indices:
            key_color = (120, 120, 120, 255)
            key_txt_color = (50, 50, 50, 255)
        else:
            key_color = (65, 65, 65, 255)
            key_txt_color = (0, 0, 0, 255)
        for index, key in enumerate(keys):
            if index == anchor_index:
                color_to_key[CYAN].append(key)
                continue
            if black_key_indices:
                used_index = (index - anchor_index) % 12
                if used_index in black_key_indices:
                    color_to_key[BLACK].append(key)
                    continue
                color_to_key[WHITE].append(key)
                continue
            # anchor mode, keys go up in half steps and we do not color black keys
            # instead we color from grey low to white high
            rgb_val = 255 - (len(keys) - 1 - index) * 3
            color = (rgb_val, rgb_val, rgb_val, 255)
            color_to_key[color].append(key)
    
        return keys, tones, color_to_key, key_color, key_txt_color
    
    
    def configure_pygame_audio_and_set_ui(
        self,
        framerate_hz: int,
        channels: int,
        keyboard_arg: str,
        color_to_key: Dict[str, List[kl.Key]],
        key_color: Tuple[int, int, int, int],
        key_txt_color: Tuple[int, int, int, int],
    ) -> Tuple[pygame.Surface, klp.KeyboardLayout]:
        # ui
        pygame.display.init()
        pygame.display.set_caption("pianoputer")
    
        # block events that we don't want, this must be after display.init
        pygame.event.set_blocked(None)
        pygame.event.set_allowed(list(ALLOWED_EVENTS))
    
        # fonts
        pygame.font.init()
    
        # audio
        pygame.mixer.init(
            framerate_hz,
            BITS_32BIT,
            channels,
            allowedchanges=AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
        )
    
        screen_width = 50
        screen_height = 50
        if "qwerty" in keyboard_arg:
            layout_name = kl.LayoutName.QWERTY
        elif "azerty" in keyboard_arg:
            layout_name = kl.LayoutName.AZERTY_LAPTOP
        else:
            ValueError("keyboard must have qwerty or azerty in its name")
        margin = 4
        key_size = 60
        overrides = {}
        for color_value, keys in color_to_key.items():
            override_color = color = pygame.Color(color_value)
            inverted_color = list(~override_color)
            other_val = 255
            if (
                abs(color_value[0] - inverted_color[0]) > abs(color_value[0] - other_val)
            ) or color_value == CYAN:
                override_txt_color = pygame.Color(inverted_color)
            else:
                # biases grey override keys to use white as txt_color
                override_txt_color = pygame.Color([other_val] * 3 + [255])
            override_key_info = kl.KeyInfo(
                margin=margin,
                color=override_color,
                txt_color=override_txt_color,
                txt_font=pygame.font.SysFont("Arial", key_size // 4),
                txt_padding=(key_size // 10, key_size // 10),
            )
            for key in keys:
                overrides[key.value] = override_key_info
    
        key_txt_color = pygame.Color(key_txt_color)
        keyboard_info = kl.KeyboardInfo(position=(0, 0), padding=2, color=key_txt_color)
        key_info = kl.KeyInfo(
            margin=margin,
            color=pygame.Color(key_color),
            txt_color=pygame.Color(key_txt_color),
            txt_font=pygame.font.SysFont("Arial", key_size // 4),
            txt_padding=(key_size // 6, key_size // 10),
        )
        letter_key_size = (key_size, key_size)  # width, height
        keyboard = klp.KeyboardLayout(
            layout_name, keyboard_info, letter_key_size, key_info, overrides
        )
        screen_width = keyboard.rect.width
        screen_height = keyboard.rect.height
    
        screen = pygame.display.set_mode((screen_width, screen_height))
        screen.fill(pygame.Color("black"))
        if keyboard:
            keyboard.draw(screen)
        pygame.display.update()
        return screen, keyboard
    
    
    def play_until_user_exits(
        self,
        keys: List[kl.Key],
        key_sounds: List[pygame.mixer.Sound],
        keyboard: klp.KeyboardLayout,
    ):
        sound_by_key = dict(zip(keys, key_sounds))
        playing = True
    
        while playing:
            for event in pygame.event.get():
    
                if event.type == pygame.QUIT:
                    playing = False
                    break
                elif event.key == pygame.K_ESCAPE:
                    playing = False
                    break
    
                key = keyboard.get_key(event)
                if key is None:
                    continue
                try:
                    sound = sound_by_key[key]
                except KeyError:
                    continue
    
                if event.type == pygame.KEYDOWN:
                    sound.stop()
                    sound.play(fade_ms=SOUND_FADE_MILLISECONDS)
                elif event.type == pygame.KEYUP:
                    sound.fadeout(SOUND_FADE_MILLISECONDS)
    
        pygame.quit()
        print("Goodbye")
    
    
    def get_audio_data(self,wav_path: str) -> Tuple:
        audio_data, framerate_hz = soundfile.read(wav_path)
        array_shape = audio_data.shape
        if len(array_shape) == 1:
            channels = 1
        else:
            channels = array_shape[1]
        return audio_data, framerate_hz, channels
    
    
    def process_args(self,parser: argparse.ArgumentParser, args: Optional[List]) -> Tuple:
        if args:
            args = parser.parse_args(args)
        else:
            args = parser.parse_args()
    
        # Enable warnings from scipy if requested
        if not args.verbose:
            warnings.simplefilter("ignore")
    
        wav_path = args.wav
        if wav_path.startswith(AUDIO_ASSET_PREFIX):
            wav_path = os.path.join(CURRENT_WORKING_DIR, wav_path)
    
        keyboard_path = args.keyboard
        if keyboard_path.startswith(KEYBOARD_ASSET_PREFIX):
            keyboard_path = os.path.join(CURRENT_WORKING_DIR, keyboard_path)
        return wav_path, keyboard_path, args.clear_cache
    
    
    def generate(self,args: Optional[List[str]] = None):
        parser = engine.get_parser(self)
        wav_path, keyboard_path, clear_cache = engine.process_args(self,parser, args)
        print(wav_path,self.filename)
        audio_data, framerate_hz, channels = engine.get_audio_data(self,wav_path)
        results = engine.get_keyboard_info(self,keyboard_path)
        keys, tones, color_to_key, key_color, key_txt_color = results
        key_sounds = engine.get_or_create_key_sounds(self,
            wav_path, framerate_hz, channels, tones, clear_cache, keys
        )
    def config(self,kwargs,value):
        if kwargs=="audio_file":
            if value in self.instrumentlist:
                self.filename=value
            else:
                raise Exceptions.ConfigError("Instrument does not exist")
        elif kwargs=="delete":
            shutil.rmtree(__config__.PATH+"audio_files\\"+value)
        elif kwargs=="add":
            tfiles=glob.glob(__config__.PATH+"audio_files\\*")
            files=[]
            for i in tfiles:
                __path,filename=os.path.split(i)
                files.append(filename)
            if value in files:
                self.instrumentlist.append(value)
                self.__conf={"filename":self.instrumentlist[0],"LIST":self.instrumentlist}                                
            else:
                raise FileNotFoundError("Please insert the .wav file in ./audio_files/ first.")
        elif kwargs=="show":
            print(self.instrumentlist,self.filename)
        else:
            raise Exceptions.UnknownArgError("Unknown args")

        
    
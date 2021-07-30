import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import textwrap
import math
import random
import xml.etree.ElementTree as ET
from typing import List
import csv


class Language:
    def __init__(self) -> None:
        pass

    def get_definition(self) -> List[str]:
        return ["nothing", "at", "all"]


class MySlideShow(tk.Toplevel):
    def __init__(self, lang: Language, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        # remove window decorations
        self.overrideredirect(True)

        # save reference to photo so that garbage collection
        # does not clear image variable in show_image()
        self.persistent_image = None

        # used to display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)

        self.lang = lang

    def startSlideShow(self, delay: int = 10):  # delay in seconds
        self.showImage()
        # its like a callback function after n seconds (cycle through pics)
        self.after(delay * 1000, self.startSlideShow)

    def showImage(self):
        character, pronunciation, translation = self.lang.get_definition()

        scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        image = Image.new("RGB", (scr_w, scr_h), color=(73, 109, 137))
        unicode_font = ImageFont.truetype("unifont-13.0.06.ttf", 65)
        d = ImageDraw.Draw(image)
        d.text(
            (50, scr_h - 440),
            character + "\n" + pronunciation + "\n" + "\n".join(textwrap.wrap(translation, width=70)),
            fill=(255, 255, 0),
            font=unicode_font,
        )

        # set window size after scaling the original image up/down to fit screen
        # removes the border on the image
        self.wm_geometry("{}x{}+{}+{}".format(scr_w, scr_h, 0, 0))

        # create new image
        self.persistent_image = ImageTk.PhotoImage(image)
        self.label.configure(image=self.persistent_image)


class Mandarin(Language):
    def __init__(self) -> None:
        super().__init__()
        self.source = open("mandarin.txt", "r", encoding="utf8")
        for _ in range(30):
            self.source.readline()
        self.definitions = self.source.readlines()
        self.tones = {
            # a
            98: "\u0101",
            99: "\u00E1",
            100: "\u01CE",
            101: "\u00E0",
            # e
            102: "\u0113",
            103: "\u00E9",
            104: "\u011B",
            105: "\u00E8",
            # i
            106: "\u012B",
            107: "\u00ED",
            108: "\u01D0",
            109: "\u00EC",
            # o
            112: "\u014D",
            113: "\u00F3",
            114: "\u01D2",
            115: "\u00F2",
            # u
            118: "\u016B",
            119: "\u00FA",
            120: "\u01D4",
            121: "\u00F9",
        }

    def parse_definition(self, definition: str) -> List[str]:
        split_definition: str = definition.split("/")
        character_pinyin: str = split_definition[0]
        pinyin_start: str = character_pinyin.find("[")
        double_character: str = character_pinyin[: pinyin_start - 1]
        pinyin: str = character_pinyin[pinyin_start:-1]
        english: str = split_definition[1]
        characters = double_character.split()
        character = characters[0]
        if characters[0] != characters[1]:
            if len(characters[0]) > 5:
                character = characters[0] + " /\n" + " " * math.floor(len(characters[0]) * 1.5) + characters[1]
            else:
                character = characters[0] + " /  " + characters[1]
        return character, self.parse_pinyin(pinyin), self.parse_pinyin(english)

    def parse_pinyin(self, pinyin: str) -> str:

        first_part: str = pinyin[: pinyin.find("[")]
        second_part: str = pinyin[pinyin.find("[") :]
        second_part: str = second_part.replace("[", "]").replace("]", "")

        pinyin_list: List[str] = second_part.split()
        output: str = first_part
        has_tone: bool = False
        for yin in pinyin_list:
            has_tone = False
            if "r5" in yin:
                output += yin.replace("r5", "er").replace("5", "")
                continue

            for num in ["1", "2", "3", "4"]:

                if not (num in yin):
                    continue
                has_tone = True
                for vowel in ["a", "e", "o", "ui", "u", "i"]:
                    if vowel in yin:
                        output += (
                            yin.replace("5", "")
                            .replace(num, "")
                            .replace(vowel, self.tones[ord(self.priority(vowel)) + int(num)])
                            + " "
                        )
                        break
            if not has_tone:
                output += yin + " "

        return output

    def priority(self, character: str) -> str:
        if character == "ui":
            return "i"
        return character

    def get_definition(self) -> List[str]:
        return self.parse_definition(random.choice(self.definitions))


class Spanish(Language):
    def __init__(self) -> None:
        super().__init__()
        self.source = ET.parse("es-en.xml")

    def get_definition(self) -> List[str]:
        root = self.source.getroot()
        letter_group = random.choice(root)
        word = random.choice(letter_group)
        return word[0].text, word[1].text, word[2].text


class Japanese(Language):
    def __init__(self) -> None:
        super().__init__()
        csv_file = open("heisig-kanjis.csv", "r", encoding="utf8")
        source = csv.DictReader(csv_file, delimiter=",")
        reader = source.reader
        self.definitions: List[str] = []
        self.definitions.extend(reader)

    def get_definition(self) -> List[str]:
        kanji, english, components, on_reading, kun_reading = random.choice(self.definitions)
        pronunciation = ''
        if kun_reading and on_reading:
            pronunciation = f'kun: {kun_reading}, \non: {on_reading}'
        elif kun_reading:
            pronunciation = f'kun: {kun_reading}'
        elif on_reading:
            pronunciation = f'on: {on_reading}'
            
        return kanji, pronunciation, english


class HiddenRoot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # hackish way, essentially makes root window
        # as small as possible but still "focused"
        # enabling us to use the binding on <esc>
        self.wm_geometry("0x0+0+0")

    def start_slideshow(self, lang: Language) -> None:
        self.window = MySlideShow(lang, self)
        self.window.startSlideShow()


slideShow = HiddenRoot()
slideShow.start_slideshow(Mandarin())
slideShow.bind("<Escape>", lambda e: slideShow.destroy())  # exit on esc
slideShow.mainloop()

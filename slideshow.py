import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from languages import Language, Cantonese, Mandarin, Japanese, Spanish
import textwrap
import sys
import os
import argparse

dirname = os.path.dirname(__file__)
font_dir = os.path.join(dirname, "fonts")

# ISO_639-3 language abbreviations https://en.wikipedia.org/wiki/ISO_639-3
LANGUAGES = {"cmn": Mandarin, "jpn": Japanese, "spa": Spanish, "yue": Cantonese}


class MySlideShow(tk.Tk):
    def __init__(self, lang: Language, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.is_fullscreen: bool = True
        self.overrideredirect(self.is_fullscreen)

        self.image_stack = []
        self.pointer = -1

        # used to display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)

        self.lang = lang

        self.bind("<Escape>", lambda: self.destroy())
        self.bind("f", lambda: self.toggle_fullscreen())
        self.bind("<Right>", lambda: self.nextImage())
        self.bind("<Left>", lambda: self.prevImage())
        self.bind("<space>", lambda: self.stopSlideshow() if self.is_active else self.startSlideShow())

        self.delay = 3

    def showImage(self):
        self.label.configure(image=self.image_stack[self.pointer])

    def prevImage(self):
        if hasattr(self, "next"):
            self.after_cancel(self.next)
        if self.pointer + len(self.image_stack) > 0:
            self.pointer -= 1

        self.showImage()
        self.next = self.after(self.delay * 1000, self.nextImage)

    def nextImage(self):
        if hasattr(self, "next"):
            self.after_cancel(self.next)
        if self.pointer == -1:
            character, pronunciation, english = self.lang.get_definition()
            self.generateImage(character, pronunciation, english)
        else:
            self.pointer += 1
        self.showImage()
        self.next = self.after(self.delay * 1000, self.nextImage)

    def startSlideShow(self):  # delay in seconds
        self.is_active = True
        self.nextImage()

    def stopSlideshow(self):
        if hasattr(self, "next"):
            self.after_cancel(self.next)
        self.is_active = False

    def generateImage(self, character, pronunciation, english):
        font_family = os.path.join(font_dir, "NotoSerifCJKjp-hinted", "NotoSerifCJKjp-ExtraLight.otf")
        scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        image = Image.new("RGB", (scr_w, scr_h), color=(73, 109, 137))
        unicode_font: ImageFont.FreeTypeFont = ImageFont.truetype(font_family, 250)
        d = ImageDraw.Draw(image)
        if unicode_font.getsize(character)[0] >= scr_w * 0.95:
            unicode_font: ImageFont.FreeTypeFont = ImageFont.truetype(font_family, 200)
        lang_w, lang_h = unicode_font.getsize(character)

        d.text(
            ((scr_w - lang_w) / 2, (scr_h - lang_h - unicode_font.getoffset(character)[1]) / 2),
            character.title(),
            fill=(255, 255, 0),
            font=unicode_font,
        )

        unicode_font = ImageFont.truetype(font_family, 50)
        english_w, english_h = unicode_font.getsize(english)
        d.text(
            ((scr_w - english_w) / 2, (scr_h + lang_h - unicode_font.getoffset(english)[1]) / 2),
            english.title(),
            fill=(255, 255, 0),
            font=unicode_font,
        )

        unicode_font = ImageFont.truetype(font_family, 40)
        pronunciation_w, pronunciation_h = unicode_font.getsize(pronunciation)
        d.text(
            ((scr_w - pronunciation_w) / 2, (scr_h - lang_h) / 2 - pronunciation_h),
            pronunciation.title(),
            fill=(255, 255, 0),
            font=unicode_font,
        )

        # set window size after scaling the original image up/down to fit screen
        # removes the border on the image
        self.wm_geometry("{}x{}+{}+{}".format(scr_w, scr_h, 0, 0))

        self.image_stack.append(ImageTk.PhotoImage(image))

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.overrideredirect(self.is_fullscreen)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="X to Eng slideshow")
    parser.add_argument("--lang", metavar="language", type=str, nargs="?", help="the language whatever")
    args = parser.parse_args()
    iso_id = args.lang

    if iso_id == None:
        print("cmn - Mandarin\njpn - Japanese\nspa - Spanish\nyue - Cantonese\n")
        iso_id = input("Enter language code:\n")

    iso_id = iso_id.lower()

    if iso_id in LANGUAGES.keys():
        window = MySlideShow(LANGUAGES[iso_id]())
        window.startSlideShow()
        window.mainloop()

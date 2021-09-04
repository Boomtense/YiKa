import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk
from PIL.ImageTk import BitmapImage
from languages import Language, LANGUAGES
from utils import title_case, get_path_to_resource
import textwrap
import argparse
import sys

ENGLISH_FONT = "NotoSerifCJKjp-ExtraLight.otf"


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

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("f", lambda e: self.toggle_fullscreen())
        self.bind("<Right>", lambda e: self.nextImage())
        self.bind("<Left>", lambda e: self.prevImage())
        self.bind("<space>", lambda e: self.stopSlideshow() if self.is_active else self.startSlideShow())

        self.delay = 10

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
            character, pronunciation, english, right_align = self.lang.get_definition()
            self.generateImage(character, pronunciation, english, right_align)
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

    def generateImage(self, character: str, pronunciation: str, english: str, right_align: bool = False):
        english_list = textwrap.wrap(english, width=70)
        font_family = self.lang.font
        scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        image = Image.new("RGB", (scr_w, scr_h), color=(73, 109, 137))
        from_size: int = 250
        unicode_font: ImageFont.FreeTypeFont = ImageFont.truetype(font_family, from_size)
        d = ImageDraw.Draw(image)
        while unicode_font.getsize(character)[0] >= scr_w * 0.95:
            from_size -= 5
            unicode_font: ImageFont.FreeTypeFont = ImageFont.truetype(font_family, from_size)
        lang_w, lang_h = unicode_font.getsize(character)

        d.text(
            ((scr_w - lang_w) / 2, (scr_h - lang_h - unicode_font.getoffset(character)[1]) / 2),
            title_case(character),
            fill=(255, 255, 0),
            font=unicode_font,
        )

        font_family = get_path_to_resource(foldername="fonts", filename=ENGLISH_FONT)
        english_offset = 0
        for e in english_list:
            unicode_font = ImageFont.truetype(font_family, 50)
            english_w, english_h = unicode_font.getsize(e)
            d.text(
                ((scr_w - english_w) / 2, (scr_h + english_offset + lang_h - unicode_font.getoffset(e)[1]) / 2),
                title_case(e),
                fill=(255, 255, 0),
                font=unicode_font,
            )
            english_offset += english_h + unicode_font.getoffset(e)[1] + 10

        unicode_font = ImageFont.truetype(font_family, 40)
        if right_align:
            word_offset = 0
            for word in pronunciation.split(","):
                pronunciation_list = textwrap.wrap(word, width=20)
                pronunciation_h = 0
                padding = 0
                for p in pronunciation_list:
                    padding = 0 if ":" in p else 105
                    pronunciation_w, pronunciation_h = unicode_font.getsize(p)
                    d.text(
                        ((scr_w + lang_w) / 2 + 50 + padding, (word_offset + scr_h - lang_h) / 2 + pronunciation_h),
                        title_case(p),
                        fill=(255, 255, 0),
                        font=unicode_font,
                    )
                    word_offset += pronunciation_h + unicode_font.getoffset(p)[1] + 20
                word_offset += 50
        else:
            pronunciation_w, pronunciation_h = unicode_font.getsize(pronunciation)
            d.text(
                ((scr_w - pronunciation_w) / 2, (scr_h - lang_h) / 2 - pronunciation_h),
                title_case(pronunciation),
                fill=(255, 255, 0),
                font=unicode_font,
            )

        # set window size after scaling the original image up/down to fit screen
        # removes the border on the image
        self.wm_geometry("{}x{}+{}+{}".format(scr_w, scr_h, 0, 0))
        self.image_stack.append(ImageTk.PhotoImage(image))
        self.image_stack = self.image_stack[-10:]

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.overrideredirect(self.is_fullscreen)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="X to Eng slideshow")
    parser.add_argument("--lang", metavar="language", type=str, nargs="?", help="the language whatever")
    args = parser.parse_args()
    iso_id = args.lang

    if iso_id == None:
        print(
            "\ncmn - Mandarin\njpn - Japanese\nrus - Russian\nspa - Spanish\nyue - Cantonese\narb - Arabic\nben - Bengali\nfra - French\ndeu - German\nhin - Hindi\nind - Indonesian\nkor - Korean\nmar - Marathi\npor - Portuguese\nswa - Swahili\ntam - Tamil\ntel - Telugu\ntur - Turkish\nurd - Urdu"
        )
        iso_id = input("\nEnter language code:\n")

    iso_id = iso_id.lower()

    if iso_id in LANGUAGES.keys():
        window = MySlideShow(LANGUAGES[iso_id]())
        window.startSlideShow()
        window.mainloop()

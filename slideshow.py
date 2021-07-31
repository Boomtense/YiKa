import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from languages import Language, Mandarin, Japanese, Spanish
import textwrap


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
        font_family = "fonts/NotoSerifCJKjp-hinted/NotoSerifCJKjp-ExtraLight.otf"
        character, pronunciation, english = self.lang.get_definition()

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

        # create new image
        self.persistent_image = ImageTk.PhotoImage(image)
        self.label.configure(image=self.persistent_image)


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

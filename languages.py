from typing import Iterable, List
from utils import get_path_to_resource
import random
import xml.etree.ElementTree as ET
import csv
import os


class Language:
    def __init__(self, name: str, font: str, needsBasic=False) -> None:
        self.name = name
        filename = "".join([name, ".txt"])
        self.definitions = []

        fonts = {
            "arabic": "NotoSansArabic-Light.ttf",
            "cjkjp": "NotoSerifCJKjp-ExtraLight.otf",
            "devanagari": "NotoSansDevanagari-Light.ttf",
            "bengali": "NotoSansBengali-Light.ttf",
            "tamil": "NotoSansTamil-Light.ttf",
            "telugu": "NotoSansTelugu-Regular.ttf",
            "eur": "NotoSans-Light.ttf",
        }
        self.font = get_path_to_resource(foldername="fonts", filename=fonts[font])

        if needsBasic:
            self.definitions.extend(self.get_resource(folder="Omegawiki", filename=filename, offset=5, delimiter="\t"))
            self.definitions.extend(self.get_resource(folder="Wikipedia", filename=filename, offset=5, delimiter="\t"))
        random.shuffle(self.definitions)
        self.definitions: Iterable[str] = iter(self.definitions)

    def get_definition(self):
        definition = next(self.definitions)
        return definition[0].replace(";", "/"), "", definition[1].replace(";", "/"), False

    def get_resource(self, folder, filename, offset, delimiter) -> List[str]:
        path = os.path.join(folder, filename)
        resource = get_path_to_resource(path)
        lines = []
        if os.path.isfile(resource):
            translations = open(resource, "r", encoding="utf8").readlines()
            lines = translations[offset:]

        return [x.split(delimiter) for x in lines]

    def to_string():
        return "name"


class Cantonese(Language):
    def __init__(self) -> None:
        super().__init__("cantonese", "cjkjp")

        with open(get_path_to_resource("cantonese.txt"), "r", encoding="utf8") as source:
            for _ in range(12):
                source.readline()
            self.definitions = source.readlines()

    def parse_definition(self, definition: str) -> List[str]:
        split_definition: str = definition.split("/")
        characters_pinyin_jyutping: str = split_definition[0]
        jyutping_start: str = characters_pinyin_jyutping.find("{")
        characters_pinyin: str = characters_pinyin_jyutping[: jyutping_start - 1]
        jyutping: str = characters_pinyin_jyutping[jyutping_start:-1]
        english: str = split_definition[1]
        character = characters_pinyin.split()[0]

        return character, self.parse_jyutping(jyutping), self.parse_jyutping(english), False

    def parse_jyutping(self, jyutping: str) -> str:
        return jyutping.replace("{", "}").replace("}", "")

    def get_definition(self):
        return self.parse_definition(random.choice(self.definitions))

    def to_string():
        return "Cantonese"


class Mandarin(Language):
    tones = {
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

    def __init__(self) -> None:
        super().__init__("mandarin", "cjkjp")
        with open(get_path_to_resource("mandarin.txt"), "r", encoding="utf8") as source:
            for _ in range(30):
                source.readline()
            self.definitions = source.readlines()

    def parse_definition(self, definition: str):
        split_definition: str = definition.split("/")
        character_pinyin: str = split_definition[0]
        pinyin_start: str = character_pinyin.find("[")
        double_character: str = character_pinyin[: pinyin_start - 1]
        pinyin: str = character_pinyin[pinyin_start:-1]
        english: str = split_definition[1]
        characters = double_character.split()
        character = characters[1]

        return character, self.parse_pinyin(pinyin), self.parse_pinyin(english), False

    def parse_pinyin(self, pinyin: str) -> str:

        first_part: str = pinyin[: pinyin.find("[")]
        second_part: str = pinyin[pinyin.find("[") :]
        second_part: str = second_part.replace("[", "]").replace("]", "")

        pinyin_list: List[str] = second_part.split()
        output: str = first_part
        has_tone: bool = False

        for yin in pinyin_list:
            has_tone = False

            for num in ["1", "2", "3", "4"]:
                if not (num in yin):
                    continue
                has_tone = True
                for vowel in ["a", "e", "o", "ui", "u", "i"]:
                    if vowel in yin:
                        output += (
                            yin.replace("5", "")
                            .replace("r5", "er")
                            .replace(num, "")
                            .replace(vowel, Mandarin.tones[ord(self.priority(vowel)) + int(num)])
                            + " "
                        )
                        break
            if not has_tone:
                output += yin.replace("r5", "er").replace("5", "") + " "

        return output

    def priority(self, character: str) -> str:
        if character == "ui":
            return "i"
        return character

    def get_definition(self):
        return self.parse_definition(random.choice(self.definitions))

    def to_string():
        return "Mandarin"


class Spanish(Language):
    def __init__(self) -> None:
        super().__init__("spanish", "cjkjp")
        self.source = ET.parse(get_path_to_resource("es-en.xml"))

    def get_definition(self):
        root = self.source.getroot()
        letter_group = random.choice(root)
        word = random.choice(letter_group)
        return word[0].text, word[2].text, word[1].text, False

    def to_string():
        return "Spanish"


class Japanese(Language):
    def __init__(self) -> None:
        super().__init__("japanese", "cjkjp")

        with open(get_path_to_resource("heisig-kanjis.csv"), "r", encoding="utf8") as csv_file:
            source = csv.DictReader(csv_file, delimiter=",")
            reader = source.reader
            self.definitions: List[str] = []
            self.definitions.extend(reader)
            self.definitions.pop(0)

    def parse_characters(self, characters: str) -> str:
        word_list = characters.split(";")
        fixed_word_list = map(lambda a: a.replace(".", "(") + ")" if "." in a else a, word_list)
        return " /".join(fixed_word_list)

    def get_definition(self):
        kanji, english, components, on_reading, kun_reading = random.choice(self.definitions)
        pronunciation = ""

        if kun_reading and on_reading:
            pronunciation = f"くん: {self.parse_characters(kun_reading)}, おん: {self.parse_characters(on_reading)}"
        elif kun_reading:
            pronunciation = f"くん: {self.parse_characters(kun_reading)}"
        elif on_reading:
            pronunciation = f"おん: {self.parse_characters(on_reading)}"

        return kanji, pronunciation, english, True

    def to_string():
        return "Japanese"


class Russian(Language):
    def __init__(self) -> None:
        super().__init__("russian", "cjkjp")

        with open(get_path_to_resource("russian_nouns.csv"), encoding="utf8") as csv_file:
            source = csv.DictReader(csv_file, delimiter="\t")
            reader = source.reader
            self.definitions: List[str] = []
            self.definitions.extend(reader)
            self.definitions.pop(0)

    def get_definition(self) -> List[str]:
        rus, _, eng, _, gender = random.choice(self.definitions)[:5]

        # TODO:
        # make it so that we see all variants of a word (gender + partner)
        # think about adding some of the extra info the data set provides

        return rus, "{%s}" % gender, eng, False

    def to_string():
        return "Russian"


class Arabic(Language):
    def __init__(self) -> None:
        super().__init__("arabic", "arabic", True)

    def to_string():
        return "Arabic"


class Bengali(Language):
    def __init__(self) -> None:
        super().__init__("bengali", "bengali", True)

    def to_string():
        return "Bengali"


class French(Language):
    def __init__(self) -> None:
        super().__init__("french", "cjkjp", True)

    def to_string():
        return "French"


class German(Language):
    def __init__(self) -> None:
        super().__init__("german", "cjkjp", True)

    def to_string():
        return "German"


class Hindi(Language):
    def __init__(self) -> None:
        super().__init__("hindi", "devanagari", True)

    def to_string():
        return "Hindi"


class Indonesian(Language):
    def __init__(self) -> None:
        super().__init__("indonesian", "cjkjp", True)

    def to_string():
        return "Indonesian"


class Korean(Language):
    def __init__(self) -> None:
        super().__init__("korean", "cjkjp", True)

    def to_string():
        return "Korean"


class Marathi(Language):
    def __init__(self) -> None:
        super().__init__("marathi", "devanagari", True)

    def to_string():
        return "Marathi"


class Portuguese(Language):
    def __init__(self) -> None:
        super().__init__("portuguese", "cjkjp", True)

    def to_string():
        return "Portuguese"


class Swahili(Language):
    def __init__(self) -> None:
        super().__init__("swahili", "cjkjp", True)

    def to_string():
        return "Swahili"


class Tamil(Language):
    def __init__(self) -> None:
        super().__init__("tamil", "tamil", True)

    def to_string():
        return "Tamil"


class Telugu(Language):
    def __init__(self) -> None:
        super().__init__("telugu", "telugu", True)

    def to_string():
        return "Telugu"


class Turkish(Language):
    def __init__(self) -> None:
        super().__init__("turkish", "eur", True)

    def to_string():
        return "Turkish"


class Urdu(Language):
    def __init__(self) -> None:
        super().__init__("urdu", "arabic", True)

    def to_string():
        return "Urdu"


# ISO_639-3 language abbreviations https://en.wikipedia.org/wiki/ISO_639-3
LANGUAGES = {
    "cmn": Mandarin,
    "jpn": Japanese,
    "rus": Russian,
    "spa": Spanish,
    "yue": Cantonese,
    "arb": Arabic,
    "ben": Bengali,
    "fra": French,
    "deu": German,
    "hin": Hindi,
    "ind": Indonesian,
    "kor": Korean,
    "mar": Marathi,
    "por": Portuguese,
    "swa": Swahili,
    "tam": Tamil,
    "tel": Telugu,
    "tur": Turkish,
    "urd": Urdu,
}

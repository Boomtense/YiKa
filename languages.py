import random
import xml.etree.ElementTree as ET
from typing import List
import csv


class Language:
    def __init__(self) -> None:
        pass

    def get_definition(self) -> List[str]:
        return ["nothing", "at", "all"]


class Cantonese(Language):
    def __init__(self) -> None:
        super().__init__()
        self.source = open("translations/cantonese.txt", "r", encoding="utf8")
        for _ in range(12):
            self.source.readline()
        self.definitions = self.source.readlines()

    def parse_definition(self, definition: str) -> List[str]:
        split_definition: str = definition.split("/")
        characters_pinyin_jyutping: str = split_definition[0]
        jyutping_start: str = characters_pinyin_jyutping.find("{")
        characters_pinyin: str = characters_pinyin_jyutping[: jyutping_start - 1]
        jyutping: str = characters_pinyin_jyutping[jyutping_start:-1]
        english: str = split_definition[1]
        character = characters_pinyin.split()[0]

        return character, self.parse_jyutping(jyutping), self.parse_jyutping(english)

    def parse_jyutping(self, jyutping: str) -> str:
        return jyutping.replace("{", "}").replace("}", "")

    def get_definition(self) -> List[str]:
        return self.parse_definition(random.choice(self.definitions))


class Mandarin(Language):
    def __init__(self) -> None:
        super().__init__()
        self.source = open("translations/mandarin.txt", "r", encoding="utf8")
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
        character = characters[1]

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
                            .replace(vowel, self.tones[ord(self.priority(vowel)) + int(num)])
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

    def get_definition(self) -> List[str]:
        return self.parse_definition(random.choice(self.definitions))


class Spanish(Language):
    def __init__(self) -> None:
        super().__init__()
        self.source = ET.parse("translations/es-en.xml")

    def get_definition(self) -> List[str]:
        root = self.source.getroot()
        letter_group = random.choice(root)
        word = random.choice(letter_group)
        return word[0].text, word[2].text, word[1].text


class Japanese(Language):
    def __init__(self) -> None:
        super().__init__()
        csv_file = open("translations/heisig-kanjis.csv", "r", encoding="utf8")
        source = csv.DictReader(csv_file, delimiter=",")
        reader = source.reader
        self.definitions: List[str] = []
        self.definitions.extend(reader)

    def get_definition(self) -> List[str]:
        kanji, english, components, on_reading, kun_reading = random.choice(self.definitions)

        # TODO: format both readings so that it doesn't look horrible on screen
        # if kun_reading and on_reading:
        #    pronunciation = f"くん: {kun_reading}, おん: {on_reading}"
        # elif kun_reading:
        #    pronunciation = f"くん: {kun_reading}"
        # elif on_reading:
        #    pronunciation = f"おん: {on_reading}"

        return kanji, (kun_reading if kun_reading else on_reading), english

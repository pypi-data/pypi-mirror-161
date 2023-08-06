#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__doc__ = """
Program for transliteration of texts written in Latin alphabet into Serbian Cyrillic.

Python implementation of great Javascript program: https://github.com/turanjanin/cirilizator .
"""

import re


class SerbCyr:

    # Digraphs must be placed first
    _initial_map = {
        "DJ": "Ђ",
        "DЈ": "Ђ", # D + cyrillic J
        "Dj": "Ђ",
        "Dј": "Ђ", # D + cyrillic j
        "LJ": "Љ",
        "LЈ": "Љ", # L + cyrillic J
        "Ǉ":  "Љ",
        "Lj": "Љ",
        "Lј": "Љ", # L + cyrillic j
        "ǈ":  "Љ",
        "NJ": "Њ",
        "NЈ": "Њ", # N + cyrillic J
        "Ǌ":  "Њ",
        "Nj": "Њ",
        "Nј": "Њ", # N + cyrillic j
        "ǋ":  "Њ",
        "DŽ": "Џ",
        "Ǆ":  "Џ",
        "DŽ": "Џ", # D + Z with caron
        "Dž": "Џ",
        "ǅ":  "Џ",
        "Dž": "Џ", # D + z with caron
        "dj": "ђ",
        "dј": "ђ", # d + cyrillic j
        "lj": "љ",
        "lј": "љ", # l + cyrillic j
        "ǉ":  "љ",
        "nj": "њ",
        "nј": "њ", # n + cyrillic j
        "ǌ":  "њ",
        "dž": "џ",
        "ǆ":  "џ",
        "dž": "џ", # d + z with caron
        "A":  "А",
        "B":  "Б",
        "V":  "В",
        "G":  "Г",
        "D":  "Д",
        "Đ":  "Ђ",
        "Ð":  "Ђ",
        "ᴆ":  "Ђ",
        "E":  "Е",
        "Ž":  "Ж",
        "Ž":  "Ж", # Z with caron
        "Z":  "З",
        "I":  "И",
        "J":  "Ј",
        "K":  "К",
        "L":  "Л",
        "M":  "М",
        "N":  "Н",
        "O":  "О",
        "P":  "П",
        "R":  "Р",
        "S":  "С",
        "T":  "Т",
        "Ć":  "Ћ",
        "Ć":  "Ћ", # C with acute accent
        "U":  "У",
        "F":  "Ф",
        "H":  "Х",
        "C":  "Ц",
        "Č":  "Ч",
        "Č":  "Ч", # C with caron
        "Š":  "Ш",
        "Š":  "Ш", # S with caron
        "a":  "а",
        "æ":  "ае",
        "b":  "б",
        "v":  "в",
        "g":  "г",
        "d":  "д",
        "đ":  "ђ",
        "e":  "е",
        "ž":  "ж",
        "ž":  "ж", # z with caron
        "z":  "з",
        "i":  "и",
        "ĳ":  "иј",
        "j":  "ј",
        "k":  "к",
        "l":  "л",
        "m":  "м",
        "n":  "н",
        "o":  "о",
        "œ":  "ое",
        "p":  "п",
        "r":  "р",
        "s":  "с",
        "ﬆ":  "ст",
        "t":  "т",
        "ć":  "ћ",
        "ć":  "ћ", # c with acute accent
        "u":  "у",
        "f":  "ф",
        "ﬁ":  "фи",
        "ﬂ":  "фл",
        "h":  "х",
        "c":  "ц",
        "č":  "ч",
        "č":  "ч", # c with caron
        "š":  "ш",
        "š":  "ш", # s with caron
    }

    _serbian_words_with_foreign_character_combinations = [
        "alchajmer",
        "ammar",
        "amss",
        "aparthejd",
        "brushalter",
        "celishod",
        "četrdesettrogodiš",
        "ddor",
        "dosjee",
        "dss",
        "devedesettrogodiš",
        "dvadesettrog",
        "epp",
        "fss",
        "gss",
        "hiperrealizam",
        "interreakc",
        "interresor",
        "intervjuu",
        "ishitren",
        "ishod",
        "ishran",
        "izzzdiovns",
        "kontinuum",
        "kss",
        "liker",
        "llsls",
        "metjuu",
        "mmf",
        "naddu",
        "natha",
        "natho",
        "najneefikas",
        "neefikas",
        "neekonomič",
        "neeksplodiran",
        "neetički",
        "neevropsk",
        "neophod",
        "neshvać",
        "neshvat",
        "obeshrabr",
        "ommetar",
        "opho",
        "ophrva",
        "othrama",
        "othuknu",
        "pash", # Pasha, jev.
        "pedesettrogod", # 53-godishnji
        "penthaus",
        "poddirektor",
        "poddisciplin",
        "poddomen",
        "poddres",
        "poluurođen",
        "posthumn",
        "posttrans",
        "posttraum",
        "pothodni",
        "pothranj",
        "pothva",
        "preddijabetes",
        "prethod",
        "prevashod",
        "ptt",
        "punkt",
        "rashla", # rashladni, rashladjivanje
        "rashod",
        "sbb",
        "sdss",
        "shem", # схема
        "shodno",
        "shvać",
        "shvat",
        "skocka",
        "snishod", # snishodljliv
        "ssp",
        "ssrnj",
        "sssr",
        "statuu",
        "superračun",
        "svrsishod",
        "šopingholi",
        "tass",
        "transseks",
        "transsibir",
        "tridesettrogodiš",
        "uppr",
        "ushić", # ushićen, ushićivali
        "ushit",
        "vakuum",
        "vannastav",
        "zoo"
    ]

    _common_foreign_words = [
        "administration",
        "adobe",
        "advanced",
        "advertising",
        "autocad",
        "bitcoin",
        "book",
        "boot",
        "cancel",
        "canon",
        "carlsberg",
        "cisco",
        "clio",
        "cloud",
        "coca-col",
        "cookie",
        "cooking",
        "cool",
        "covid",
        "dacia",
        "default",
        "develop",
        "e-mail",
        "edge",
        "email",
        "emoji",
        "english",
        "facebook",
        "fashion",
        "food",
        "foundation",
        "gaming",
        "gmail",
        "gmt",
        "good",
        "google",
        "hdmi",
        "image",
        "iphon",
        "ipod",
        "javascript",
        "jazeera",
        "joomla",
        "league",
        "like",
        "linkedin",
        "look",
        "macbook",
        "mail",
        "manager",
        "maps",
        "mastercard",
        "mercator",
        "microsoft",
        "mitsubishi",
        "notebook",
        "nvidia",
        "online",
        "outlook",
        "panasonic",
        "pdf",
        "peugeot",
        "podcast",
        "postpaid",
        "printscreen",
        "procredit",
        "project",
        "prslook",
        "punk",
        "renault",
        "rock",
        "screenshot",
        "seen",
        "selfie",
        "share",
        "shift",
        "shop",
        "smartphone",
        "space",
        "steam",
        "stream",
        "subscrib",
        "tool",
        "topic",
        "trailer",
        "ufc",
        "unicredit",
        "username",
        "viber"
    ]

    _whole_foreign_words = [
        "again",
        "air",
        "alpha",
        "and",
        "back",
        "bitcoin",
        "blue",
        "celebrities",
        "conditions",
        "co2",
        "cpu",
        "creative",
        "disclaimer",
        "dj",
        "electronics",
        "fresh",
        "fun",
        "geographic",
        "gmbh",
        "h2o",
        "hair",
        "have",
        "home",
        "ii",
        "iii",
        "iv",
        "idj",
        "idjtv",
        "life",
        "live",
        "login",
        "national",
        "made",
        "makeup",
        "must",
        "previous",
        "public",
        "reserved",
        "terms",
        "url",
        "v", # In Serbian language this is not a word, unlike in Russian
        "vii",
        "viii",
        "visa"
    ]

    _foreign_character_combinations = [
        'q',
        'w',
        'x',
        'y',
        'é',
        'á',
        'à',
        'ó',
        'ò',
        'ü',
        'ö',
        'ä',
        'ê',
        'è',
        'ú',
        'ù',
        'í',
        'ì',
        'ï',
        'ő',
        'ű',
        'ñ',
        'ş',
        'ç',
        'ğ',
        'ı',
        'ł',
        'ý',
        'ø',
        'ß',
        '&',
        '@',
        '#',
        'bb',
        'cc',
        'cs',
        'dd',
        'dh',
        'ee',
        'ff',
        'gg',
        'gy',
        'hh',
        'ie',
        'kk',
        'll',
        'ly',
        'nn',
        'ny',
        'ph',
        'pp',
        'rr',
        'sh',
        'ss',
        'sz',
        'tt',
        'uu',
        'zh',
        'zs',
        'zz',
        'ch',
        'gh',
        'th',
        '\'s',
        '\'t',
        '.com',
        '.edu',
        '.net',
        '.info',
        '.rs',
        '.org',
        '©',
        '®',
        '™'
    ]

    _triple_character_combinations = [
        "aaa", "ccc", "čč", "ćć", "eee", "fff", "hhh", "iii", "mmm",
        "ooo", "ppp", "rrr", "sss", "šš", "ttt", "uuu", "vvv", "zzz", "žž"
    ]

    _digraph_exceptions = {
        "dj": [
            "adjektiv",
            "adjunkt",
            "bazdje",
            "bdje",
            "bezdje",
            "blijedje",
            "bludje",
            "bridjе",
            "vidje",
            "vindjakn",
            "višenedje",
            "vrijedje",
            "gdje",
            "gudje",
            "gdjir",
            "daždje",
            "dvonedje",
            "devetonedje",
            "desetonedje",
            "djb",
            "djeva",
            "djevi",
            "djevo",
            "djed",
            "djejstv",
            "djel",
            "djenem",
            "djeneš",
            # "djene" rare (+ Дјене (town)), but it would colide with ђене-ђене, ђеневљанка, ђенерал итд.
            "djenu",
            "djet",
            "djec",
            "dječ",
            "djelotvo",
            "djuar",
            "djubison",
            "djubouz",
            "djuer",
            "djui",
            # "djuk", djuk (engl. Duke) косило би се нпр. са Djukanović
            "djuks",
            "djulej",
            "djumars",
            "djupont",
            "djurant",
            "djusenberi",
            "djuharst",
            "djuherst",
            "dovdje",
            "dogrdje",
            "dodjel",
            "drvodje",
            "drugdje",
            "elektrosnabdje",
            "žudje",
            "zabludje",
            "zavidje",
            "zavrijedje",
            "zagudje",
            "zadjev",
            "zadjen",
            "zalebdje",
            "zaludje",
            "zaodje",
            "zapodje",
            "zarudje",
            "zasjedje",
            "zasmrdje",
            "zastidje",
            "zaštedje",
            "zdje",
            "zlodje",
            "igdje",
            "izbledje",
            "izblijedje",
            "izvidje",
            "izdjejst",
            "izdjelj",
            "izludje",
            "isprdje",
            "jednonedje",
            "kojegdje",
            "kudjelj",
            "lebdje",
            "ludjel",
            "ludjet",
            "makfadjen",
            "marmadjuk",
            "međudjel",
            "nadjaha",
            "nadjača",
            "nadjeb",
            "nadjev",
            "nadjenul",
            "nadjenuo",
            "nadjenut",
            "najdjelotvo",
            "negdje",
            "nedjel",
            "nadjunač",
            "nenadjača",
            "nenadjebi",
            "nenavidje",
            "neodje",
            "nepodjarm",
            "nerazdje",
            "nigdje",
            "obdjel",
            "obnevidje",
            "ovdje",
            "odjav",
            "odjah",
            "odjaš",
            "odjeb",
            "odjev",
            "odjed",
            "odjezd",
            "odjek",
            "odjel",
            "odjen",
            "odjeć",
            "odjec",
            "odjur",
            "odjutros",
            "odsjedje",
            "ondje",
            "opredje",
            "osijedje",
            "osmonedje",
            "pardju",
            "perdju",
            "petonedje",
            "poblijedje",
            "povidje",
            "pogdjegdje",
            "pogdje",
            "podjakn",
            "podjamč",
            "podjastu",
            "podjemč",
            "podjar",
            "podjeb",
            "podjed",
            "podjezič",
            "podjel",
            "podjen",
            "podjes",
            "podjet",
            "pododjel",
            "pozavidje",
            "poludje",
            "poljodjel",
            "ponegdje",
            "ponedjelj",
            "porazdje",
            "posijedje",
            "posjedje",
            "postidje",
            "potpodjel",
            "poštedje",
            "pradjed",
            "prdje",
            "preblijedje",
            "previdje",
            "predvidje",
            "predjel",
            "preodjen",
            "preraspodje",
            "presjedje",
            "pridjev",
            "pridjen",
            "prismrdje",
            "prištedje",
            "probdje",
            "problijedje",
            "prodjen",
            "prolebdje",
            "prosijedje",
            "prosjedje",
            "protivdjel",
            "prošlonedje",
            "radjard",
            "razvidje",
            "razdjev",
            "razdjel",
            "razodje",
            "raspodje",
            "rasprdje",
            "remekdjel",
            "rudjen",
            "rudjet",
            "sadje",
            "svagdje",
            "svidje",
            "svugdje",
            "sedmonedjelj",
            "sijedje",
            "sjedje",
            "smrdje",
            "snabdje",
            "snovidje",
            "starosjedje",
            "stidje",
            "studje",
            "sudjel",
            "tronedje",
            "ublijedje",
            "uvidje",
            "udjel",
            "udjen",
            "uprdje",
            "usidjel",
            "usjedje",
            "usmrdje",
            "uštedje",
            "cjelonedje",
            "četvoronedje",
            "čukundjed",
            "šestonedjelj",
            "štedje",
            "štogdje",
            "šukundjed",
        ],
        "dž": [
            "feldžandarm",
            "nadžanj",
            "nadždrel",
            "nadžel",
            "nadžeo",
            "nadžet",
            "nadživ",
            "nadžinj",
            "nadžnj",
            "nadžrec",
            "nadžup",
            "odžali",
            "odžari",
            "odžel",
            "odžive",
            "odživljava",
            "odžubor",
            "odžvaka",
            "odžval",
            "odžvać",
            "podžanr",
            "podžel",
            "podže",
            "podžig",
            "podžiz",
            "podžil",
            "podžnje",
            "podžupan",
            "predželu",
            "predživot",
        ],
        "nj": [
            "anjon",
            "injaric",
            "injekc",
            "injekt",
            "injicira",
            "injurij",
            "kenjon",
            "konjug",
            "konjunk",
            "nekonjug",
            "nekonjunk",
            "ssrnj",
            "tanjug",
            "vanjezičk",
        ],
    }

    # See: https://en.wikipedia.org/wiki/Zero-width_non-joiner
    _digraph_replacements = {
        "dj": {
            "dj": "d\u200Cj",
            "Dj": "D\u200Cj",
            "DJ": "D\u200CJ",
        },
        "dž": {
            "dž": "d\u200Cž",
            "Dž": "D\u200Cž",
            "DŽ": "D\u200CŽ",
        },
        "nj": {
            "nj": "n\u200Cj",
            "Nj": "N\u200Cj",
            "NJ": "N\u200CJ",
        }
    }

    # Main method that converts Latin text to Cyrillic
    def text_to_cyrillic(self, text):
        if len(text.strip()) == 0:
            return text
        words = re.split('\s+', text)
        for i in range(len(words)):
            index = self._transliteration_index_of_word_starts_with(words[i], self._whole_foreign_words, "-")
            if index >= 0:
                words[i] = words[i][:index] + self._word_to_cyrillic(words[i][index:])
            else:
                if not self._looks_like_foreign_word(words[i]):
                    words[i] = self._word_to_cyrillic(words[i])
        return ' '.join(words)


    def _looks_like_foreign_word(self, word):
        trimmed_word = self._trim_excessive_characters(word)
        word = trimmed_word.lower()

        if word == "":
            return False

        if self._word_starts_with(word, self._serbian_words_with_foreign_character_combinations):
            return False

        if self._word_contains_string(word, self._triple_character_combinations):
            return False

        if self._word_contains_string(word, self._foreign_character_combinations):
            return True

        if self._word_starts_with(word, self._common_foreign_words):
            return True

        if self._word_is_equal_to(word, self._whole_foreign_words):
            return True

        if self._word_contains_measurement_unit(trimmed_word):
            return True

        return False


    def _word_to_cyrillic(self, word):
        word = self._split_latin_digraphs(word)
        for key, value in self._initial_map.items():
            word = word.replace(key, value)
        return word


    def _split_latin_digraphs(self, str1):
        lowercaseStr = str1.strip().lower()

        for digraph in self._digraph_exceptions:
            if not digraph in lowercaseStr:
                continue

            for word in self._digraph_exceptions[digraph]:
                if not lowercaseStr.startswith(word):
                    continue

                # Split all possible occurrences, regardless of case
                for key in self._digraph_replacements[digraph]:
                    str1 = str1.replace(key, self._digraph_replacements[digraph][key])

                break
        return str1


    def _word_contains_string(self, word, array):
        for array_word in array:
            if array_word in word:
                return True
        return False

    def _word_is_equal_to(self, word, array):
        for array_word in array:
            if word == array_word:
                return True
        return False

    def _word_starts_with(self, word, array):
        for array_word in array:
            if word.startswith(array_word):
                return True
        return False

    def _word_contains_measurement_unit(self, word):
        unit_adjacent_to_sth = "([zafpnμmcdhKMGTPEY]?([BVWJFSHCΩATNhlmg]|m[²³]?|s[²]?|cd|Pa|Wb|Hz))"
        # Removed prefix "h" (hecto-) for meters to allow transliteration of "hm", which is
        # expression of confusion in Serbian language
        unit_optionaly_adjacent_to_sth = "(°[FC]|[kMGTPZY](B|Hz)|[pnμmcdk]m[²³]?|m[²³]|[mcdh][lg]|kg|km)"
        number = "(\d+([\.,]\d)*)"
        regExp = "^(" + number + unit_adjacent_to_sth + ")|(" \
            + number + "?(" + unit_optionaly_adjacent_to_sth + "|" \
            + unit_adjacent_to_sth + "/" + unit_adjacent_to_sth + "))$"

        return re.match(regExp, word) is not None


    """
    Retrieves index of the first character of the word that should be transliterated.
    Function examines only words that have a root that is a foreign word, followed by
    some separator character and remainder of the word which is in Serbian.
    Example: dj-evi should be transliterated as dj-еви so the function retrieves 3.
    """
    def _transliteration_index_of_word_starts_with(self, word, array, char_separator):
        word = self._trim_excessive_characters(word).lower()
        if word == "":
            return -1

        appended_foreign_words = list(map(lambda el: el + char_separator, array))

        for array_word in appended_foreign_words:
            if word.startswith(array_word):
                return len(array_word)

        return -1


    # Trims white spaces and punctuation marks from the start and the end of the word.
    def _trim_excessive_characters(self, word):
        excessive_chars = "[\\s!?,:;\.\*\\-—~`'\"„”“”‘’(){}\\[\\]<>«»\\/\\\\]"
        regexp = "^(" + excessive_chars + ")+|(" + excessive_chars + ")+$"

        return re.sub(regexp, '', word)

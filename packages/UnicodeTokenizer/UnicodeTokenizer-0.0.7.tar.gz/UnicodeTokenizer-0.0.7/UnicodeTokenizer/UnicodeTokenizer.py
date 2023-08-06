# -*- coding: utf-8 -*-

import bisect
from logging import raiseExceptions
import unicodedata

# from Blocks import Blocks
# from UnicodeTokenizer.Blocks import Blocks
from .Blocks import Blocks
BlockStarts = [x[0] for x in Blocks]


def get_block(c):
    point = ord(c)
    idx = bisect.bisect_right(BlockStarts, point)-1
    if 0 <= idx <= len(Blocks) and Blocks[idx][0] <= point <= Blocks[idx][1]:
        return Blocks[idx]
    else:
        return -1, 0xffffffff, 'invalid', 0


def detect_hanzi(c):
    """
    if character c is hanzi
    """
    m, n, name, is_hanzi = get_block(c)
    return is_hanzi


def is_iso_char(c):
    m, n, name, is_hanzi = get_block(c)
    if is_hanzi:
        return True
    if n-m+1 > 256:
        return True
    return False


def split_chars(line):
    if len(line) <= 1:
        return [line]
    tokens = []
    for x in line:
        if is_iso_char(x):
            tokens.append(' ')
            tokens.append(x)
            tokens.append(' ')
        else:
            tokens.append(x)
    w = ''.join(tokens).split()
    return [x for x in w if x]


def trunc_len(words, max_len=50, never_split=None):
    tokens = []
    for x in words:
        if not x:
            continue
        if len(x) <= max_len or (never_split and x in never_split):
            tokens.append(x)
        else:
            tokens += [x[i:i+max_len] for i in range(0, len(x), max_len)]
    return tokens

# https://www.zmonster.me/2018/10/20/nlp-road-3-unicode.html


def split_category(line):
    # if len(line) <= 1:
    # return line
    l = ''
    cat0 = cat = ''
    for x in line:
        cat = unicodedata.category(x)[0]
        if cat in 'CZ':
            x = ' '
        elif cat in 'P':
            x = ' '+x+' '
        elif cat in 'LN' and cat0 != cat:
            x = ' '+x
        cat0 = cat
        l += x
    return l


def strip_accents(line):
    line = unicodedata.normalize('NFD', line)
    l = ''
    for x in line:
        if x == '-':
            d = 0
        cat = unicodedata.category(x)
        if cat == "Mn":
            continue
        l += x
    return l


def split_lanugage(line):
    if len(line) <= 1:
        return line
    l = ''
    name0 = name = ''
    for x in line:
        try:
            name = unicodedata.name(x).split(' ')[0]
            if name != name0:
                x = ' '+x
        except:
            x = ' '
        name0 = name
        l += x
    return l


def split_punctuation(line):
    if len(line) <= 1:
        return line
    l = ''
    for x in line:
        cat = unicodedata.category(x)[0]
        if cat == "P":
            x = ' '+x+' '
        l += x
    return l


def char_name(x):
    try:
        name = unicodedata.name(x).split(' ')[0]
    except:
        name = ""
        # raiseExceptions(f"{x} no name")
    return name


def full2half(s):
    # ref:https://segmentfault.com/a/1190000006197218
    t=''
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xFEE0
        c = chr(num)
        t+=c
    return t

def normalize(line, do_lower_case=True, normal_type="NFD"):
    l = line.strip()
    if do_lower_case:
        l = l.lower()
    l = unicodedata.normalize(normal_type, l)
    l=full2half(l)
    return l


def char_split(line, split_mark=True):
    chars = []
    name0 = name = ' '
    cat0 = cat = ' '
    chars0 = [x for x in line.strip() if x]
    chars = []
    start_new_word = False
    for x in chars0:
        if start_new_word and split_mark:
            chars.append(' ')
            start_new_word = False
        cat = unicodedata.category(x)
        name = char_name(x)
        if cat[0] in 'CZ':
            chars.append(' ')
        elif cat[0] in 'PS' or is_iso_char(x):
            chars.append(' ')
            chars.append(x)
            chars.append(' ')
        elif cat[0] in 'LN':
            if cat[0] != cat0[0] or name != name0:
                chars.append(' ')
            chars.append(x)
        elif cat[0] in 'M':
            start_new_word = True
            continue
        else:
            raiseExceptions(f"{x} cat{cat} not in LMNPSZC")

        cat0 = cat
        name0 = name

    l = ''.join(chars)
    tokens = [x for x in l.split() if x]
    return tokens


def blank_split(line):
    l = ''.join([x if x else ' ' for x in line])
    tokens = [x for x in l.split() if x]
    return tokens


class UnicodeTokenizer:
    def __init__(self,  do_lower_case=True, never_split=set()):
        self.do_lower_case = do_lower_case
        self.never_split = set(x for x in never_split)
        self.chars = self.load_chars()

    def load_chars(self, max_unicode=0x110000):
        chars = [chr(x) for x in range(max_unicode)]
        for i, x in enumerate(chars):
            cat = unicodedata.category(x)[0]
            name = char_name(x)
            isolate = is_iso_char(x)
            chars[i] = (cat, name, isolate)
        return chars

    def char_split(self, line, split_mark=True):
        if not line:
            return []
        l = ''
        start_new_word = False
        cat0, name0, isolate0 = self.chars[ord(line[0])]
        for i, x in enumerate(line):
            if start_new_word and split_mark:
                l += ' '
                start_new_word = False
            cat, name, isolate = self.chars[ord(x)]
            if cat in 'CZ':
                l += ' '
            elif cat in 'PS' or isolate:
                l += f' {x} '
            elif cat in 'LN':
                if i >= 1:
                    if cat != cat0 or name != name0:
                        l += ' '
                l += x
            elif cat in 'M':
                start_new_word = True
                continue  # not update
            else:
                raiseExceptions(f"{x} cat{cat} not in LMNPSZC")
            cat0 = cat
            name0 = name
        tokens = blank_split(l)
        return tokens

    def tokenize(self, line):
        words = blank_split(line)
        tokens = []
        for x in words:
            if x in self.never_split:
                tokens.append(x)
            else:
                if self.do_lower_case:
                    x = x.lower()
                if x in self.never_split:
                    tokens.append(x)
                    continue
                ts = self.char_split(x)
                if self.do_lower_case:
                    tsl = []
                    for t in ts:
                        s = normalize(t, do_lower_case=False)
                        if s in self.never_split or s == t:
                            tsl.append(t)
                        else:
                            us = self.char_split(s, split_mark=False)
                            tsl += us
                    ts = tsl
                tokens += ts
        tokens = [x for x in tokens if x]
        return tokens


if __name__ == "__main__":
    print(full2half("２０１９"))
    for x in " 〇(白":
        print(detect_hanzi(x))
    line = ''
    for i in range(128):
        try:
            c = chr(i)
            line += c
        except:
            pass
    line = "'〇㎡[คุณจะจัดพิธีแต่งงานเมื่อไรคะัีิ์ื็ํึ]Ⅷpays-g[ran]d-blanc-élevé » (白高大夏國)😀熇'\x0000𧭏２０１９\U0010ffff"
    # line = "=True"
    print("split_chars", split_chars(line))
    print("split_category", split_category(line))
    print("strip_accents", strip_accents(line))
    print("split_lanugage", split_lanugage(line))
    print("split_punctuation", split_punctuation(line))

    print("blank_split", blank_split(line))
    l2 = normalize(line)
    print(l2)
    print(char_split(line))
    print(char_split(l2))

    tokenizer = UnicodeTokenizer()
    print(tokenizer.tokenize(line))
    print(tokenizer.tokenize(line))
    import timeit
    # re=timeit.timeit("''.join(chr(x) for x in range(int(1e6))) ")
    # print(re)

    import time
    t0 = time.time()
    for i in range(10000):
        # chr(i)  # ValueError: chr() arg not in range(0x110000)
        tokenizer.tokenize(line)
    t1 = time.time()
    print(t1-t0)

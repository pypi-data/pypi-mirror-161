# -*- coding: utf-8 -*-

# http://yedict.com/zsts.htm
"""
unicode编码	字符集内容	字数
4E00-9FA5	基本区  分页：  一 二 三 四	20902
9FA6-9FFF	基本区补充	90
3400-4DB5	扩展A	6582
4DB6-4DBF	扩展A补充	10
20000-2A6D6	扩展B 分页： 一 二 三 四 五 六 七 八 九	42711
2A6D7-2A6DF	扩展B补充	9
2A700-2B734	扩展C	4149
2B735-2B739	扩展C补充	5
2B740-2B81D	扩展D	222
2B820-2CEA1	扩展E	5762
2CEB0-2EBE0	扩展F	7473
30000-3134A	扩展G => WS2015	4939
31350-323AF	扩展H(草案码，还未正式发布) => WS2017	4192
暂无unicode	扩展I(拟定中) => WS2021	4952
2F00-2FD5	康熙部首	214
2E80-2EF3	部首扩展	115
F900-FAD9	兼容汉字	472
2F800-2FA1D	兼容扩展	542
31C0-31E3	汉字笔画	36
2FF0-2FFB	汉字结构	12
3105-312F	汉语注音	43
31A0-31BF	注音扩展	30
"""
"""
https://unicode-table.com/cn/blocks/
更新较快

2E80—2EFF 中日韩部首补充
2F00—2FDF 康熙部首
2FF0—2FFF 表意文字描述符

3000—303F 中日韩符号和标点
3040—309F 日文平假名
30A0—30FF 日文片假名

3100—312F 注音字母

3130—318F 谚文兼容字母
3190—319F 象形字注释标志

31A0—31BF 注音字母扩展
31C0—31EF 中日韩笔画
"""

# raw_han_keyword = """ CJK Ideographic Ideographs Kanbun Radicals Bopomofo """
# keywords = raw_han_keyword.split()
# keywords = [x.lower() for x in keywords if x]
keywords = ['cjk', 'ideographic', 'ideographs',
            'kanbun', 'radicals', 'bopomofo']


def is_han_block(name, keywords):
    words = name.split(' ')
    words = [x.lower() for x in words if x]
    for x in words:
        for y in keywords:
            if x.startswith(y):
                return 1
    return 0


def read_blocks():
    # https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt
    doc = []
    blocks = []
    num_han = 0
    for line in open("data/Blocks.txt"):
        line = line.strip()
        if not line or line[0] == '#':
            continue
        w = line.split('; ')
        name = w[1].strip()
        a, b = w[0].split('..')
        # m = int(a, 16)
        # n = int(b, 16)
        m = '0x'+a
        n = '0x'+b
        is_han = is_han_block(name, keywords)
        row = [m, n, name, is_han]
        blocks.append(row)
        # print(f"[{hex(m)},{hex(n)},'{name}'],")
        # line=f"[{m},{n},'{name}',{is_han}],"
        if is_han:
            print(row)
            num_han += int(n, base=16)-int(m, base=16)+1
        # doc.append(line)
    # print("==blocks==")
    tgt = "data/BlocksWithHan.txt"
    with open(tgt, 'w') as f:
        for row in blocks:
            l = '\t'.join(str(x) for x in row)
            f.write(l+'\n')

    # num_han:95424 --> BlocksWithHan.txt
    print(f'num_han:{num_han} --> {tgt}')


Blocks = [
    [0x0000, 0x007F,  "Basic Latin", 0],
    [0x0080, 0x00FF,  "Latin-1 Supplement", 0],
    [0x0100, 0x017F,  "Latin Extended-A", 0],
    [0x0180, 0x024F,  "Latin Extended-B", 0],
    [0x0250, 0x02AF,  "IPA Extensions", 0],
    [0x02B0, 0x02FF,  "Spacing Modifier Letters", 0],
    [0x0300, 0x036F,  "Combining Diacritical Marks", 0],
    [0x0370, 0x03FF,  "Greek and Coptic", 0],
    [0x0400, 0x04FF,  "Cyrillic", 0],
    [0x0500, 0x052F,  "Cyrillic Supplement", 0],
    [0x0530, 0x058F,  "Armenian", 0],
    [0x0590, 0x05FF,  "Hebrew", 0],
    [0x0600, 0x06FF,  "Arabic", 0],
    [0x0700, 0x074F,  "Syriac", 0],
    [0x0750, 0x077F,  "Arabic Supplement", 0],
    [0x0780, 0x07BF,  "Thaana", 0],
    [0x07C0, 0x07FF,  "NKo", 0],
    [0x0800, 0x083F,  "Samaritan", 0],
    [0x0840, 0x085F,  "Mandaic", 0],
    [0x0860, 0x086F,  "Syriac Supplement", 0],
    [0x0870, 0x089F,  "Arabic Extended-B", 0],
    [0x08A0, 0x08FF,  "Arabic Extended-A", 0],
    [0x0900, 0x097F,  "Devanagari", 0],
    [0x0980, 0x09FF,  "Bengali", 0],
    [0x0A00, 0x0A7F,  "Gurmukhi", 0],
    [0x0A80, 0x0AFF,  "Gujarati", 0],
    [0x0B00, 0x0B7F,  "Oriya", 0],
    [0x0B80, 0x0BFF,  "Tamil", 0],
    [0x0C00, 0x0C7F,  "Telugu", 0],
    [0x0C80, 0x0CFF,  "Kannada", 0],
    [0x0D00, 0x0D7F,  "Malayalam", 0],
    [0x0D80, 0x0DFF,  "Sinhala", 0],
    [0x0E00, 0x0E7F,  "Thai", 0],
    [0x0E80, 0x0EFF,  "Lao", 0],
    [0x0F00, 0x0FFF,  "Tibetan", 0],
    [0x1000, 0x109F,  "Myanmar", 0],
    [0x10A0, 0x10FF,  "Georgian", 0],
    [0x1100, 0x11FF,  "Hangul Jamo", 0],
    [0x1200, 0x137F,  "Ethiopic", 0],
    [0x1380, 0x139F,  "Ethiopic Supplement", 0],
    [0x13A0, 0x13FF,  "Cherokee", 0],
    [0x1400, 0x167F,  "Unified Canadian Aboriginal Syllabics", 0],
    [0x1680, 0x169F,  "Ogham", 0],
    [0x16A0, 0x16FF,  "Runic", 0],
    [0x1700, 0x171F,  "Tagalog", 0],
    [0x1720, 0x173F,  "Hanunoo", 0],
    [0x1740, 0x175F,  "Buhid", 0],
    [0x1760, 0x177F,  "Tagbanwa", 0],
    [0x1780, 0x17FF,  "Khmer", 0],
    [0x1800, 0x18AF,  "Mongolian", 0],
    [0x18B0, 0x18FF,  "Unified Canadian Aboriginal Syllabics Extended", 0],
    [0x1900, 0x194F,  "Limbu", 0],
    [0x1950, 0x197F,  "Tai Le", 0],
    [0x1980, 0x19DF,  "New Tai Lue", 0],
    [0x19E0, 0x19FF,  "Khmer Symbols", 0],
    [0x1A00, 0x1A1F,  "Buginese", 0],
    [0x1A20, 0x1AAF,  "Tai Tham", 0],
    [0x1AB0, 0x1AFF,  "Combining Diacritical Marks Extended", 0],
    [0x1B00, 0x1B7F,  "Balinese", 0],
    [0x1B80, 0x1BBF,  "Sundanese", 0],
    [0x1BC0, 0x1BFF,  "Batak", 0],
    [0x1C00, 0x1C4F,  "Lepcha", 0],
    [0x1C50, 0x1C7F,  "Ol Chiki", 0],
    [0x1C80, 0x1C8F,  "Cyrillic Extended-C", 0],
    [0x1C90, 0x1CBF,  "Georgian Extended", 0],
    [0x1CC0, 0x1CCF,  "Sundanese Supplement", 0],
    [0x1CD0, 0x1CFF,  "Vedic Extensions", 0],
    [0x1D00, 0x1D7F,  "Phonetic Extensions", 0],
    [0x1D80, 0x1DBF,  "Phonetic Extensions Supplement", 0],
    [0x1DC0, 0x1DFF,  "Combining Diacritical Marks Supplement", 0],
    [0x1E00, 0x1EFF,  "Latin Extended Additional", 0],
    [0x1F00, 0x1FFF,  "Greek Extended", 0],
    [0x2000, 0x206F,  "General Punctuation", 0],
    [0x2070, 0x209F,  "Superscripts and Subscripts", 0],
    [0x20A0, 0x20CF,  "Currency Symbols", 0],
    [0x20D0, 0x20FF,  "Combining Diacritical Marks for Symbols", 0],
    [0x2100, 0x214F,  "Letterlike Symbols", 0],
    [0x2150, 0x218F,  "Number Forms", 0],
    [0x2190, 0x21FF,  "Arrows", 0],
    [0x2200, 0x22FF,  "Mathematical Operators", 0],
    [0x2300, 0x23FF,  "Miscellaneous Technical", 0],
    [0x2400, 0x243F,  "Control Pictures", 0],
    [0x2440, 0x245F,  "Optical Character Recognition", 0],
    [0x2460, 0x24FF,  "Enclosed Alphanumerics", 0],
    [0x2500, 0x257F,  "Box Drawing", 0],
    [0x2580, 0x259F,  "Block Elements", 0],
    [0x25A0, 0x25FF,  "Geometric Shapes", 0],
    [0x2600, 0x26FF,  "Miscellaneous Symbols", 0],
    [0x2700, 0x27BF,  "Dingbats", 0],
    [0x27C0, 0x27EF,  "Miscellaneous Mathematical Symbols-A", 0],
    [0x27F0, 0x27FF,  "Supplemental Arrows-A", 0],
    [0x2800, 0x28FF,  "Braille Patterns", 0],
    [0x2900, 0x297F,  "Supplemental Arrows-B", 0],
    [0x2980, 0x29FF,  "Miscellaneous Mathematical Symbols-B", 0],
    [0x2A00, 0x2AFF,  "Supplemental Mathematical Operators", 0],
    [0x2B00, 0x2BFF,  "Miscellaneous Symbols and Arrows", 0],
    [0x2C00, 0x2C5F,  "Glagolitic", 0],
    [0x2C60, 0x2C7F,  "Latin Extended-C", 0],
    [0x2C80, 0x2CFF,  "Coptic", 0],
    [0x2D00, 0x2D2F,  "Georgian Supplement", 0],
    [0x2D30, 0x2D7F,  "Tifinagh", 0],
    [0x2D80, 0x2DDF,  "Ethiopic Extended", 0],
    [0x2DE0, 0x2DFF,  "Cyrillic Extended-A", 0],
    [0x2E00, 0x2E7F,  "Supplemental Punctuation", 0],
    [0x2E80, 0x2EFF,  "CJK Radicals Supplement", 1],
    [0x2F00, 0x2FDF,  "Kangxi Radicals", 1],
    [0x2FF0, 0x2FFF,  "Ideographic Description Characters", 1],
    [0x3000, 0x303F,  "CJK Symbols and Punctuation", 1],
    [0x3040, 0x309F,  "Hiragana", 0],
    [0x30A0, 0x30FF,  "Katakana", 0],
    [0x3100, 0x312F,  "Bopomofo", 1],
    [0x3130, 0x318F,  "Hangul Compatibility Jamo", 0],
    [0x3190, 0x319F,  "Kanbun", 1],
    [0x31A0, 0x31BF,  "Bopomofo Extended", 1],
    [0x31C0, 0x31EF,  "CJK Strokes", 1],
    [0x31F0, 0x31FF,  "Katakana Phonetic Extensions", 0],
    [0x3200, 0x32FF,  "Enclosed CJK Letters and Months", 1],
    [0x3300, 0x33FF,  "CJK Compatibility", 1],
    [0x3400, 0x4DBF,  "CJK Unified Ideographs Extension A", 1],
    [0x4DC0, 0x4DFF,  "Yijing Hexagram Symbols", 0],
    [0x4E00, 0x9FFF,  "CJK Unified Ideographs", 1],
    [0xA000, 0xA48F,  "Yi Syllables", 0],
    [0xA490, 0xA4CF,  "Yi Radicals", 1],
    [0xA4D0, 0xA4FF,  "Lisu", 0],
    [0xA500, 0xA63F,  "Vai", 0],
    [0xA640, 0xA69F,  "Cyrillic Extended-B", 0],
    [0xA6A0, 0xA6FF,  "Bamum", 0],
    [0xA700, 0xA71F,  "Modifier Tone Letters", 0],
    [0xA720, 0xA7FF,  "Latin Extended-D", 0],
    [0xA800, 0xA82F,  "Syloti Nagri", 0],
    [0xA830, 0xA83F,  "Common Indic Number Forms", 0],
    [0xA840, 0xA87F,  "Phags-pa", 0],
    [0xA880, 0xA8DF,  "Saurashtra", 0],
    [0xA8E0, 0xA8FF,  "Devanagari Extended", 0],
    [0xA900, 0xA92F,  "Kayah Li", 0],
    [0xA930, 0xA95F,  "Rejang", 0],
    [0xA960, 0xA97F,  "Hangul Jamo Extended-A", 0],
    [0xA980, 0xA9DF,  "Javanese", 0],
    [0xA9E0, 0xA9FF,  "Myanmar Extended-B", 0],
    [0xAA00, 0xAA5F,  "Cham", 0],
    [0xAA60, 0xAA7F,  "Myanmar Extended-A", 0],
    [0xAA80, 0xAADF,  "Tai Viet", 0],
    [0xAAE0, 0xAAFF,  "Meetei Mayek Extensions", 0],
    [0xAB00, 0xAB2F,  "Ethiopic Extended-A", 0],
    [0xAB30, 0xAB6F,  "Latin Extended-E", 0],
    [0xAB70, 0xABBF,  "Cherokee Supplement", 0],
    [0xABC0, 0xABFF,  "Meetei Mayek", 0],
    [0xAC00, 0xD7AF,  "Hangul Syllables", 0],
    [0xD7B0, 0xD7FF,  "Hangul Jamo Extended-B", 0],
    [0xD800, 0xDB7F,  "High Surrogates", 0],
    [0xDB80, 0xDBFF,  "High Private Use Surrogates", 0],
    [0xDC00, 0xDFFF,  "Low Surrogates", 0],
    [0xE000, 0xF8FF,  "Private Use Area", 0],
    [0xF900, 0xFAFF,  "CJK Compatibility Ideographs", 1],
    [0xFB00, 0xFB4F,  "Alphabetic Presentation Forms", 0],
    [0xFB50, 0xFDFF,  "Arabic Presentation Forms-A", 0],
    [0xFE00, 0xFE0F,  "Variation Selectors", 0],
    [0xFE10, 0xFE1F,  "Vertical Forms", 0],
    [0xFE20, 0xFE2F,  "Combining Half Marks", 0],
    [0xFE30, 0xFE4F,  "CJK Compatibility Forms", 1],
    [0xFE50, 0xFE6F,  "Small Form Variants", 0],
    [0xFE70, 0xFEFF,  "Arabic Presentation Forms-B", 0],
    [0xFF00, 0xFFEF,  "Halfwidth and Fullwidth Forms", 0],
    [0xFFF0, 0xFFFF,  "Specials", 0],
    [0x10000, 0x1007F,  "Linear B Syllabary", 0],
    [0x10080, 0x100FF,  "Linear B Ideograms", 0],
    [0x10100, 0x1013F,  "Aegean Numbers", 0],
    [0x10140, 0x1018F,  "Ancient Greek Numbers", 0],
    [0x10190, 0x101CF,  "Ancient Symbols", 0],
    [0x101D0, 0x101FF,  "Phaistos Disc", 0],
    [0x10280, 0x1029F,  "Lycian", 0],
    [0x102A0, 0x102DF,  "Carian", 0],
    [0x102E0, 0x102FF,  "Coptic Epact Numbers", 0],
    [0x10300, 0x1032F,  "Old Italic", 0],
    [0x10330, 0x1034F,  "Gothic", 0],
    [0x10350, 0x1037F,  "Old Permic", 0],
    [0x10380, 0x1039F,  "Ugaritic", 0],
    [0x103A0, 0x103DF,  "Old Persian", 0],
    [0x10400, 0x1044F,  "Deseret", 0],
    [0x10450, 0x1047F,  "Shavian", 0],
    [0x10480, 0x104AF,  "Osmanya", 0],
    [0x104B0, 0x104FF,  "Osage", 0],
    [0x10500, 0x1052F,  "Elbasan", 0],
    [0x10530, 0x1056F,  "Caucasian Albanian", 0],
    [0x10570, 0x105BF,  "Vithkuqi", 0],
    [0x10600, 0x1077F,  "Linear A", 0],
    [0x10780, 0x107BF,  "Latin Extended-F", 0],
    [0x10800, 0x1083F,  "Cypriot Syllabary", 0],
    [0x10840, 0x1085F,  "Imperial Aramaic", 0],
    [0x10860, 0x1087F,  "Palmyrene", 0],
    [0x10880, 0x108AF,  "Nabataean", 0],
    [0x108E0, 0x108FF,  "Hatran", 0],
    [0x10900, 0x1091F,  "Phoenician", 0],
    [0x10920, 0x1093F,  "Lydian", 0],
    [0x10980, 0x1099F,  "Meroitic Hieroglyphs", 0],
    [0x109A0, 0x109FF,  "Meroitic Cursive", 0],
    [0x10A00, 0x10A5F,  "Kharoshthi", 0],
    [0x10A60, 0x10A7F,  "Old South Arabian", 0],
    [0x10A80, 0x10A9F,  "Old North Arabian", 0],
    [0x10AC0, 0x10AFF,  "Manichaean", 0],
    [0x10B00, 0x10B3F,  "Avestan", 0],
    [0x10B40, 0x10B5F,  "Inscriptional Parthian", 0],
    [0x10B60, 0x10B7F,  "Inscriptional Pahlavi", 0],
    [0x10B80, 0x10BAF,  "Psalter Pahlavi", 0],
    [0x10C00, 0x10C4F,  "Old Turkic", 0],
    [0x10C80, 0x10CFF,  "Old Hungarian", 0],
    [0x10D00, 0x10D3F,  "Hanifi Rohingya", 0],
    [0x10E60, 0x10E7F,  "Rumi Numeral Symbols", 0],
    [0x10E80, 0x10EBF,  "Yezidi", 0],
    [0x10F00, 0x10F2F,  "Old Sogdian", 0],
    [0x10F30, 0x10F6F,  "Sogdian", 0],
    [0x10F70, 0x10FAF,  "Old Uyghur", 0],
    [0x10FB0, 0x10FDF,  "Chorasmian", 0],
    [0x10FE0, 0x10FFF,  "Elymaic", 0],
    [0x11000, 0x1107F,  "Brahmi", 0],
    [0x11080, 0x110CF,  "Kaithi", 0],
    [0x110D0, 0x110FF,  "Sora Sompeng", 0],
    [0x11100, 0x1114F,  "Chakma", 0],
    [0x11150, 0x1117F,  "Mahajani", 0],
    [0x11180, 0x111DF,  "Sharada", 0],
    [0x111E0, 0x111FF,  "Sinhala Archaic Numbers", 0],
    [0x11200, 0x1124F,  "Khojki", 0],
    [0x11280, 0x112AF,  "Multani", 0],
    [0x112B0, 0x112FF,  "Khudawadi", 0],
    [0x11300, 0x1137F,  "Grantha", 0],
    [0x11400, 0x1147F,  "Newa", 0],
    [0x11480, 0x114DF,  "Tirhuta", 0],
    [0x11580, 0x115FF,  "Siddham", 0],
    [0x11600, 0x1165F,  "Modi", 0],
    [0x11660, 0x1167F,  "Mongolian Supplement", 0],
    [0x11680, 0x116CF,  "Takri", 0],
    [0x11700, 0x1174F,  "Ahom", 0],
    [0x11800, 0x1184F,  "Dogra", 0],
    [0x118A0, 0x118FF,  "Warang Citi", 0],
    [0x11900, 0x1195F,  "Dives Akuru", 0],
    [0x119A0, 0x119FF,  "Nandinagari", 0],
    [0x11A00, 0x11A4F,  "Zanabazar Square", 0],
    [0x11A50, 0x11AAF,  "Soyombo", 0],
    [0x11AB0, 0x11ABF,  "Unified Canadian Aboriginal Syllabics Extended-A", 0],
    [0x11AC0, 0x11AFF,  "Pau Cin Hau", 0],
    [0x11C00, 0x11C6F,  "Bhaiksuki", 0],
    [0x11C70, 0x11CBF,  "Marchen", 0],
    [0x11D00, 0x11D5F,  "Masaram Gondi", 0],
    [0x11D60, 0x11DAF,  "Gunjala Gondi", 0],
    [0x11EE0, 0x11EFF,  "Makasar", 0],
    [0x11FB0, 0x11FBF,  "Lisu Supplement", 0],
    [0x11FC0, 0x11FFF,  "Tamil Supplement", 0],
    [0x12000, 0x123FF,  "Cuneiform", 0],
    [0x12400, 0x1247F,  "Cuneiform Numbers and Punctuation", 0],
    [0x12480, 0x1254F,  "Early Dynastic Cuneiform", 0],
    [0x12F90, 0x12FFF,  "Cypro-Minoan", 0],
    [0x13000, 0x1342F,  "Egyptian Hieroglyphs", 0],
    [0x13430, 0x1343F,  "Egyptian Hieroglyph Format Controls", 0],
    [0x14400, 0x1467F,  "Anatolian Hieroglyphs", 0],
    [0x16800, 0x16A3F,  "Bamum Supplement", 0],
    [0x16A40, 0x16A6F,  "Mro", 0],
    [0x16A70, 0x16ACF,  "Tangsa", 0],
    [0x16AD0, 0x16AFF,  "Bassa Vah", 0],
    [0x16B00, 0x16B8F,  "Pahawh Hmong", 0],
    [0x16E40, 0x16E9F,  "Medefaidrin", 0],
    [0x16F00, 0x16F9F,  "Miao", 0],
    [0x16FE0, 0x16FFF,  "Ideographic Symbols and Punctuation", 1],
    [0x17000, 0x187FF,  "Tangut", 0],
    [0x18800, 0x18AFF,  "Tangut Components", 0],
    [0x18B00, 0x18CFF,  "Khitan Small Script", 0],
    [0x18D00, 0x18D7F,  "Tangut Supplement", 0],
    [0x1AFF0, 0x1AFFF,  "Kana Extended-B", 0],
    [0x1B000, 0x1B0FF,  "Kana Supplement", 0],
    [0x1B100, 0x1B12F,  "Kana Extended-A", 0],
    [0x1B130, 0x1B16F,  "Small Kana Extension", 0],
    [0x1B170, 0x1B2FF,  "Nushu", 0],
    [0x1BC00, 0x1BC9F,  "Duployan", 0],
    [0x1BCA0, 0x1BCAF,  "Shorthand Format Controls", 0],
    [0x1CF00, 0x1CFCF,  "Znamenny Musical Notation", 0],
    [0x1D000, 0x1D0FF,  "Byzantine Musical Symbols", 0],
    [0x1D100, 0x1D1FF,  "Musical Symbols", 0],
    [0x1D200, 0x1D24F,  "Ancient Greek Musical Notation", 0],
    [0x1D2E0, 0x1D2FF,  "Mayan Numerals", 0],
    [0x1D300, 0x1D35F,  "Tai Xuan Jing Symbols", 0],
    [0x1D360, 0x1D37F,  "Counting Rod Numerals", 0],
    [0x1D400, 0x1D7FF,  "Mathematical Alphanumeric Symbols", 0],
    [0x1D800, 0x1DAAF,  "Sutton SignWriting", 0],
    [0x1DF00, 0x1DFFF,  "Latin Extended-G", 0],
    [0x1E000, 0x1E02F,  "Glagolitic Supplement", 0],
    [0x1E100, 0x1E14F,  "Nyiakeng Puachue Hmong", 0],
    [0x1E290, 0x1E2BF,  "Toto", 0],
    [0x1E2C0, 0x1E2FF,  "Wancho", 0],
    [0x1E7E0, 0x1E7FF,  "Ethiopic Extended-B", 0],
    [0x1E800, 0x1E8DF,  "Mende Kikakui", 0],
    [0x1E900, 0x1E95F,  "Adlam", 0],
    [0x1EC70, 0x1ECBF,  "Indic Siyaq Numbers", 0],
    [0x1ED00, 0x1ED4F,  "Ottoman Siyaq Numbers", 0],
    [0x1EE00, 0x1EEFF,  "Arabic Mathematical Alphabetic Symbols", 0],
    [0x1F000, 0x1F02F,  "Mahjong Tiles", 0],
    [0x1F030, 0x1F09F,  "Domino Tiles", 0],
    [0x1F0A0, 0x1F0FF,  "Playing Cards", 0],
    [0x1F100, 0x1F1FF,  "Enclosed Alphanumeric Supplement", 0],
    [0x1F200, 0x1F2FF,  "Enclosed Ideographic Supplement", 1],
    [0x1F300, 0x1F5FF,  "Miscellaneous Symbols and Pictographs", 0],
    [0x1F600, 0x1F64F,  "Emoticons", 0],
    [0x1F650, 0x1F67F,  "Ornamental Dingbats", 0],
    [0x1F680, 0x1F6FF,  "Transport and Map Symbols", 0],
    [0x1F700, 0x1F77F,  "Alchemical Symbols", 0],
    [0x1F780, 0x1F7FF,  "Geometric Shapes Extended", 0],
    [0x1F800, 0x1F8FF,  "Supplemental Arrows-C", 0],
    [0x1F900, 0x1F9FF,  "Supplemental Symbols and Pictographs", 0],
    [0x1FA00, 0x1FA6F,  "Chess Symbols", 0],
    [0x1FA70, 0x1FAFF,  "Symbols and Pictographs Extended-A", 0],
    [0x1FB00, 0x1FBFF,  "Symbols for Legacy Computing", 0],
    [0x20000, 0x2A6DF,  "CJK Unified Ideographs Extension B", 1],
    [0x2A700, 0x2B73F,  "CJK Unified Ideographs Extension C", 1],
    [0x2B740, 0x2B81F,  "CJK Unified Ideographs Extension D", 1],
    [0x2B820, 0x2CEAF,  "CJK Unified Ideographs Extension E", 1],
    [0x2CEB0, 0x2EBEF,  "CJK Unified Ideographs Extension F", 1],
    [0x2F800, 0x2FA1F,  "CJK Compatibility Ideographs Supplement", 1],
    [0x30000, 0x3134F,  "CJK Unified Ideographs Extension G", 1],
    [0xE0000, 0xE007F,  "Tags", 0],
    [0xE0100, 0xE01EF,  "Variation Selectors Supplement", 0],
    [0xF0000, 0xFFFFF,  "Supplementary Private Use Area-A", 0],
    [0x100000, 0x10FFFF,  "Supplementary Private Use Area-B", 0],
]


if __name__ == "__main__":
    read_blocks()

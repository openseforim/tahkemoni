"""Build the side-by-side page for one gate of the Taḥkemoni, and the index page.

Usage: py -3.13 scripts/build_page.py 40 "The Fortieth Gate" "The pen and the sword: which is more needed"

Inputs (in data/):
  gate-NN.he.json     from extract_hebrew.py (blocks with kind and lines)
  gate-NN.en.txt      one English line for each Hebrew line; a blank line between blocks;
                      a verse line has its two halves split by " / "
  gate-NN.notes.json  notes for the marks "⚠n"
Output: docs/gate-NN.html, then docs/index.html (from GATES below).
The script stops if the English and Hebrew block or line counts do not agree.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
e = html.escape

# gates that have a page: number -> (English title, subtitle)
GATES = {
    0: ("Introduction", "The author's preface: praise of God, the soul and the intellect, the Hebrew language as a bride, why the book was written, and the dedication"),
    1: ("The First Gate", "How the book came to be, and in whose name it was composed: a friend's challenge, the defense of Hebrew, and the praise of the Nasi Josiah"),
    2: ('The Second Gate', 'A preacher in the isles of the sea: a sermon on the false bride of this world, the grave and the hypocrites, and the preacher is Ḥever in disguise'),
    3: ('The Third Gate', 'A glutton at a feast in Babylon silences the guests who mocked him, with a survey of the Hebrew poets of Spain that ends in praise of Judah Halevi'),
    4: ('The Fourth Gate', 'Two poets quarrel before a judge over who is more eloquent: one praises the ant, the other the flea, and they turn out to be Ḥever and his son'),
    5: ('The Fifth Gate', 'A company of friends in spring: twelve poets each praise one month of the year, from Nisan to Adar, and the drinkers of Damascus learn their praises by heart'),
    6: ('The Sixth Gate', 'Ḥever tells how an old matchmaker tricked him into marrying a hideous bride, and how he fled on the wedding night'),
    7: ('The Seventh Gate', 'Two champions at war: a battle between armies seen by travellers caught between them, and the boasts of two warriors who meet in single combat'),
    8: ('The Eighth Gate', 'A letter that praises a prince when read forward and curses him when read backward, and two lines of verse that turn the same way'),
    9: ('The Ninth Gate', 'Thirty poets set a disguised old man thirty biblical verses as poem endings; he caps each one, and he is Ḥever the Kenite'),
    10: ('The Tenth Gate', "The villager's hospitality and the pious cock: a guest who says he is sick asks to eat the rooster, which escapes to the synagogue roof and preaches against its owners until it is spared"),
    11: ('The Eleventh Gate', 'Three proofs of skill in Bethlehem: a poem in Hebrew, Arabic and Aramaic, a letter of praise with a resh in every word, and a second letter with no resh at all'),
    12: ('The Twelfth Gate', "Miserliness crowned king of the Jews of the East: his dream, his prison and the dove's letter, the war of the communities against Generosity, and how generosity was lost"),
    13: ('The Thirteenth Gate', 'On Judgment Day the soul and the body blame each other; the Intellect and the Inclination argue for the soul, and repentance wins'),
    14: ('The Fourteenth Gate', "An old sage, asked by his students for a prayer, composes two: a hymn on God's unity and goodness, and a penitent's lament over sin and lust; then he is revealed as Ḥever the Kenite"),
    15: ('The Fifteenth Gate', 'After a shipwreck, Ḥever the Kenite comforts Heman with a prayer to Moses the man of God, and the prayer restores his fortune'),
    16: ('The Sixteenth Gate', 'Seven poets each praise their own poetry before Ḥever the Kenite, and he finds all seven equal'),
    17: ('The Seventeenth Gate', 'The heretic and the believer: Ḥever describes the Samaritans and the Karaites, and tells of a debate in verse on whether the Law of Moses needs the sages'),
    18: ('The Eighteenth Gate', 'How Hebrew poetry came from the Arabs to Spain: an old sage tells the history of the Spanish poets, gives the seven conditions of a good poem, and mocks the poets of Provence, France, Greece and the East'),
    19: ('The Nineteenth Gate', 'Seven young men by the Euphrates argue which quality is best, and an old man, Ḥever in disguise, gives the prize to generosity'),
    20: ('The Twentieth Gate', 'Seven veiled maidens bewitch Heman in the field, and the loveliest of them unveils to show Ḥever the Kenite with a long beard and a drawn sword'),
    21: ('The Twenty-First Gate', 'Ḥever greets a hungry villager by a false name, pretends to grieve for his dead parents, feasts with him in the market, and leaves him to pay the bill'),
    22: ('The Twenty-Second Gate', 'An Arab astrologer reads the stars and the sand at the city gate; when Ḥever and his friends ask when the exile will end, he denounces them, and only a just judge saves them'),
    23: ('The Twenty-Third Gate', "Ḥever, robbed and beaten, runs off from Heman's hospitality, then comes back rich, and tells how a prince's request for a poem of mourning and joy made his fortune"),
    24: ('The Twenty-Fourth Gate', 'The ignorant cantor: his blunders in the Sabbath prayers, a dispute on whether piyyutim belong in the service, and a poem against those who call prayer optional'),
    25: ('The Twenty-Fifth Gate', 'A hunter with horse, hawk and hounds destroys a family of gazelles, and the old man draws the moral: all creatures prey on each other and are equal in death'),
    26: ('The Twenty-Sixth Gate', 'Travel and staying at home: an old man in Basra tells the miseries of the road, then, when asked, its blessings, and at last tells his name, Ḥever'),
    27: ('The Twenty-Seventh Gate', "Wine praised and condemned: an old drinker extols the vine, then at the company's request shows its evils, and many of them vow to give it up"),
    28: ('The Twenty-Eighth Gate', "Heman's pilgrimage to Jerusalem: a lament for Zion, how the Jews came back to the city, the strife among them, and a meeting with Ḥever the Kenite"),
    29: ('The Twenty-Ninth Gate', "A ragged father and his young son beg in a Nineveh synagogue in the winter cold; the son's speech opens the congregation's hearts and purses"),
    30: ('The Thirtieth Gate', 'The traveling doctor: an old quack in the square sells cures for every disease to the crowd, and when unmasked, blames Time for his trade'),
    31: ('The Thirty-First Gate', 'A veiled rider poses as a maiden in distress, makes a band of warriors bind one another, and dies by the knife Ḥever hid in his shoe'),
    32: ('The Thirty-Second Gate', 'A contest in description: a young poet starts a verse on each of twenty things, from the pen to the moon, and an old man caps every one, until he reveals that he is Ḥever'),
    33: ('The Thirty-Third Gate', 'A silent old man shows a company of poets how to make the "linked" poem, in a sermon and an alphabet of short poems with double-meaning rhymes, and then reveals that he is Ḥever'),
    34: ('The Thirty-Fourth Gate', 'A boastful merchant shows his guest every part of his house, his wife, his servant boy and even his privy before any food comes, until the hungry guest runs away'),
    35: ('The Thirty-Fifth Gate', "Ezra's tomb by the river: how a herdsman's dream found it, the light that rises over it at night, and two poems, at Ezra's grave and at Ezekiel's"),
    36: ('The Thirty-Sixth Gate', "Ḥever, found drinking in a tavern, tells how he escaped a besieged city, boasted of his learning before a crowd, and answered a young man's questions on wisdom and conduct"),
    37: ('The Thirty-Seventh Gate', 'The snake charmer: in the wilderness a man is bitten by a snake, and a stranger calls up all the serpents with spells and makes the guilty one suck out its own venom'),
    38: ('The Thirty-Eighth Gate', 'A storm at sea: a calm old man on board sells the frightened passengers sea charms, and on dry land he turns out to be Ḥever'),
    39: ('The Thirty-Ninth Gate', 'Day and Night argue about which of them is greater, until Night gives way, and the storyteller is revealed as Ḥever'),
    40: ("The Fortieth Gate", "The pen and the sword: which is more needed by men and by their wars"),
    41: ('The Forty-First Gate', 'Man and woman: an old man and a bold woman argue in the market square over which of them the world depends on'),
    42: ('The Forty-Second Gate', 'Generosity and miserliness: an old man argues for the closed hand against a young champion of giving, then concedes so that the churls may not boast, and is revealed as Ḥever'),
    43: ('The Forty-Third Gate', 'The sea and the dry land: each boasts of its power and its merits and accuses the other, until their elders make peace between them'),
    44: ('The Forty-Fourth Gate', 'An old teacher has fifty students each give a wise saying; when they finish, he names himself in verse as Ḥever the Kenite'),
    45: ('The Forty-Fifth Gate', 'Twenty-four sages each tell a proverb of wisdom: the pious and the dead, mourners and lovers, misers, poets and boasters'),
    46: ('The Forty-Sixth Gate', "Ḥever the Kenite's tour of the Jewish communities of Spain, Provence, Egypt, the Land of Israel, Syria and Iraq: praise of their generous and learned men, and satire of the wicked and the mean"),
    47: ('The Forty-Seventh Gate', 'Eight cities, from Alexandria to Babylon, each boast in turn that the first place is theirs'),
    48: ('The Forty-Eighth Gate', "The lovesick man and the free physician: two prescriptions for love, one made from the beloved's charms and one from the lover's sorrows"),
    49: ('The Forty-Ninth Gate', 'A spring wind leads Heman into a garden, where he praises its fruits one by one in short poems, then finds Ḥever the Kenite among a company of young poets'),
    50: ('The Fiftieth Gate', 'Ḥever recites his separate poems to a company of poets: repentance and Zion, praise and blame of patrons, wine, love and satire, and an account of the journey to Jerusalem, Damascus and Aleppo'),
}
# Project Ben-Yehuda texts: gate number -> (work id, Hebrew subtitle). Gate 35 is not on Project Ben-Yehuda.
BY = {
    0: (32702, ""),
    1: (32703, "מוֹדִיעַ הֲוָיַת הַסֵּפֶר, וְעַל שֵׁם מִי חִבְּרוֹ בְּאִמְרֵי שֶׁפֶר"),
    2: (7763, "בְּשֶבַח הַמּוֹכִיחַ, הַמַּהְבִּיל עִנְיְנֵי הָעוֹלָם וּמֵפִיץ וּמַדִּיחַ"),
    3: (1738, "הַמּוֹדִיעַ תֹּקֶף הַשִּׁיר וּמַהֲלָלוֹ, וּשְׁמוֹת הַמְשׁוֹרְרִים אִישׁ אִישׁ עַל דִּגְלוֹ"),
    4: (32704, "בְּשֶׁבַח שְׁנֵי מְשׁוֹרְרִים, מִי יָשִׁיר שִׁירִים יוֹתֵר יְקָרִים"),
    5: (32705, "בְּשֶׁבַח י\"ב מְשׁוֹרְרִים, אֲשֶׁר כָּל אֶחָד עַל חֹדֶשּ אֶחָד קוֹלוֹ יָרִים."),
    6: (592, "בְּעִנְיַן זִוּוּג אִשָּה כְעוּרָה, חָשַׁךְ מִשְּׁחוֹר תָּאֳרָה"),
    7: (8405, "מִשְּׁנֵי גִבּוֹרִים, הַנִּלְחָמִים כִּשְׁנֵי כְפִירִים"),
    8: (6786, "בְּמַהֲלַל אִגֶּרֶת יְשָׁרָה, וּכְעִירוּתָהּ בִּקְרִיאַת אוֹתָהּ נְזוֹרָה"),
    9: (126, "בִּשְׁלֹשִׁים מְשׁוֹרְרִים מִתְהַלְּלִים, מִי יַעֲשֶׂה שִׁירִים יוֹתֵר מְעֻלִּים"),
    10: (7444, "בַּחֲסִידוּת הַכָּפְרִי, כְּעֵת בַּמָּרוֹם יַמְרִיא"),
    11: (8082, "בְּמַהֲלַל מְלִיצָה בְּכָל מִלּוֹתֶיהָ רֵי\"שׁ, וְהַשְּׁנִיָה לָהּ"),
    12: (32706, "מֵהַכִּילוּת וְהַנְּדִיבוּת וּמְרִיבוֹתֵיהֶם. מַחְלְקוֹתָם וּמִלְחֲמוֹתֵיהֶם."),
    13: (32724, "וִכּוּחַ הַנֶּפֶשׁ עִם הַגּוּף וְהַשֵּׂכֶל. מִי מִשְּׁלָשְׁתָּם הַנּוֹכֵל"),
    14: (32725, "בְּסֵדֶר תְּפִלָּה יְקָרָה. לֹא יִשָּׁקֵל כֶּסֶף מְחִירָהּ"),
    15: (32726, "תְּפִלָּה לְמשֶׁה אִישׁ הָאֱלֹהִים. הַפּוֹתַחַת לְכָל אוֹמְרָהּ שַׁעֲרֵי גְבוֹהִים."),
    16: (7111, "בְּוִכּוּחַ שִבְעָה מְשוֹרְרִים. מִי יְחַבֵּר שִירִים יְקָרִים"),
    17: (32994, "בְּוִכּוּחַ הַמִּין וְהַמַּאֲמִין. זֶה עַל שְׂמֹאל וְזֶה עַל יָמִין."),
    18: (32995, "בִּידִיעַת הַשִּׁיר מֵאַיִן עָלָה וְיָרָד. אִם מִבְּנֵי עֲרָב אוֹ מִבְּנֵי סְפָרָד"),
    19: (33359, "מִשְׁבְעָה בַחוּרֵי חֶמֶד טוֹבָה. מִתְוַכְּחִים אֵיזוֹ מִדָּה טוֹבָה"),
    20: (32996, "מִשֶּׁבַע הַבְּתוּלוֹת וְתַחְבּוּלוֹתֵיהֶן"),
    21: (33016, "בְּעָרְמַת חֶבֶר הַקֵּינִי. עִם הַכָּפְרִי הֶעָנִי"),
    22: (33017, "עִנְיַן הָאִישׁ הַחוֹזֶה בַכּוֹכַבִים וּמַזָּלוֹת וּבְעָרְמָתוֹ וְשִׂכְלוֹ יְדַבֵּר גְּדוֹלוֹת"),
    23: (33018, "בְּצָרַת חֶבֶר הַקֵּינִי וְדַאֲגָתוֹ. וּמֶמְשַׁלְתּוֹ וּמַעֲלָתוֹ."),
    24: (33019, "בִּשְׁלִיחַ צִבּוּר וּתְפִלּוֹתָיו. וְסִפּוּר שִׁבּוּשָׁיו וְטָעֻיוֹתָיו."),
    25: (33020, "כַּצַּיָּד הַגִּבּוֹר וְהֶחָזָק. רָצוֹא וָשׁוֹב כְּמַרְאֵה הַבָּזָק"),
    26: (33021, "בְּסִפּוּר עִנְיְנֵי הַדְּרָכִים. וְכָל אֲשֶׁר בָּם נִמְשָׁכִים."),
    27: (33022, "בְּשֶׁבַח הַיַיִן וְתוֹעֲלוֹתָיו. וְהַמִּקְרִים אֲשֶׁר יִקְרוּ לְשׁוֹתָיו"),
    28: (33023, "בְּשִׁבְחֵי צִיּוֹן וִירוּשָׁלַיִם. וּבַקָּשָׁה רוּמָהּ תַּעֲלֶה לַשָּׁמַיִם."),
    29: (33024, "הָאָב וּבְנוֹ לְרֹעַ זְמַנָּם. שׁוֹאֲלִים לִמְלֹאת סִפְקָם."),
    30: (33025, "הָרוֹפֵא הָאוֹרֵחַ. וּמִינֵי תְּרוּפוֹתָיו בָּרְחוֹבוֹת צוֹרֵחַ"),
    31: (32730, "כַּפָּרָשׁ אֲשֶׁר הֵתֵל בְּגִבּוֹרִים. וַיַּשְׁקֵם כּוֹס לַעֲנָה וְתַמְרוּרִים"),
    32: (32731, "בְּבָחוּר בְּשִׁירִים חֲיָלִים יְגַבֵּר. וְהַזָּקֵן מֵשִׁיב סְלָעִים יְשַׁבֵּר."),
    33: (32732, "בְּשִׁירִים עַל אַלְפָ\"א בֵיתָ\"א יְקָרִים. מֵהַרֲרֵי שֵׂכֶל גְּזוּרִים."),
    34: (1441, "בְּסִפּוּר הַסּוֹחֵר לָאוֹרֵחַ מֶמְשַׁלְתּוֹ. וּבְהַרְאוֹתוֹ אֶת עֹשֶׁר גְּדֻלָּתוֹ"),
    36: (33031, "בִּשְׁאֵלוֹת וּתְשׁוּבוֹת. זֶה שׁוֹאֵל וְזֶה מֵשִׁיב בְּמִלִּים עֲרֵבוֹת"),
    37: (33032, "מִן הַנָּשׁוּךְ מֵהַנָּחָשׁ. אֲשֶׁר אֵין לוֹ לָחַשׁ"),
    38: (33033, "בִּסְפִינָה מִסְתָּעֶרֶת בַּיָּם. מִשְּאוֹן גַּלָּיו וְדָכְיָם"),
    39: (33034, "וִכּוּחַ הַלַּיְלָה וְהַיּוֹם. מִי הוּא יוֹתֵר נוֹרָא וְאָיֹם"),
    40: (33035, "הָעֵט וְהַחֶרֶב וּמַחְלְקוֹתָם. מִי יוֹתֵר נִצְרָךְ לְאִישִׁים וּלְמִלְחַמְתָּם"),
    41: (33036, "מַחֲלֹקֶת הָאִישׁ וְהָאִשָּׁה. מִי הוּא יוֹתֵר קִיּוּם הָעוֹלָם וְאִשָּׁהּ"),
    42: (33037, "מְרִיבַת הַכִּילוּת וְהַנְּדִיבוּת. מִי יוֹתֵר נִכְבָּד בֵּין אַנְשֵׁי הַחֲשִׁיבוּת"),
    43: (33038, "מְרִיבַת הַיָּם וְהַיַּבָּשָׁה. מִי הִיא יוֹתֵר חֲשׁוּבָה וּדְרוּשָׁה"),
    44: (33360, "בְּרַב הַשוֹאֵל לְתַלְמִידָיו שְׁאֵלוֹת. לְהַבְחִין תַּלְמִידָיו בַּתְּשׁוּבוֹת הָעוֹלוֹת"),
    45: (33361, "מִמִּשְׁלֵי הַחָכְמָה. וְתַעֲלוּמוֹת סְתוּמָה"),
    46: (6457, "סִפּוּר אַנְשֵׁי הַמְּדִינוֹת וּמַעֲלוֹתֵיהֶם. וְחֶסְרוֹנָם וּגְרִיעוּת מִדּוֹתֵיהֶם"),
    47: (32733, "בְּשֶׁבַח כָּל מְדִינָה. זֹאת אוֹמֶרֶת אֲנִי אֶעֱבֹר רִאשׁוֹנָה"),
    48: (32734, "הַחוֹלֶה וְהָרוֹפֵא. בְּתַחְלוּאֵי הַחֵשֶׁק מֻכֶּה וְנִסְפֶּה."),
    49: (32735, "בְּשֶּׁבַח פֵּרוֹת אִילָנֵי הַגָּן"),
    50: (32736, "בְּשִׁירִים נִפְרָדִים. מִזָּהָב וּמִפָּז רַב נֶחֱמָדִים"),
}
BYURL = "https://benyehuda.org/read/{}"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Hebrew:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="/assets/os.css">
<script src="/assets/os.js" defer></script>
</head>
<body>
"""


def read_english(path):
    blocks, cur = [], []
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if line:
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def fmt_en(text):
    text = e(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]", r'<span class="ref">[\1]</span>', text)
    return re.sub(r"\s*⚠(\d+)", r'<a class="warn" href="#n\1" id="r\1" title="uncertain rendering">⚠\1</a>', text)


def halves(text, fmt):
    """A verse line: two halves, shown apart."""
    if " / " not in text:
        return fmt(text)
    parts = text.split(" / ")
    if len(parts) > 2:  # a line in three parts (the trilingual poem of gate 11)
        return " ".join(f'<span class="h3">{fmt(p)}</span>' for p in parts)
    a, b = parts
    return f'<span class="h1">{fmt(a)}</span> <span class="h2">{fmt(b)}</span>'


def gate_page(num, title, subtitle):
    stem = f"gate-{num:02d}"
    he = json.loads((ROOT / "data" / f"{stem}.he.json").read_text(encoding="utf-8"))
    en = read_english(ROOT / "data" / f"{stem}.en.txt")
    notes = json.loads((ROOT / "data" / f"{stem}.notes.json").read_text(encoding="utf-8"))
    hb = he["blocks"]
    bad = len(hb) != len(en)
    if bad:
        print(f"block count: Hebrew {len(hb)}, English {len(en)}")
    for i, (h, x) in enumerate(zip(hb, en)):
        if len(h["lines"]) != len(x):
            bad = True
            print(f"block {i}: Hebrew {len(h['lines'])} lines, English {len(x)} lines: {x[0][:50]}")
        for j, (hl, xl) in enumerate(zip(h["lines"], x)):
            if (" / " in hl) != (" / " in xl):
                bad = True
                print(f"block {i} line {j + 1}: half-line marks differ: {xl[:50]}")
    if bad:
        sys.exit("alignment errors; no page written")

    rows, n = [], 0
    for h, x in zip(hb, en):
        rows.append(f'<section class="blk {h["kind"]}{" supp" if h.get("source") else ""}">')
        if h.get("source"):
            rows.append(f'<p class="supp-label">Not in the Ben-Yehuda text; from {e(h["source"])}, unvocalized</p>')
        for hl, xl in zip(h["lines"], x):
            n += 1
            rows.append(f'<div class="row" id="l{n}"><a class="ln" href="#l{n}">{n}</a>'
                        f'<p class="en">{halves(xl, fmt_en)}</p>'
                        f'<p class="he" lang="he" dir="rtl">{halves(hl, lambda s: e(s, quote=False))}</p></div>')
        rows.append("</section>")
    note_rows = "\n".join(
        f'<li id="n{k}"><a href="#r{k}">⚠{k}</a> <span lang="he" dir="rtl" class="he-inline">{e(v["he"])}</span>'
        f' — {e(v["note"], quote=False)}</li>' for k, v in notes.items())
    if he.get("source_id"):
        srclink = (f'<p class="srclink"><a href="{BYURL.format(he["source_id"])}">'
                   f'{"The introduction" if num == 0 else f"Gate {num}"} on Project Ben-Yehuda ↗</a></p>')
        srcnote = f'Hebrew text: <a href="{BYURL.format(he["source_id"])}">Project Ben-Yehuda</a>.'
        if any(b.get("source") for b in hb):
            srcnote += " Passages missing there are added from Kaminka's edition (Warsaw 1899), unvocalized, and marked."
    else:
        srclink = (f'<p class="srclink"><a href="https://archive.org/details/TachkemoniYehudaAlchariziWarsaw1899">'
                   f'Kaminka\'s edition (Warsaw 1899) on archive.org ↗</a></p>')
        srcnote = (f"Hebrew text: {e(he.get('source', 'Kaminka 1899'))}, unvocalized, transcribed from the scan; this gate "
                   f"is not on Project Ben-Yehuda.")
    keys = sorted(GATES)
    i = keys.index(num)
    label = lambda k: "Introduction" if k == 0 else f"Gate {k}"
    prev = f'<a href="gate-{keys[i - 1]:02d}.html" rel="prev">← {label(keys[i - 1])}</a>' if i > 0 else ""
    nxt = f'<a href="gate-{keys[i + 1]:02d}.html" rel="next">{label(keys[i + 1])} →</a>' if i + 1 < len(keys) else ""
    pn = f'<span class="pn">{prev}{nxt}</span>' if prev or nxt else ""
    page = HEAD.format(title=f"{e(title)} — al-Ḥarizi, Taḥkemoni") + f"""<header class="chapter">
<nav class="crumb" aria-label="Gates"><span><a href="index.html">All gates</a> · {label(num)}</span>{pn}</nav>
<p class="title-he" lang="he" dir="rtl">{e(he["title"])}</p>
{f'<p class="sub-he" lang="he" dir="rtl">{e(he["subtitle"])}</p>' if he["subtitle"] else ""}
<h1>{e(title)}</h1>
<p class="sub">{e(subtitle)}</p>
{srclink}
<details class="about"><summary>About this text</summary>
<p class="meta">{n} lines. One row is one rhyme unit of the rhymed prose, or one line of verse (its two halves set apart).
References in <span class="ref">[gray brackets]</span> are the translator's identifications of biblical phrases.
<a class="warn" href="#notes">⚠</a> marks an uncertain rendering.
Each line number is a link to that line.
{srcnote}</p>
</details>
</header>
<main>
{chr(10).join(rows)}
</main>
<footer id="notes">
<h2>Uncertain renderings</h2>
<ul class="notes">
{note_rows}
</ul>
<nav class="crumb foot" aria-label="Gates"><span><a href="index.html">All gates</a></span>{pn}</nav>
</footer>
</body>
</html>
"""
    out = ROOT / "docs" / f"{stem}.html"
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}: {len(hb)} blocks, {n} lines")
    return n


def index_page(counts):
    def row(k):
        name = "Introduction" if k == 0 else str(k)
        if k in GATES:
            return (f'<tr class="done"><td><a href="gate-{k:02d}.html">{name}</a></td><td><a href="gate-{k:02d}.html">{e(GATES[k][1])}</a></td>'
                    f'<td>{counts[k]} lines</td></tr>')
        sub = f'<span lang="he" dir="rtl">{e(BY[k][1])}</span>' if k in BY and BY[k][1] else ""
        return f'<tr><td>{name}</td><td>{sub}</td><td>Not started</td></tr>'
    rows = "\n".join(row(k) for k in range(51))
    first = min(GATES)  # 0 = the introduction
    page = HEAD.format(title="Judah al-Ḥarizi, Taḥkemoni: Hebrew and English") + f"""<header>
<h1>Judah al-Ḥarizi, <i>Taḥkemoni</i></h1>
<p class="sub">The Hebrew maqamat, with an English translation line by line · <span lang="he" dir="rtl">ספר תחכמוני</span></p>
<p class="meta">Judah al-Ḥarizi (about 1165 – 1225) wrote the <i>Taḥkemoni</i>, fifty gates of Hebrew rhymed prose with poems set
into it. The narrator, Heman the Ezrahite, meets again and again the wandering poet Ḥever the Kenite. The book was the model for
Immanuel of Rome's <a href="/immanuel/"><i>Maḥberot</i></a>. This site shows the Hebrew and the English side by side, one row for each line.</p>
</header>
<article>
<h2>Gates</h2>
<div class="tablewrap">
<table>
<tr><th>Gate</th><th>Subject</th><th>Status</th></tr>
{rows}
</table>
</div>
<a class="cta" href="gate-{first:02d}.html">Read the {e(GATES[first][0])}, side by side →</a>
<p><b><a href="background.html">Background for the reader</a></b>: al-Ḥarizi's life and travels, what a maqama is, the
biblical inlay (<i>shibbutz</i>), how the fifty gates are built, the world of the book, the editions, and how to read
this one, with a list of further reading.</p>

<h2>Method</h2>
<ul>
<li><b>Lines.</b> The Hebrew edition ends each rhyme unit of the rhymed prose with a full stop. Each unit is one row. Each line of verse is one row, with its two halves set apart.</li>
<li><b>Prose.</b> The English is cadenced prose. Rhyme is kept only where English gives it without added words.</li>
<li><b>Poems.</b> The English is literal, line for line. It does not keep the meter or the rhyme.</li>
<li><b>Allusions.</b> Al-Ḥarizi builds his sentences from biblical phrases. References in gray brackets identify them. They are the translator's identifications and are not yet checked against a concordance.</li>
<li><b>Uncertain renderings</b> have the mark ⚠ and a note at the end of the page.</li>
<li><b>Translator.</b> The translation is by Claude (Anthropic), directed and reviewed by Ezra Brand.</li>
</ul>

<h2>The Hebrew text</h2>
<div class="tablewrap">
<table>
<tr><th>Source</th><th>Contents</th><th>Notes</th></tr>
<tr><td><a href="https://benyehuda.org/author/86">Project Ben-Yehuda</a></td><td>The introduction and 49 of the 50 gates, one text for each (gate 35 is not there; gates 5, 21 and 23 stop before their end)</td><td>Vocalized. In the project's <a href="https://github.com/projectbenyehuda/public_domain_dump">public-domain dump</a> (folder <code>txt/p86/</code>). Most gates name the edition published by Maḥbarot le-Sifrut with Mosad ha-Rav Kook, Tel Aviv. This is the text used here.</td></tr>
<tr><td><a href="https://archive.org/details/tahkemoni00hari">Lagarde, Göttingen 1883</a></td><td>Scan of P. de Lagarde's edition (400 ppi)</td><td>For a check of readings.</td></tr>
<tr><td><a href="https://archive.org/details/TachkemoniYehudaAlchariziWarsaw1899">Kaminka, Warsaw 1899</a></td><td>Scan of A. Kaminka's edition with commentary</td><td>The source of gate 35 and of the passages missing from the Ben-Yehuda text (marked on the page), unvocalized. The end of every gate was compared with this edition.</td></tr>
</table>
</div>

<h2>Translations that exist</h2>
<ul>
<li>English: V. E. Reichert, <i>The Taḥkemoni of Judah al-Ḥarizi</i>, 2 vols. (Jerusalem, 1965–73); D. S. Segal, <i>The Book of Taḥkemoni</i> (Littman Library, 2001). Both are in copyright.</li>
<li>German: S. I. Kaempf, the first maqamat (Berlin, 1845), <a href="https://archive.org/details/dieerstenmakamen00juda">scan</a>.</li>
</ul>
<p>So the value here is an open Hebrew text with an open, line-aligned translation, not a first translation. This list can be incomplete.</p>
</article>
</body>
</html>
"""
    (ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
    print("wrote docs/index.html")


def background_page():
    """docs/background.html from BACKGROUND.md (a general background note for readers)."""
    import markdown
    md = (ROOT / "BACKGROUND.md").read_text(encoding="utf-8")
    md = re.sub(r"^# .*\n", "", md, count=1)
    body = markdown.markdown(md, extensions=["extra"])
    page = HEAD.format(title="Background for the reader — al-Ḥarizi, Taḥkemoni") + f"""<header class="chapter">
<nav class="crumb" aria-label="Gates"><span><a href="index.html">All gates</a> · Background</span></nav>
<p class="title-he" lang="he" dir="rtl">ספר תחכמוני</p>
<h1>Background for the reader</h1>
<p class="sub">Judah al-Ḥarizi and his <i>Taḥkemoni</i>: the author, the form, the world of the book, and the editions</p>
</header>
<article class="bgnote">
{body}
</article>
<footer><nav class="crumb foot" aria-label="Gates"><span><a href="index.html">All gates</a></span></nav></footer>
</body>
</html>
"""
    (ROOT / "docs" / "background.html").write_text(page, encoding="utf-8")
    print("wrote docs/background.html")


def main():
    (ROOT / "docs").mkdir(exist_ok=True)
    counts = {k: gate_page(k, *v) for k, v in GATES.items()}
    index_page(counts)
    background_page()


if __name__ == "__main__":
    main()
    # Open Seforim post-build: canonical and social tags, early display script, lang, CSS/JS version stamps
    import subprocess
    tool = ROOT.parent / "openseforim-site" / "tools" / "postbuild.py"
    if tool.exists():
        subprocess.run([sys.executable, str(tool), "tahkemoni", str(ROOT / "docs")], check=False)

import os
import sys
import typing

article_path = "wiki/Tournaments/Countries_that_participated_in_osu!_tournaments"


class Section:
    IDLE = 0
    GENERAL = 1
    OSU = 2
    TAIKO = 3
    CATCH = 4
    MANIA = 5
    WC_OSU = 6
    WC_TAIKO = 7
    WC_CATCH = 8
    WC_MANIA = 9

sections = {
    "### General ranking": Section.GENERAL,
    "### ![][osu!] osu! ranking": Section.OSU,
    "### ![][osu!taiko] osu!taiko ranking": Section.TAIKO,
    "### ![][osu!catch] osu!catch ranking": Section.CATCH,
    "### ![][osu!mania] osu!mania ranking": Section.MANIA,
    "### ![][osu!] osu! World Cup": Section.WC_OSU,
    "### ![][osu!taiko] osu!taiko World Cup": Section.WC_TAIKO,
    "### ![][osu!catch] osu!catch World Cup": Section.WC_CATCH,
    "### ![][osu!mania] osu!mania World Cup": Section.WC_MANIA,
}

tables: typing.Dict[int, typing.List[str]] = {
    Section.GENERAL: [],
    Section.OSU: [],
    Section.TAIKO: [],
    Section.CATCH: [],
    Section.MANIA: [],
    Section.WC_OSU: [],
    Section.WC_TAIKO: [],
    Section.WC_CATCH: [],
    Section.WC_MANIA: [],
}

with open(article_path + "/en.md", 'r', encoding='utf-8') as fd:
    section = Section.IDLE
    for line in fd:
        if line.startswith('#') and line.strip() in sections:
            section = sections[line.strip()]
            continue
        elif section == Section.IDLE:
            continue

        print(line)
        if line.startswith('|'):
            tables[section].append(line)

for table in tables.values():
    print(''.join(table))

#for f in os.listdir(article_path):
#    if not f.endswith(".md") or f.endswith("en.md"):
#        continue
#    
#    for line in 

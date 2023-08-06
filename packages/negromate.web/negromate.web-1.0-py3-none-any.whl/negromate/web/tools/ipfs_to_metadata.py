#!/usr/bin/env python
import json
import subprocess
import re
from collections import defaultdict
from pathlib import Path, PurePath
import os.path

HASH="QmaZTJyA6oBQR2YXck9hAD5yFmak9KQ8Mnq2w3pbm5AKhn"
LINE_RE = b'([\w\d]+) (-|\d+)\s+(.+)$'
IGNORE_FOLDERS = [
    'static/',
    'home/',
]
TARGET_DIR = Path('../bideoak')


def tree():
    return defaultdict(tree)


def get_ipfs_directory_contents(cid):
    dir_contents = subprocess.check_output(['ipfs', 'ls', cid]).split(b'\n')

    for line in dir_contents:
        match = re.match(LINE_RE, line)
        if match:
            yield (x.decode('utf-8') for x in match.groups())


for entry in get_ipfs_directory_contents(HASH):
    cid, size, name = entry
    if size == '-':
        if name in IGNORE_FOLDERS:
            continue
        else:
            # es una carpeta de cancion
            data = tree()
            jsonfile = TARGET_DIR / name / 'metadata.json'
            for song_entry in get_ipfs_directory_contents(cid):
                cid2, size2, name2 = song_entry
                if size2 == '-':
                    print("Estructura de directorios extraña, no deberia estar")
                
                filename, ext = os.path.splitext(name2)
                if ext == '.srt':
                    data['subtitles']['srt'] = cid2
                if ext == '.vtt':
                    data['subtitles']['vtt'] = cid2
                if ext == '.ass':
                    data['subtitles']['ass'] = cid2
                if ext == '.mp4':
                    data['video']['mp4'] = cid2
                if ext == '.ogm':
                    data['bideo']['ogm'] = cid2
                if name2 == 'metadata.json':
                    # Leer el fichero de ipfs
                    with jsonfile.open('r') as jsonf:
                        jsondata = json.loads(jsonf.read())
                    # cargar el contenido como tree en vez de diccionarios
                    # merge con data
                    data.update(jsondata)

            print("SONG: {}".format(name))
            print(json.dumps(data, indent=4))
            with open(jsonfile, 'w') as jsonf:
                jsonf.write(json.dumps(data, indent=4))

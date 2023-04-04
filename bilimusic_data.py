# BiliMusic Data
# Copyright (C) 2023 cmderli. This program is a free software.
import os
DATA = None      # DO NOT DELETE OR MODIFY THIS LINE.
IS_BUILD = False # DO NOT DELETE OR MODIFY THIS LINE.
# getData(filename, mode) -> str / bytes / None
# Get Data.
# filename: Name of file.
# mode: Read mode.
def getData(filename: str, mode: str):
    if IS_BUILD:
        if filename in DATA:
            return DATA[filename]
        else:
            return None
    else:
        if os.path.exists(filename):
            if mode == 'bytes':
                with open(filename, 'rb') as f:
                    return f.read()
            elif mode == 'str':
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return None
def writeData(dataDict: dict):
    fileData = dict()
    for filename in dataDict:
        file = None
        mode = dataDict[filename]
        if os.path.exists(filename):
            if mode == 'bytes':
                with open(filename, 'rb') as f:
                    file = f.read()
            elif mode == 'str':
                with open(filename, 'r', encoding='utf-8') as f:
                    file = f.read()
        fileData[filename] = file
    data = str()
    with open('bilimusic_data.py', 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.replace("DATA = None", f"DATA = {str(fileData)}", 1)
    data = data.replace("IS_BUILD = False", "IS_BUILD = True", 1)
    with open('bilimusic_data.py', 'w+', encoding='utf-8') as f:
        f.write(data)
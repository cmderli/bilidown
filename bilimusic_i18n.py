# BiliMusic i18n
# Copyright (C) 2023 cmderli. This program is a free software.
import json
import hashlib
import os
import locale
MAGIC_STRING = '6L+Z6YeM5LuA5LmI5Lmf5rKh5pyJ'
I18N_DATA = None # DO NOT DELETE OR MODIFY THIS LINE.
IS_BUILD = False # DO NOT DELETE OR MODIFY THIS LINE.
def readSettings():
    with open('bilimusic.SETTINGS', 'r', encoding='utf-8') as f:
        jsonString = f.read()
        jsonStringList = jsonString.split('\n', 2)
        if len(jsonStringList) != 3:
            badSettingFile = True
            print('ERROR: BAD SETTING FILE.')
            return 1
        if jsonStringList[0] == MAGIC_STRING:
            settingHash = hashlib.sha256(jsonStringList[2].encode('utf-8')).hexdigest()
            if settingHash != jsonStringList[1]:
                badSettingFile = True
                print('ERROR: BAD SETTING FILE.')
                return 1
            else:
                settings = json.loads(jsonStringList[2])
                return settings
def getI18nDict():
    setting = readSettings()
    if setting != 1:
        lang = setting["language"]
    if IS_BUILD:
        i18nFile = I18N_DATA
        i18n = i18nFile[lang]
    else:
        with open(f'i18n/{lang}.json', 'r', encoding='utf-8') as f:
            i18n = json.loads(f.read())
    return i18n
def writeI18n():
    i18n_data = dict()
    for root, dirs, files in os.walk('i18n'):
        for name in files:
            # print(name)
            if name[-5::] == '.json':
                with open(f'i18n/{name}', 'r', encoding='utf-8') as f:
                    i18n_data[name[:-5:]]=json.loads(f.read())
    with open('bilimusic_i18n.py', 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.replace("IS_BUILD = False", "IS_BUILD = True", 1)
    data = data.replace("I18N_DATA = None", f"I18N_DATA = {i18n_data}", 1)
    print(data)
    with open('bilimusic_i18n.py', 'w+', encoding='utf-8') as f:
        f.write(data)
def getI18nListDict():
    lang_dict = dict()
    if IS_BUILD:
        for lang_name in I18N_DATA:
            lang_dict[lang_name] = I18N_DATA[lang_name]["langname"]
    else:
        for root, dirs, files in os.walk('i18n'):
            for name in files:
                if name[-5::] == '.json':
                    with open(f'i18n/{name}', 'r', encoding='utf-8') as f:
                        lang_name = name[:-5:]
                        langflie = json.loads(f.read())
                        langname = langflie["langname"]
                        lang_dict[lang_name] = langname
    return lang_dict
def getI18nList() -> list :
    langname_list = list()
    if IS_BUILD:
        for lang_name in I18N_DATA:
            langname_list.append(lang_name)
    else:
        for root, dirs, files in os.walk('i18n'):
            for name in files:
                if name[-5::] == '.json':
                    langname_list.append(name[:-5:])
    return langname_list
def getI18nCode():
    i18n_code = locale.getdefaultlocale()
    langname_list = getI18nList()
    if i18n_code[0] in langname_list:
        return i18n_code[0]
    else:
        return 'en_US'
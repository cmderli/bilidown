# BiliMusic Build
# Copyright (C) 2023 cmderli. This program is a free software.
DATA = {
    "LICENSE": "str",
    "LICENSE_OTHER_LIBRARY": "str"
}
import os
import shutil
import platform
COPYRIGHT = 'Copyright (C) 2023 cmderli.'
os_name = str(platform.system())
if os_name == 'Windows':
    os_name = 'win32'
else:
    os_name = os_name.lower()
os_arch = platform.machine().lower()
output_name = f'bilimusic_{os_name}_{os_arch}'
print('bilimusic builder')
print(f'platform.system(): {platform.system()}')
print(f'platform.machine(): {platform.machine()}')
print(f'OS Name: {os_name}')
print(f'os.getcwd(): {os.getcwd()}')
print(f'try to build bilimusic...')
shutil.copy('bilimusic_data.py', 'bilimusic_data_back.py')
shutil.copy('bilimusic_i18n.py', 'bilimusic_i18n_back.py')
import bilimusic_data_back, bilimusic_i18n_back
bilimusic_data_back.writeData(DATA)
bilimusic_i18n_back.writeI18n()
if os.system('flet --version') != 0:
    print('flet is not exists. Press Ctrl+C to exit.')
    while True:
        pass
build_command = f'flet pack bilimusic.pyw --product-name bilimusic --copyright "{COPYRIGHT}" --icon bilimusic-app-dark.png --name {output_name}'
# build_command = 'echo 0'
if os.system(build_command) == 0:
    print('Build finished. Cleaning...')
    os.remove('bilimusic_data.py')
    os.remove('bilimusic_i18n.py')
    shutil.copy('bilimusic_data_back.py', 'bilimusic_data.py')
    shutil.copy('bilimusic_i18n_back.py', 'bilimusic_i18n.py')
    os.remove('bilimusic_data_back.py')
    os.remove('bilimusic_i18n_back.py')
else:
    print('Build failed.')
    os.remove('bilimusic_data.py')
    os.remove('bilimusic_i18n.py')
    shutil.copy('bilimusic_data_back.py', 'bilimusic_data.py')
    shutil.copy('bilimusic_i18n_back.py', 'bilimusic_i18n.py')
    os.remove('bilimusic_data_back.py')
    os.remove('bilimusic_i18n_back.py')
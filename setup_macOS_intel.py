"""
Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = ['images/remove.png', './ffmpeg']
OPTIONS = {
    'iconfile': 'images/icon.png',
    'plist':{
        'CFBundleName': 'Swamp Ash MP3 Converter',
        'CFBundleShortVersionString': '1.0.3',
        'CFBundleExecutable': 'Swamp Ash MP3 Converter',
        'CFBundleAuthor': 'Simone De Angelis',
        'CFBundleCopyright': 'Simone De Angelis'
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    author="Simone De Angelis",
    copyright="Simone De Angelis",
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

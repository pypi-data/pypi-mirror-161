__all__ = ['selenium', 'paramiko', 'telegram', 'dropbox', 'util', 'schedule']

__version__ = '0.5.4'

from . import selenium, paramiko, telegram, dropbox, util, schedule

from .util import *

def is_latest_version():
    import feedparser
    feed = feedparser.parse('https://pypi.org/rss/project/scode/releases.xml')
    return __version__ == feed.entries[0]['title']


def update_scode():
    import os
    import subprocess
    os.environ['PATH'] = ';'.join(distinct(os.getenv('PATH').split(';') if os.getenv('PATH') else [] + ["C:\\Python38\\Scripts\\", "C:\\Python38\\", "C:\\Python34\\Scripts\\", "C:\\Python34\\"]))
    subprocess.run(['pip', 'install', '-U', 'scode'])


def refresh():
    import sys
    import importlib
    importlib.reload(sys.modules[__name__])

try:
    is_outdated = not is_latest_version()
except Exception as e:
    import warnings
    warnings.warn(f"{type(e).__name__}: Skipped auto update sequence because error occurred while checking the version", Warning)
else:
    if is_outdated:

        try:
            update_scode()
        except Exception as e:
            import warnings
            warnings.warn(f"{type(e).__name__}: Skipped auto update sequence because error occurred while updating", Warning)
        else:
            refresh()

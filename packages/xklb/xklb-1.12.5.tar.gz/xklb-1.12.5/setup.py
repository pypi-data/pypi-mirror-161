# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xklb']

package_data = \
{'': ['*']}

install_requires = \
['catt>=0.12.9,<0.13.0',
 'humanize>=4.2.3,<5.0.0',
 'ipython>=8.4.0,<9.0.0',
 'joblib>=1.1.0,<2.0.0',
 'mutagen>=1.45.1,<2.0.0',
 'natsort>=8.1.0,<9.0.0',
 'pandas>=1.4.3,<2.0.0',
 'protobuf<4',
 'rich>=12.5.1,<13.0.0',
 'sqlite-utils>=3.28,<4.0',
 'subliminal>=2.1.0,<3.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'tinytag>=1.8.1,<2.0.0',
 'trash-cli>=0.22.4,<0.23.0']

entry_points = \
{'console_scripts': ['lb-extract = xklb.extract:main',
                     'lt = xklb.listen:main',
                     'wt = xklb.watch:main']}

setup_kwargs = {
    'name': 'xklb',
    'version': '1.12.5',
    'description': 'xk media library',
    'long_description': "## lb: opinionated media library\n\nRequires ffmpeg, mpv\n\n!!! You should be warned that the default action after watching a video is to trash it. Restore via your [trash can](https://specifications.freedesktop.org/trash-spec/trashspec-latest.html). Use `--keep` to ask y/n.\n\n### Install\n\n```\npip install xklb\n```\n\n### Step 1. Extract Metadata\n\n    lb-extract tv.db ./video/folder/\n\n    lb-extract --audio podcasts.db ./your/music/or/podcasts/folder/\n\n### Step 2. Watch / Listen\n\n    wt tv.db\n\n    lt podcasts.db\n\n### Repeat!\n\nImplementing repeat / auto-play is left to the end user. I recommend something like this if you use fish shell:\n\n```fish\nfunction repeat\n    while $argv\n        and :\n    end\nend\n\nrepeat lt audio.db\n```\n\nor\n\n```fish\nfunction repeatn --description 'repeatn <count> <command>'\n    for i in (seq 1 $argv[1])\n        eval $argv[2..-1]\n    end\nend\n\nrepeat 5 lt audio.db\n```\n\n#### Watch longest videos\n\n    wt tv.db --sort 'duration desc'\n\n#### Watch specific video series in order\n\n    wt tv.db --search 'title of series' --play-in-order\n\n#### There are multiple strictness levels of --play-in-order. If things aren't playing in order try adding more `O`s:\n\n    wt tv.db --search 'title of series' -O    # default\n    wt tv.db --search 'title of series' -OO   # slower, more complex algorithm\n    wt tv.db --search 'title of series' -OOO  # most strict\n\n#### I usually use the following:\n\n    lt -cast -s '  ost'      # for listening to OSTs on my chromecast groups\n    wt -u priority -w sub=0  # for exercising and watching YouTube\n    wt -u duration --print -s 'video title'  # when I want to check if I've downloaded something before\n\n#### Watch Options\n\n    wt -h\n\n    usage: watch.py [-h] [-1] [-cast-to CHROMECAST_DEVICE] [-cast] [-f] [-d DURATION]\n                    [-dM MAX_DURATION] [-dm MIN_DURATION] [-keep] [-list] [-filename]\n                    [-printquery] [-mv MOVE] [-O] [-r] [-s SEARCH] [-E EXCLUDE] [-S SKIP]\n                    [-t TIME_LIMIT] [-v] [-vlc] [-z SIZE] [-zM MAX_SIZE] [-zm MIN_SIZE]\n                    db\n\n    positional arguments:\n    db\n\n    options:\n    -h, --help            show this help message and exit\n    -1, --last\n    -cast-to CHROMECAST_DEVICE, --chromecast-device CHROMECAST_DEVICE\n    -cast, --chromecast\n    -f, --force-transcode\n    -d DURATION, --duration DURATION\n    -dM MAX_DURATION, --max-duration MAX_DURATION\n    -dm MIN_DURATION, --min-duration MIN_DURATION\n    -keep, --keep\n    -list, --list\n    -filename, --filename\n    -printquery, --printquery\n    -mv MOVE, --move MOVE\n    -O, --play-in-order\n    -r, --random\n    -s SEARCH, --search SEARCH\n    -E EXCLUDE, --exclude EXCLUDE\n    -S SKIP, --skip SKIP\n    -t TIME_LIMIT, --time-limit TIME_LIMIT\n    -v, --verbose\n    -vlc, --vlc\n    -z SIZE, --size SIZE\n    -zM MAX_SIZE, --max-size MAX_SIZE\n    -zm MIN_SIZE, --min-size MIN_SIZE\n\n#### Listen Options\n\n    lt -h\n\n    usage: listen.py [-h] [-cast] [-cast-to CHROMECAST_DEVICE] [-s SEARCH] [-E EXCLUDE]\n                    [-S SKIP] [-d DURATION] [-dm MIN_DURATION] [-dM MAX_DURATION]\n                    [-sz SIZE] [-szm MIN_SIZE] [-szM MAX_SIZE] [-mv MOVE] [-wl] [-O]\n                    [-r] [-v]\n                    db\n\n    positional arguments:\n    db\n\n    options:\n    -h, --help            show this help message and exit\n    -cast, --chromecast\n    -cast-to CHROMECAST_DEVICE, --chromecast-device CHROMECAST_DEVICE\n    -s SEARCH, --search SEARCH\n    -E EXCLUDE, --exclude EXCLUDE\n    -S SKIP, --skip SKIP\n    -d DURATION, --duration DURATION\n    -dm MIN_DURATION, --min-duration MIN_DURATION\n    -dM MAX_DURATION, --max-duration MAX_DURATION\n    -sz SIZE, --size SIZE\n    -szm MIN_SIZE, --min-size MIN_SIZE\n    -szM MAX_SIZE, --max-size MAX_SIZE\n    -mv MOVE, --move MOVE\n    -wl, --with-local\n    -O, --play-in-order\n    -r, --random\n    -v, --verbose\n",
    'author': 'Jacob Chapman',
    'author_email': '7908073+chapmanjacobd@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

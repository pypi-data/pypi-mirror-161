# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""kurek - main script

Parse command line arguments and prepare the operation.
"""

import asyncio
import argparse

from kurek import config
from kurek.http import Session
from kurek.downloaders import ProfileDownloader


async def main(args):
    """Main coroutine
    """

    # consolidate profile names
    file_nicks = []
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as file:
            file_nicks = file.read().splitlines()

    nicks = sorted([*args.profiles, *file_nicks],
                   key=lambda s: s.lower())
    photos = not args.only_videos
    videos = not args.only_photos

    email, password = args.email, args.password

    session = Session(config.request_headers)
    downloader = ProfileDownloader(nicks)

    await session.start()

    await session.login(email, password)
    await downloader.download(session,
                              photos,
                              videos,
                              args.download_limit,
                              args.api_limit)
    await session.close()


def parse():
    """Parse command line arguments

    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
    oooo    oooo ooooo     ooo ooooooooo.   oooooooooooo oooo    oooo
    `888   .8P'  `888'     `8' `888   `Y88. `888'     `8 `888   .8P'
    888  d8'     888       8   888   .d88'  888          888  d8'
    88888[       888       8   888ooo88P'   888oooo8     88888[
    888`88b.     888       8   888`88b.     888    "     888`88b.
    888  `88b.   `88.    .8'   888  `88b.   888       o  888  `88b.
    o888o  o888o    `YbodP'    o888o  o888o o888ooooood8 o888o  o888o

Batch media downloader for zbiornik.com

This script is used to download photos and videos of profiles registered on
zbiornik.com.
It uses libraries based on *asyncio* to rapidly download data - tasks are run
concurrently so that saving massive amounts of data is very fast.
A registered account on the site is required. Media quality is based on account
status. Only the highest fidelity.
        """,
        epilog="""
Use responsibly! Use download and API limits. Live and let live.
        """
    )

    parser.add_argument('-u',
                        '--email',
                        type=str,
                        metavar='EMAIL',
                        required=True,
                        help='login email')
    parser.add_argument('-p',
                        '--pass',
                        dest='password',
                        type=str,
                        metavar='PASSWORD',
                        required=True,
                        help='login password')
    parser.add_argument('-f',
                        '--file',
                        type=str,
                        metavar='FILE',
                        help='file with a list of profile names (1 name/line)')
    exclude_media = parser.add_mutually_exclusive_group()
    exclude_media.add_argument('-g',
                               '--gallery',
                               dest='only_photos',
                               action='store_true',
                               help='download photos only')
    exclude_media.add_argument('-v',
                               '--videos',
                               dest='only_videos',
                               action='store_true',
                               help='download videos only')
    parser.add_argument('-d',
                        '--root-dir',
                        type=str,
                        default=config.root_dir,
                        metavar='DIR',
                        help='base folder to save data to')
    parser.add_argument('-t',
                        '--path-template',
                        type=str,
                        default=config.path_template,
                        metavar='STR',
                        help="""save path template:
    %%d - base directory
    %%p - profile name
    %%t - file type (photo/video)
""")
    parser.add_argument('-n',
                        '--name-template',
                        type=str,
                        default=config.name_template,
                        metavar='STR',
                        help="""name template for files:
    %%t - title
    %%h - unique hash ID
    %%e - file extension
    %%o - owner's profile name
    %%d - description

    Empty strings are replaced with '_'.
""")
    parser.add_argument('-a',
                        '--api-limit',
                        type=int,
                        default=config.max_api_requests,
                        metavar='INT',
                        help='API requests limit')
    parser.add_argument('-l',
                        '--download-limit',
                        type=int,
                        default=config.max_downloads,
                        metavar='INT',
                        help='simultaneous downloads limit')
    parser.add_argument('profiles',
                        nargs='*',
                        type=str,
                        metavar='PROFILE',
                        help='list of profile names')

    args = parser.parse_args()
    if not args.profiles and not args.file:
        parser.error('no profile names given')

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as file:
            file_nicks = file.read().splitlines()
            if not file_nicks:
                parser.error(f'file {args.file} is empty')

    # TODO: handle this better - use only args, remove config
    if args.root_dir:
        config.root_dir = args.root_dir
    if args.path_template:
        config.path_template = args.path_template
    if args.name_template:
        config.name_template = args.name_template

    return args


def run(args):
    """Main entry point
    """

    asyncio.run(main(args))


if __name__ == '__main__':
    arguments = parse()
    run(arguments)

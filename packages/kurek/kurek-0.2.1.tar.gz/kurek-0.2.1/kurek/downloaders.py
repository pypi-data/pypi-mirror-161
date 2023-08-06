# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""A variety of downloader classes

Downloader classes take in profile data or top list data and then start
the downloads concurrently.
"""

import os
import sys
import asyncio

from kurek import json
from kurek.http import Session
from kurek.utils import ItemProperties


class ProfileDownloader:
    """Downloads media from a collection of profiles
    """

    def __init__(self, nicks):
        """Create a new downloader

        Args:
            nicks (Iterable): a list of profile names
        """

        self._nicks = nicks
        self._api_limiter = None
        self._download_limiter = None
        self._download_ids = None

    async def download(self,
                       session: Session,
                       photos=True,
                       videos=True,
                       download_limit=sys.maxsize,
                       request_limit=sys.maxsize):
        """Start downloading data

        Args:
            session (Session): http session
            photos (bool, optional): download photos. Defaults to True.
            videos (bool, optional): download videos. Defaults to True.
            download_limit (int, optional): max downloads.
                Defaults to sys.maxsize.
            request_limit (int, optional): max api requests.
                Defaults to sys.maxsize.
        """

        self._api_limiter = asyncio.Semaphore(request_limit)
        self._download_limiter = asyncio.Semaphore(download_limit)
        self._download_ids = asyncio.Queue()

        for i in range(0, download_limit):
            self._download_ids.put_nowait(i)

        profiles = (json.Profile(nick) for nick in self._nicks)

        albums = set()
        for profile in profiles:
            if photos:
                albums.add(profile.photos)
            if videos:
                albums.add(profile.videos)
        album_tasks = set()
        for album in albums:
            task = asyncio.create_task(self._album_task(session, album))
            task.add_done_callback(album_tasks.discard)
            album_tasks.add(task)
        await asyncio.gather(*album_tasks)

    async def _album_task(self, session, album):
        async with self._api_limiter:
            await album.fetch(session)
        item_tasks = set()
        for item in album.items:
            task = asyncio.create_task(self._download_task(item, session))
            task.add_done_callback(item_tasks.discard)
            item_tasks.add(task)
        await asyncio.gather(*item_tasks)

    async def _download_task(self, item: json.Item, session: Session):
        if item.item_type == 'video':
            async with self._api_limiter:
                await item.fetch(session)
        path = ItemProperties(item).full_path
        if os.path.exists(path):
            return

        async with self._download_limiter:
            position = await self._download_ids.get()
            await session.download(item.url, path, position)
            await self._download_ids.put(position)

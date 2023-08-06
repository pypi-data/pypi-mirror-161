# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing session, connection and user information

Main focus should be put on Session class. The rest of them are basically
helper classes to deal with session parameters.
"""

import os

import aiofiles
from yarl import URL
from tqdm import tqdm
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from kurek import config
from kurek.ajax import Ajax


class User:
    """User information and login status

    Helper class for holding user information.
    """

    def __init__(self, email, password):
        """Create a new User with credentials

        Args:
            email (str): user's email
            password (str): user's password
        """

        self.email = email
        self.password = password
        self.nick = None
        self.token = None


    def login(self, nick, token):
        """Use token and nick to identify the user session

        Args:
            nick (str): user's profile name
            token (str): user's session token
        """

        self.token = token
        self.nick = nick


class Site:
    """Main site operations

    Used mainly to parse html and obtain the login token.
    """

    def __init__(self, client: ClientSession):
        """Create a new Site handler object

        Args:
            client (ClientSession): client for async http requests
        """

        self.url = str(URL.build(scheme=config.scheme,
                                 host=config.host))
        self.client = client

    async def _get_html_text(self):
        async with self.client.get(self.url) as response:
            response.raise_for_status()
            html = await response.text()
        return html

    async def get_tag_property_by_id(self, tag_id, field='value'):
        """Get value of a field from a tag represented by id

        Args:
            tag_id (str): html id of the tag
            field (str, optional): field name. Defaults to 'value'.

        Returns:
            str: tag field value
        """

        soup = BeautifulSoup(await self._get_html_text(), 'html.parser')
        return soup.find(id=tag_id)[field]


class Session:
    """Session interface for HTTP/AJAX API requests

    Use this class to execute AJAX commands and make GET requests.
    Also used for downloading files.
    """

    def __init__(self, headers=None):
        """Create a new HTTP session

        Args:
            headers (dict, optional): dict with HTML headers. Defaults to None.
        """

        self.headers = headers
        self.user: User = None
        self.ajax: Ajax = None
        self.client: ClientSession = None

    async def json(self, url):
        """Make GET request to get JSON data

        Args:
            url (str): request URL

        Returns:
            dict: response JSON object
        """

        async with self.client.get(url) as response:
            response.raise_for_status()
            json = await response.json(content_type=None)
        return json

    async def download(self, url, path, download_no):
        """Download data and save to file

        Args:
            url (str): request URL
            path (path): file to save to
        """

        bar_fmt = '{rate_fmt:>10}|{n_fmt:>6}/{total_fmt:<6}|' \
                  '{bar:30}|{percentage:3.0f}%|{desc:<150}'
        async with self.client.get(url) as response:
            response.raise_for_status()
            total = response.content_length
            save_dir = os.path.dirname(path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            async with aiofiles.open(path, 'wb') as file:
                with tqdm(desc=path,
                          unit='B',
                          unit_scale=True,
                          dynamic_ncols=True,
                          bar_format=bar_fmt,
                          position=download_no,
                          colour='green',
                          total=total) as progress:
                    async for data, _ in response.content.iter_chunks():
                        byte_count = await file.write(data)
                        progress.update(byte_count)

    async def start(self):
        """Start the session and initialize synchronization primitives

        """

        self.client = ClientSession(headers=self.headers)

    async def close(self):
        """Close the session and do cleanup

        """

        await self.client.close()

    async def login(self, email, password):
        """Log the user in using credentials

        Args:
            email (str): account email
            password (str): account password
        """

        user = User(email, password)
        site = Site(self.client)
        ltoken = await site.get_tag_property_by_id('zbiornik-ltoken')
        self.ajax = Ajax(ltoken)
        url = self.ajax.login(user.email, user.password)
        json = await self.json(url)
        token = json['token']
        nick = json['loggedUser']['nick']
        user.login(nick, token)
        self.ajax.token = token
        self.user = user

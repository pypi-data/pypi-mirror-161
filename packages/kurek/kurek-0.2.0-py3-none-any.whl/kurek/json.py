# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Classes representing JSON objects

These classes make use of the JSON representation and add different properties
and methods to ease data fetching.
"""

from kurek.http import Session


class ItemInfo:
    """Additional information about Items

    Wrapper for JSON response from *GetItemInfo* AJAX command.
    Each ItemInfo is identified by 3 things:
        * the type of an Item ('photo'/'video')
        * the 'data' hash from Item's json['data']
        * the 'lData' hash from Item's json['lData']
    """

    def __init__(self, item_type, data, ldata):
        """Create a new ItemInfo object

        Args:
            item_type (str): type of item ('photo'/'video')
            data (str): hash from parent JSON Item -> json['data']
            ldata (str): hash from parent JSON Item -> json['lData']
        """

        self.json = None

        self._data = data
        self._ldata = ldata
        self._type = item_type

    async def fetch(self, session: Session):
        """Fetch JSON data using HTTP session

        Args:
            session (Session): HTTP request session object
        """

        url = session.ajax.get_item_info(self._type, self._data, self._ldata)
        json = await session.json(url)
        self.json = json['item']


class Item:
    """Information about an Item

    Wrapper for a single element of JSON response from AJAX commands:
        * GetProfilePhotos
        * GetProfileVideos

    Basic information is held in the *json* member.
    More fields can be obtained with *info* member.
    """

    def __init__(self, json):
        self.json = json
        data, ldata = json['data'], json['lData']
        if any((key.startswith('src') for key, _ in self.json.items())):
            self.item_type = 'photo'
        else:
            self.item_type = 'video'
        self.info = ItemInfo(self.item_type, data, ldata)

    @property
    def url(self):
        if self.item_type == 'photo':
            src_keys = {key: key
                        for key in self.json if key.startswith('src')}
            size2key = {int("".join(c for c in value if c.isdecimal())): key
                        for key, value in src_keys.items()}
            sorted_sizes = sorted(list(size2key.keys()), reverse=True)
            key = size2key[sorted_sizes[0]]
            url = self.json[key]
        else:
            key = 'mp4480' if 'mp4480' in self.info.json else 'mp4'
            url = self.info.json[key]
        return url


    async def fetch(self, session: Session):
        """Fetch object's ItemInfo JSON data using HTTP session

        Args:
            session (Session): HTTP request session object
        """

        await self.info.fetch(session)


class ProfilePhotos:
    """Collection of Photo Items

    Wrapper for JSON response from *GetProfilePhotos* AJAX command.
    It is identified only by the profile's name.
    """

    def __init__(self, owner):
        """Create a collection of profile photos

        Args:
            owner (str): profile name
        """

        self.owner = owner
        self.json = None
        self.items = None

    async def fetch(self, session: Session):
        """Fetch collection JSON data

        Args:
            session (Session): HTTP request session object
        """
        url = session.ajax.get_profile_photos(self.owner)
        json = await session.json(url)
        self.json = json['items']
        self.items = [Item(item) for item in json['items'] if item['access']]


class ProfileVideos:
    """Collection of Video Items

    Wrapper for JSON response from *GetProfileVideos* AJAX command.
    It is identified only by the profile's name.
    """

    def __init__(self, owner):
        """Create a collection of profile videos

        Args:
            owner (str): profile name
        """

        self.owner = owner
        self.json = None
        self.items = None

    async def fetch(self, session: Session):
        """Fetch collection JSON data

        Args:
            session (Session): HTTP request session object
        """

        url = session.ajax.get_profile_videos(self.owner)
        json = await session.json(url)
        self.json = json['items']
        self.items = [Item(item) for item in json['items'] if item['access']]


class Profile:
    """Information about a profile

    Wrapper for JSON response from *GetProfile* AJAX command.
    A profile is identified by a nick.
    """

    def __init__(self, nick):
        """Create a new Profile object

        Args:
            nick (str): profile name
        """

        self.nick = nick
        self.photos = ProfilePhotos(self.nick)
        self.videos = ProfileVideos(self.nick)
        self.json = None

    async def fetch(self, session: Session):
        """Fetch collection JSON data

        Args:
            session (Session): HTTP request session object
        """

        url = session.ajax.get_profile(self.nick)
        json = await session.json(url)
        self.json = json['profile']

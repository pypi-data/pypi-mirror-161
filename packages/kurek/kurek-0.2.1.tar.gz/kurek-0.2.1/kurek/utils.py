# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""A collection of utility classes.

Helper classes useful in other modules.
"""

import os

from yarl import URL

from kurek import config


class ItemProperties:
    """Computed properties for JSON Items"""

    def __init__(self, item):
        """Create new ItemProperties object"""

        self.item = item

    @property
    def owner(self):
        """Item owner's nick """

        return self.item.json['nick']

    @property
    def description(self):
        """Description string """

        return self.item.json['description']

    @property
    def title(self):
        """Title string """

        return self.item.json['title']

    @property
    def uid(self):
        """Unique data hash"""

        return self.item.json['lData']

    @property
    def ext(self):
        """File extension"""
        return URL(self.item.url).parts[-1][-3:]

    @property
    def filename(self):
        """File name used for saving the file - based on configured template"""

        template = config.name_template
        subs = {
            '%t': self.title,
            '%h': self.uid,
            '%e': self.ext,
            '%d': self.description,
            '%o': self.owner
        }
        for key, value in subs.items():
            if not value:
                value = '_'
            template = template.replace(key, value)
        return template

    @property
    def save_path(self):
        """Directory path where the file will be saved """

        template = config.path_template
        return template.replace('%d', config.root_dir) \
                       .replace('%t', self.item.item_type) \
                       .replace('%p', self.owner)

    @property
    def full_path(self):
        """Save path and filename combined"""

        return os.path.join(self.save_path, self.filename)

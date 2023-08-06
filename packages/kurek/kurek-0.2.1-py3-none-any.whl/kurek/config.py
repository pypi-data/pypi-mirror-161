# Copyright (C) Bartosz Bartyzel 2022
# Distributed under the MIT License.
# License terms are at https://opensource.org/licenses/MIT and in LICENSE.md
"""Config module for holding script settings

This module holds all the information needed to configure the download
process.
"""

import os


host = 'zbiornik.com'
scheme = 'https'
api_servers = ('dzesika', 'brajanek', 'vaneska', 'denisek')
api_root = '/ajax/'
request_headers = {
    'User-Agent': 'Mozilla/5.0',
}
max_server_requests = 5
max_downloads = 5
max_api_requests = 50
root_dir = 'profiles'
path_template = os.path.join('%d', '%p', '%t')
name_template = '%t-%h.%e'

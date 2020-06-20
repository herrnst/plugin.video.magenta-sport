# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""General plugin utils"""

from __future__ import unicode_literals
import platform
import hashlib
import urllib
import json
import xbmc
import xbmcaddon

try:
    import urllib.parse as urllib
except:
    import urllib


class Utils(object):
    """General plugin utils"""


    def __init__(self, kodi_base_url, constants):
        """
        Injects instances & the plugin handle

        :param kodi_base_url: Plugin base url
        :type kodi_base_url: string
        :param constants: Constants instance
        :type constants: resources.lib.Constants
        """
        self.constants = constants
        self.kodi_base_url = kodi_base_url


    def get_addon_data(self):
        """
        Returns the relevant addon data for the plugin,
        e.g. name, version, default fanart, base data path & cookie pathname

        :returns:  dict - Addon data
        """
        addon = self.get_addon()
        base_data_path = xbmc.translatePath(addon.getAddonInfo('profile'))
        return dict(
            plugin=addon.getAddonInfo('name'),
            version=addon.getAddonInfo('version'),
            fanart=addon.getAddonInfo('fanart'),
            base_data_path=base_data_path,
            cookie_path='{0}COOKIE'.format(base_data_path))


    def log(self, msg, level=xbmc.LOGNOTICE):
        """
        Logs a message to the Kodi log (default debug)

        :param msg: Message to be logged
        :type msg: mixed
        :param level: Log level
        :type level: int
        """
        addon_data = self.get_addon_data()
        xbmc.log('[{0}] {1}'.format(addon_data.get('plugin'), msg), level)


    def get_local_string(self, string_id):
        """
        Fetches a translated string from the po files

        :param string_id: Id of the string to be translated
        :type string_id: int
        :returns:  string - Translated string
        """
        src = xbmc if string_id < 30000 else self.get_addon()
        return src.getLocalizedString(string_id)


    def build_url(self, query):
        """
        Generates an URL for internal plugin navigation

        :param query: Map of request params
        :type query: dict
        :returns:  string - Url
        """
        return '{0}?{1}'.format(self.kodi_base_url, urllib.urlencode(query))


    def get_addon(self):
        """
        Returns an Kodi addon instance

        :returns:  xbmcaddon.Addon - Addon instance
        """
        return xbmcaddon.Addon(self.constants.get_addon_id())


    @classmethod
    def generate_hash(cls, text):
        """
        Returns an hash for a given text

        :param text: String to be hashed
        :type text: string
        :returns:  string - Hash
        """
        return hashlib.sha224(text).hexdigest()


    @classmethod
    def capitalize(cls, sentence):
        """
        Capitalizes a sentence

        :param sentence: String to be capitalized
        :type sentence: string
        :returns:  string - Capitalized sentence
        """
        cap = ''
        words = sentence.split(' ')
        i = 0
        for word in words:
            if i > 0:
                cap = '{0} '.format(cap)
            cap = '{0}{1}{2}'.format(cap, word[:1].upper(), word[1:].lower())
            i += 1
        return cap


    @classmethod
    def get_kodi_version(cls):
        """
        Retrieves the Kodi version (Defaults to 18)

        :returns:  string - Kodi version
        """
        version = 18
        payload = {
            'jsonrpc': '2.0',
            'method': 'Application.GetProperties',
            'params': {
                'properties': ['version', 'name']
            },
            'id': 1
        }
        response = xbmc.executeJSONRPC(json.dumps(payload))
        response_serialized = json.loads(response)
        if 'error' not in response_serialized.keys():
            result = response_serialized.get('result', {})
            version_raw = result.get('version', {})
            version = version_raw.get('major', 18)
        return version


    @classmethod
    def get_inputstream_version(cls):
        """
        Retrieves the Inputsteam version (Defaults to 1.0.0)

        :returns:  string - Inputsteam version
        """
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'Addons.GetAddonDetails',
            'params': {
                'addonid': 'inputstream.adaptive',
                'properties': ['enabled', 'version']
            }
        }
        # execute the request
        response = xbmc.executeJSONRPC(json.dumps(payload))
        response_serialized = json.loads(response)
        if 'error' not in response_serialized.keys():
            result = response_serialized.get('result', {})
            addon = result.get('addon', {})
            if addon.get('enabled', False) is True:
                return addon.get('version', '1.0.0')
        return '1.0.0'


    @classmethod
    def get_user_agent(cls):
        """Determines the user agent string for the current platform

        :returns:  str -- User agent string
        """
        base = 'Mozilla/5.0 {0} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        system = platform.system()
        # Mac OSX
        if system == 'Darwin':
            return base.format('(Macintosh; Intel Mac OS X 10_10_1)')
        # Windows
        if system == 'Windows':
            return base.format('(Windows NT 6.1; WOW64)')
        # ARM based Linux
        if platform.machine().startswith('arm'):
            return base.format('(X11; CrOS armv7l 7647.78.0)')
        # x86 Linux
        return base.format('(X11; Linux x86_64)')

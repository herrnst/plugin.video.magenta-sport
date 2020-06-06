# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""Settings interface for Kodi, includes en-/decryption of credentials"""

from __future__ import unicode_literals
from kodi_six.utils import py2_encode
import base64
import uuid
import time
import xbmc
import pyDes

class Settings(object):
    """Settings interface for Kodi, includes en-/decryption of credentials"""


    def __init__(self, utils, dialogs, constants):
        """
        Injects instances, sets encryption var & addon_id

        :param utils: Utils instance
        :type utils: resources.lib.Utils
        :param dialogs: Dialogs instance
        :type dialogs: resources.lib.Dialogs
        :param constants: Constants instance
        :type constants: resources.lib.Constants
        """
        self.utils = utils
        self.dialogs = dialogs
        self.constants = constants
        self.addon_id = self.constants.get_addon_id()


    def uniq_id(self, delay=1):
        """
        Returns a unique id based on the devices MAC address

        :param delay: Retry delay in sec
        :type delay: int
        :returns:  string -- Unique secret
        """
        mac_addr = self.__get_mac_address(delay=delay)
        if py2_encode(':') in mac_addr and delay == 2:
            return uuid.uuid5(uuid.NAMESPACE_DNS, str(mac_addr)).bytes
        else:
            error_msg = '[{0}] error: failed to get device id ({1})'
            self.utils.log(error_msg.format(self.addon_id, str(mac_addr)))
            self.dialogs.show_storing_credentials_failed()
            return 'UnsafeStaticSecret'


    def encode(self, data):
        """
        Encodes data

        :param data: Data to be encoded
        :type data: str
        :returns:  string -- Encoded data
        """
        key_handle = pyDes.triple_des(
            self.uniq_id(delay=2),
            pyDes.CBC,
            py2_encode("\0\0\0\0\0\0\0\0"),
            padmode=pyDes.PAD_PKCS5)
        encrypted = key_handle.encrypt(
            data=data)
        return base64.b64encode(s=encrypted)


    def decode(self, data):
        """
        Decodes data

        :param data: Data to be decoded
        :type data: str
        :returns:  string -- Decoded data
        """
        if data == '':
            return data

        key_handle = pyDes.triple_des(
            self.uniq_id(delay=2),
            pyDes.CBC,
            py2_encode("\0\0\0\0\0\0\0\0"),
            padmode=pyDes.PAD_PKCS5)
        decrypted = key_handle.decrypt(
            data=base64.b64decode(s=data))
        return decrypted.decode('utf-8')


    def has_credentials(self):
        """
        checks if credentials are set

        :returns:  bool -- Credentials set
        """
        addon = self.utils.get_addon()
        user = addon.getSetting('email')
        password = addon.getSetting('password')
        return user != '' or password != ''


    def set_credentials(self):
        """
        Opens up the email & password dialogs and stores entered credentials

        :returns:  tuple -- Credential pai
        """
        addon = self.utils.get_addon()
        user = self.dialogs.show_email_dialog()
        password = self.dialogs.show_password_dialog()

        _mail = self.encode(user) if user != '' else user
        _password = self.encode(password) if password != '' else password

        addon.setSetting('email', _mail)
        addon.setSetting('password', _password)
        return (user, password)


    def get_credentials(self):
        """
        Returns credentials in clear text

        :returns:  tuple -- Clear text credentials
        """
        addon = self.utils.get_addon()
        user = addon.getSetting('email')
        password = addon.getSetting('password')
        return (self.decode(user), self.decode(password))


    def clear_credentials(self):
        """
        Clears credentials
        """
        user, password = '', ''
        addon = self.utils.get_addon()
        addon.setSetting('email', user)
        addon.setSetting('password', password)
        return (user, password)


    @classmethod
    def __get_mac_address(cls, delay=1):
        """
        Returns the users mac address

        :param delay: retry delay in sec
        :type delay: int
        :returns:  string -- Devices MAC address
        """
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        # hack response busy
        i = 0
        while py2_encode(':') not in mac_addr and i < 3:
            i += 1
            time.sleep(delay)
            mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        return mac_addr
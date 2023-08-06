# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

from abc import ABC, abstractmethod
from typing import Optional, Union, Any, Dict, List

from mkm.types import Wrapper
from mkm.crypto import SymmetricKey
from mkm import ID

from .types import ContentType
from .content import Content
from .envelope import Envelope
from .message import Message
from .secure import SecureMessage
from .factories import Factories


class InstantMessage(Message, ABC):
    """
        Instant Message
        ~~~~~~~~~~~~~~~

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content
            content  : {...}
        }
    """

    @property
    def content(self) -> Content:
        """ message content """
        raise NotImplemented

    """
        Encrypt the Instant Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | content  |      | data     |  1. data = encrypt(content, PW)
            +----------+      | key/keys |  2. key  = encrypt(PW, receiver.PK)
                              +----------+
    """

    @abstractmethod
    def encrypt(self, password: SymmetricKey, members: Optional[List[ID]] = None) -> Optional[SecureMessage]:
        """
        Encrypt message content with password(symmetric key)

        :param password: A symmetric key for encrypting message content
        :param members:  If this is a group message, get all members here
        :return: SecureMessage object
        """
        raise NotImplemented

    #
    #   Factory methods
    #

    @classmethod
    def create(cls, head: Envelope, body: Content):  # -> InstantMessage:
        factory = cls.factory()
        # assert isinstance(factory, InstantMessageFactory), 'instant message factory error: %s' % factory
        return factory.create_instant_message(head=head, body=body)

    @classmethod
    def parse(cls, msg: Any):  # -> InstantMessage:
        if msg is None:
            return None
        elif isinstance(msg, InstantMessage):
            return msg
        info = Wrapper.get_dictionary(msg)
        # assert info is not None, 'instant message error: %s' % msg
        factory = cls.factory()
        # assert isinstance(factory, InstantMessageFactory), 'instant message factory error: %s' % factory
        return factory.parse_instant_message(msg=info)

    @classmethod
    def generate_serial_number(cls, msg_type: Union[int, ContentType], time: float) -> int:
        factory = cls.factory()
        # assert isinstance(factory, InstantMessageFactory), 'instant message factory error: %s' % factory
        return factory.generate_serial_number(msg_type=msg_type, time=time)

    @classmethod
    def factory(cls):  # -> InstantMessageFactory:
        return Factories.instant_message_factory

    @classmethod
    def register(cls, factory):
        Factories.instant_message_factory = factory


class InstantMessageFactory(ABC):

    @abstractmethod
    def generate_serial_number(self, msg_type: Union[int, ContentType], time: float) -> int:
        """
        Generate SN for message content

        :param msg_type: content type
        :param time:     message time
        :return: SN (uint64, serial number as msg id)
        """
        raise NotImplemented

    @abstractmethod
    def create_instant_message(self, head: Envelope, body: Content) -> InstantMessage:
        """
        Create instant message with envelope & content

        :param head: message envelope
        :param body: message content
        :return: InstantMessage
        """
        raise NotImplemented

    @abstractmethod
    def parse_instant_message(self, msg: Dict[str, Any]) -> Optional[InstantMessage]:
        """
        Parse map object to message

        :param msg: message info
        :return: InstantMessage
        """
        raise NotImplemented


class InstantMessageDelegate(ABC):

    """ Encrypt Content """

    @abstractmethod
    def serialize_content(self, content: Content, key: SymmetricKey, msg: InstantMessage) -> bytes:
        """
        1. Serialize 'message.content' to data (JsON / ProtoBuf / ...)

        :param content:  message content
        :param key:      symmetric key
        :param msg:      instant message
        :return:         serialized content data
        """
        raise NotImplemented

    @abstractmethod
    def encrypt_content(self, data: bytes, key: SymmetricKey, msg: InstantMessage) -> bytes:
        """
        2. Encrypt content data to 'message.data' with symmetric key

        :param data:     serialized data of message.content
        :param key:      symmetric key
        :param msg:      instant message
        :return:         encrypted message content data
        """
        raise NotImplemented

    @abstractmethod
    def encode_data(self, data: bytes, msg: InstantMessage) -> str:
        """
        3. Encode 'message.data' to String (Base64)

        :param data:     encrypted content data
        :param msg:      instant message
        :return:         string
        """
        raise NotImplemented

    """ Encrypt Key """

    @abstractmethod
    def serialize_key(self, key: SymmetricKey, msg: InstantMessage) -> Optional[bytes]:
        """
        4. Serialize message key to data (JsON / ProtoBuf / ...)

        :param key:      symmetric key to be encrypted
        :param msg:      instant message
        :return:         serialized key data
        """
        raise NotImplemented

    @abstractmethod
    def encrypt_key(self, data: bytes, receiver: ID, msg: InstantMessage) -> Optional[bytes]:
        """
        5. Encrypt key data to 'message.key' with receiver's public key

        :param data:     serialized data of symmetric key
        :param receiver: receiver ID
        :param msg:      instant message
        :return:         encrypted key data
        """
        raise NotImplemented

    @abstractmethod
    def encode_key(self, data: bytes, msg: InstantMessage) -> str:
        """
        6. Encode 'message.key' to String (Base64)

        :param data:     encrypted key data
        :param msg:      instant message
        :return:         base64 string
        """
        raise NotImplemented

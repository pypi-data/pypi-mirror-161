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
from typing import Optional, Any, Dict

from mkm.types import Wrapper
from mkm import ID, Meta, Visa

from .secure import SecureMessage, SecureMessageDelegate
from .factories import Factories


class ReliableMessage(SecureMessage, ABC):
    """This class is used to sign the SecureMessage
    It contains a 'signature' field which signed with sender's private key

        Instant Message signed by an asymmetric key
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content data and key/keys
            data     : "...",  // base64_encode(symmetric)
            key      : "...",  // base64_encode(asymmetric)
            keys     : {
                "ID1": "key1", // base64_encode(asymmetric)
            },
            //-- signature
            signature: "..."   // base64_encode()
        }
    """

    @property
    def signature(self) -> bytes:
        """ signature for encrypted data of message content """
        raise NotImplemented

    @property
    def meta(self) -> Optional[Meta]:
        """
            Sender's Meta
            ~~~~~~~~~~~~~
            Extends for the first message package of 'Handshake' protocol.
        """
        raise NotImplemented

    @meta.setter
    def meta(self, value: Meta):
        raise NotImplemented

    @property
    def visa(self) -> Optional[Visa]:
        """
            Sender's Visa Document
            ~~~~~~~~~~~~~~~~~~~~~~
            Extends for the first message package of 'Handshake' protocol.
        """
        raise NotImplemented

    @visa.setter
    def visa(self, value: Visa):
        raise NotImplemented

    """
        Verify the Reliable Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |  1. verify(data, signature, sender.PK)
            | key/keys |      | key/keys |
            | signature|      +----------+
            +----------+
    """

    @abstractmethod
    def verify(self) -> Optional[SecureMessage]:
        """
        Verify the message.data with signature

        :return: SecureMessage object if signature matched
        """
        raise NotImplemented

    #
    #   Factory method
    #

    @classmethod
    def parse(cls, msg: Any):  # -> ReliableMessage:
        if msg is None:
            return None
        elif isinstance(msg, ReliableMessage):
            return msg
        info = Wrapper.get_dictionary(msg)
        # assert info is not None, 'reliable message error: %s' % msg
        factory = cls.factory()
        # assert isinstance(factory, ReliableMessageFactory), 'reliable message factory error: %s' % factory
        return factory.parse_reliable_message(msg=info)

    @classmethod
    def factory(cls):  # -> ReliableMessageFactory:
        return Factories.reliable_message_factory

    @classmethod
    def register(cls, factory):
        Factories.reliable_message_factory = factory


class ReliableMessageFactory(ABC):

    @abstractmethod
    def parse_reliable_message(self, msg: Dict[str, Any]) -> Optional[ReliableMessage]:
        """
        Parse map object to message

        :param msg: message info
        :return: ReliableMessage
        """
        raise NotImplemented


class ReliableMessageDelegate(SecureMessageDelegate, ABC):

    @abstractmethod
    def decode_signature(self, signature: str, msg: ReliableMessage) -> Optional[bytes]:
        """
        1. Decode 'message.signature' from String (Base64)

        :param signature: base64 string
        :param msg:       reliable message
        :return:          signature data
        """
        raise NotImplemented

    @abstractmethod
    def verify_data_signature(self, data: bytes, signature: bytes, sender: ID, msg: ReliableMessage) -> bool:
        """
        2. Verify the message data and signature with sender's public key

        :param data:      message content(encrypted) data
        :param signature: signature of message content(encrypted) data
        :param sender:    sender ID
        :param msg:       reliable message
        :return:          True on signature matched
        """
        raise NotImplemented

# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
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

"""
    Messenger
    ~~~~~~~~~

    Transform and send message
"""

from typing import Optional, List

from mkm.crypto import SymmetricKey

from dimp.transceiver import is_broadcast
from dimp import ID
from dimp import Content
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import Transceiver, Packer, Processor

from .delegate import CipherKeyDelegate


class Messenger(Transceiver, CipherKeyDelegate, Packer, Processor):

    @property
    def key_cache(self) -> CipherKeyDelegate:
        """ Delegate for Cipher Key """
        raise NotImplemented

    @property
    def packer(self) -> Packer:
        """ Delegate for Packing Message """
        raise NotImplemented

    @property
    def processor(self) -> Processor:
        """ Delegate for Processing Message """
        raise NotImplemented

    #
    #   Interfaces for Cipher Key
    #

    # Override
    def cipher_key(self, sender: ID, receiver: ID, generate: bool = False) -> Optional[SymmetricKey]:
        delegate = self.key_cache
        return delegate.cipher_key(sender=sender, receiver=receiver, generate=generate)

    # Override
    def cache_cipher_key(self, key: SymmetricKey, sender: ID, receiver: ID):
        delegate = self.key_cache
        return delegate.cache_cipher_key(key=key, sender=sender, receiver=receiver)

    #
    #   Interfaces for Packing Message
    #

    # Override
    def overt_group(self, content: Content) -> Optional[ID]:
        delegate = self.packer
        return delegate.overt_group(content=content)

    # Override
    def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
        delegate = self.packer
        return delegate.encrypt_message(msg=msg)

    # Override
    def sign_message(self, msg: SecureMessage) -> ReliableMessage:
        delegate = self.packer
        return delegate.sign_message(msg=msg)

    # Override
    def serialize_message(self, msg: ReliableMessage) -> bytes:
        delegate = self.packer
        return delegate.serialize_message(msg=msg)

    # Override
    def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
        delegate = self.packer
        return delegate.deserialize_message(data=data)

    # Override
    def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        delegate = self.packer
        return delegate.verify_message(msg=msg)

    # Override
    def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        delegate = self.packer
        return delegate.decrypt_message(msg=msg)

    #
    #   Interfaces for Processing Message
    #

    # Override
    def process_package(self, data: bytes) -> List[bytes]:
        delegate = self.processor
        return delegate.process_package(data=data)

    # Override
    def process_reliable_message(self, msg: ReliableMessage) -> List[ReliableMessage]:
        delegate = self.processor
        return delegate.process_reliable_message(msg=msg)

    # Override
    def process_secure_message(self, msg: SecureMessage, r_msg: ReliableMessage) -> List[SecureMessage]:
        delegate = self.processor
        return delegate.process_secure_message(msg=msg, r_msg=r_msg)

    # Override
    def process_instant_message(self, msg: InstantMessage, r_msg: ReliableMessage) -> List[InstantMessage]:
        delegate = self.processor
        return delegate.process_instant_message(msg=msg, r_msg=r_msg)

    # Override
    def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        delegate = self.processor
        return delegate.process_content(content=content, r_msg=r_msg)

    #
    #   SecureMessageDelegate
    #

    # Override
    def deserialize_key(self, data: Optional[bytes], sender: ID, receiver: ID,
                        msg: SecureMessage) -> Optional[SymmetricKey]:
        if data is None:
            # get key from cache
            return self.cipher_key(sender=sender, receiver=receiver)
        else:
            return super().deserialize_key(data=data, sender=sender, receiver=receiver, msg=msg)

    # Override
    def deserialize_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[Content]:
        content = super().deserialize_content(data=data, key=key, msg=msg)
        assert content is not None, 'content error: %d' % len(data)
        if not is_broadcast(msg=msg):
            # check and cache key for reuse
            group = self.overt_group(content=content)
            if group is None:
                # personal message or (group) command
                # cache key with direction (sender -> receiver)
                self.cache_cipher_key(key=key, sender=msg.sender, receiver=msg.receiver)
            else:
                # group message (excludes group command)
                # cache the key with direction (sender -> group)
                self.cache_cipher_key(key=key, sender=msg.sender, receiver=group)
        # NOTICE: check attachment for File/Image/Audio/Video message content
        #         after deserialize content, this job should be do in subclass
        return content

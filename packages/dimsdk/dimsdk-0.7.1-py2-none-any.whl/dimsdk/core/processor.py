# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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

from typing import List, Union, Optional

from dimp import ContentType, Content, Envelope
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import Processor

from .facebook import Facebook
from .messenger import Messenger
from .helper import TwinsHelper
from .proc_content import ContentProcessor, ContentProcessorFactory, ContentProcessorCreator


class MessageProcessor(TwinsHelper, Processor):

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__factory = self._create_factory()

    # protected
    def _create_factory(self) -> ContentProcessorFactory:
        creator = self._create_creator()
        from ..cpu import GeneralContentProcessorFactory
        return GeneralContentProcessorFactory(facebook=self.facebook, messenger=self.messenger, creator=creator)

    # protected
    def _create_creator(self) -> ContentProcessorCreator:
        from ..cpu import BaseContentProcessorCreator
        return BaseContentProcessorCreator(facebook=self.facebook, messenger=self.messenger)

    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        return self.__factory.get_processor(content=content)

    def get_content_processor(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        return self.__factory.get_content_processor(msg_type=msg_type)

    def get_command_processor(self, cmd_name: str, msg_type: Union[int, ContentType] = 0) -> Optional[ContentProcessor]:
        return self.__factory.get_command_processor(msg_type=msg_type, cmd_name=cmd_name)

    #
    #  Processing Message
    #

    # Override
    def process_package(self, data: bytes) -> List[bytes]:
        messenger = self.messenger
        # 1. deserialize message
        msg = messenger.deserialize_message(data=data)
        if msg is None:
            # no valid message received
            return []
        # 2. process message
        responses = messenger.process_reliable_message(msg=msg)
        if responses is None or len(responses) == 0:
            return []
        # 3. serialize messages
        packages = []
        for res in responses:
            pack = messenger.serialize_message(msg=res)
            if pack is not None:
                packages.append(pack)
        return packages

    # Override
    def process_reliable_message(self, msg: ReliableMessage) -> List[ReliableMessage]:
        # TODO: override to check broadcast message before calling it
        messenger = self.messenger
        # 1. verify message
        s_msg = messenger.verify_message(msg=msg)
        if s_msg is None:
            # waiting for sender's meta if not exists
            return []
        # 2. process message
        responses = messenger.process_secure_message(msg=s_msg, r_msg=msg)
        if responses is None or len(responses) == 0:
            return []
        # 3. sign message
        messages = []
        for res in responses:
            signed = messenger.sign_message(msg=res)
            if signed is not None:
                messages.append(signed)
        return messages
        # TODO: override to deliver to the receiver when catch exception "receiver error ..."

    # Override
    def process_secure_message(self, msg: SecureMessage, r_msg: ReliableMessage) -> List[SecureMessage]:
        messenger = self.messenger
        # 1. decrypt message
        i_msg = messenger.decrypt_message(msg=msg)
        if i_msg is None:
            # cannot decrypt this message, not for you?
            # delivering message to other receiver?
            return []
        # 2. process message
        responses = messenger.process_instant_message(msg=i_msg, r_msg=r_msg)
        if responses is None or len(responses) == 0:
            return []
        # 3. encrypt messages
        messages = []
        for res in responses:
            encrypted = messenger.encrypt_message(msg=res)
            if encrypted is not None:
                messages.append(encrypted)
        return messages

    # Override
    def process_instant_message(self, msg: InstantMessage, r_msg: ReliableMessage) -> List[InstantMessage]:
        messenger = self.messenger
        # 1. process content from sender
        responses = messenger.process_content(content=msg.content, r_msg=r_msg)
        if responses is None or len(responses) == 0:
            # nothing to respond
            return []
        # 2. select a local user to build message
        sender = msg.sender
        receiver = msg.receiver
        facebook = self.facebook
        user = facebook.select_user(receiver=receiver)
        assert user is not None, 'receiver error: %s' % receiver
        me = user.identifier
        # 3. package messages
        messages = []
        for res in responses:
            if res is None:
                # should not happen
                continue
            env = Envelope.create(sender=me, receiver=sender)
            msg = InstantMessage.create(head=env, body=res)
            messages.append(msg)
        return messages

    # Override
    def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        # TODO: override to check group
        cpu = self.get_processor(content=content)
        if cpu is None:
            # default content processor
            cpu = self.get_content_processor(msg_type=0)
            assert cpu is not None, 'default CPU not defined'
        return cpu.process(content=content, msg=r_msg)
        # TODO: override to filter the response

# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2021 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2021 Albert Moky
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
    Processor Factory
    ~~~~~~~~~~~~~~~~~

    produce content/command processors
"""

from typing import Dict, Optional, Union

from dimp import ContentType, Content, Command, GroupCommand

from ..core.helper import TwinsHelper
from ..core import Facebook, Messenger
from ..core import ContentProcessor, ContentProcessorFactory

from .creator import ContentProcessorCreator


class GeneralContentProcessorFactory(TwinsHelper, ContentProcessorFactory):

    def __init__(self, facebook: Facebook, messenger: Messenger, creator: ContentProcessorCreator):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__creator = creator
        self.__content_processors: Dict[int, ContentProcessor] = {}
        self.__command_processors: Dict[str, ContentProcessor] = {}

    @property  # protected
    def creator(self) -> ContentProcessorCreator:
        return self.__creator

    # protected
    def _get_content_processor(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        if isinstance(msg_type, ContentType):
            msg_type = msg_type.value
        return self.__content_processors.get(msg_type)

    # protected
    def _put_content_processor(self, msg_type: Union[int, ContentType], cpu: ContentProcessor):
        if isinstance(msg_type, ContentType):
            msg_type = msg_type.value
        self.__content_processors[msg_type] = cpu

    # protected
    def _get_command_processor(self, cmd_name: str) -> Optional[ContentProcessor]:
        return self.__command_processors.get(cmd_name)

    # protected
    def _put_command_processor(self, cmd_name: str, cpu: ContentProcessor):
        self.__command_processors[cmd_name] = cpu

    #
    #   ContentProcessorFactory
    #

    # Override
    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        msg_type = content.type
        if isinstance(content, Command):
            name = content.cmd
            # command processor
            cpu = self.get_command_processor(msg_type=msg_type, cmd_name=name)
            if cpu is not None:
                return cpu
            elif isinstance(content, GroupCommand):
                # group command processor
                cpu = self.get_command_processor(msg_type=msg_type, cmd_name='group')
                if cpu is not None:
                    return cpu
        # content processor
        return self.get_content_processor(msg_type=msg_type)

    # Override
    def get_content_processor(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        cpu = self._get_content_processor(msg_type=msg_type)
        if cpu is None:
            cpu = self.creator.create_content_processor(msg_type=msg_type)
            if cpu is not None:
                self._put_content_processor(msg_type=msg_type, cpu=cpu)
        return cpu

    # Override
    def get_command_processor(self, msg_type: Union[int, ContentType], cmd_name: str) -> Optional[ContentProcessor]:
        cpu = self._get_command_processor(cmd_name=cmd_name)
        if cpu is None:
            cpu = self.creator.create_command_processor(msg_type=msg_type, cmd_name=cmd_name)
            if cpu is not None:
                self._put_command_processor(cmd_name=cmd_name, cpu=cpu)
        return cpu

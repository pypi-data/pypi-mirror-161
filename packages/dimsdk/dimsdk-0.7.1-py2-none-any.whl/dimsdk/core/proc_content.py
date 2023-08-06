# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2022 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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
from typing import List, Optional, Union

from dimp import Content, ContentType
from dimp import ReliableMessage


class ContentProcessor(ABC):
    """
        CPU: Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        """
        Process message content

        :param content: content received
        :param msg:     reliable message
        :return: responses to sender
        """
        raise NotImplemented


class ContentProcessorFactory(ABC):
    """
        CPU Factory
        ~~~~~~~~~~~

        Delegate for Message Processor
    """

    @abstractmethod
    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        """
        Get content/command processor

        :param content: Content/Command
        :return: ContentProcessor
        """
        raise NotImplemented

    @abstractmethod
    def get_content_processor(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        raise NotImplemented

    @abstractmethod
    def get_command_processor(self, msg_type: Union[int, ContentType], cmd_name: str) -> Optional[ContentProcessor]:
        raise NotImplemented


class ContentProcessorCreator(ABC):
    """
        CPU Creator
        ~~~~~~~~~~~

        Delegate for CPU Factory
    """

    @abstractmethod
    def create_content_processor(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        """
        Create content processor with type

        :param msg_type: content type
        :return ContentProcessor
        """
        raise NotImplemented

    @abstractmethod
    def create_command_processor(self, msg_type: Union[int, ContentType], cmd_name: str) -> Optional[ContentProcessor]:
        """
        Create command processor with name

        :param msg_type: content type
        :param cmd_name: command name
        :return CommandProcessor
        """
        raise NotImplemented

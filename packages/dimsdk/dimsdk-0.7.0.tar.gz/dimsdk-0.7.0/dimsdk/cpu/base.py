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
    Content Processor
    ~~~~~~~~~~~~~~~~~

"""

from typing import Optional, List

from dimp import ID
from dimp import ReliableMessage
from dimp import Content, TextContent, Command

from ..core.helper import TwinsHelper
from ..core import ContentProcessor


class BaseContentProcessor(TwinsHelper, ContentProcessor):
    """
        Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~
    """

    FMT_CONTENT_NOT_SUPPORT = 'Content (type: %s) not support yet!'

    # Override
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        text = self.FMT_CONTENT_NOT_SUPPORT % content.type
        return self._respond_text(text=text, group=content.group)

    # noinspection PyMethodMayBeStatic
    def _respond_text(self, text: str, group: Optional[ID] = None) -> List[Content]:
        res = TextContent.create(text=text)
        if group is not None:
            res.group = group
        return [res]

    # noinspection PyMethodMayBeStatic
    def _respond_content(self, content: Optional[Content]) -> List[Content]:
        if content is None:
            return []
        else:
            return [content]


class BaseCommandProcessor(BaseContentProcessor):
    """
        Command Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~
    """

    FMT_CMD_NOT_SUPPORT = 'Command (name: %s) not support yet!'

    # Override
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, Command), 'command error: %s' % content
        text = self.FMT_CMD_NOT_SUPPORT % content.cmd
        return self._respond_text(text=text, group=content.group)

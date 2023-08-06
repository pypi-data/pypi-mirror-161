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
from typing import List

from dimp import ID
from dimp import ReliableMessage
from dimp import Content, CustomizedContent

from .base import BaseContentProcessor


class CustomizedContentHandler(ABC):
    """
        Handler for Customized Content
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    def handle_action(self, act: str, sender: ID, content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        """
        Do your job

        @param act:     action
        @param sender:  user ID
        @param content: customized content
        @param msg:     network message
        @return contents
        """
        raise NotImplemented


class CustomizedContentProcessor(BaseContentProcessor, CustomizedContentHandler):
    """
        Customized Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    FMT_APP_NOT_SUPPORT = 'Customized Content (app: %s) not support yet!'
    FMT_ACT_NOT_SUPPORT = 'Customized Content (app: %s, mod: %s, act: %s) not support yet!'

    # Override
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, CustomizedContent), 'customized content error: %s' % content
        # 1. check app id
        app = content.application
        responses = self._filter(app=app, content=content, msg=msg)
        if responses is not None:
            # application ID not found
            return responses
        # 2. get handler with module name
        mod = content.module
        handler = self._fetch(mod=mod, content=content, msg=msg)
        if handler is None:
            # module not support
            return []
        # 3. do the job
        act = content.action
        sender = msg.sender
        return handler.handle_action(act=act, sender=sender, content=content, msg=msg)

    # protected
    def _filter(self, app: str, content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        """ Override for your application """
        text = self.FMT_APP_NOT_SUPPORT % app
        return self._respond_text(text=text)

    # protected
    def _fetch(self, mod: str, content: CustomizedContent, msg: ReliableMessage) -> CustomizedContentHandler:
        """ Override for you module """
        # if the application has too many modules, I suggest you to
        # use different handler to do the job for each module.
        return self

    # Override
    def handle_action(self, act: str, sender: ID, content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        """ Override for customized actions """
        app = content.application
        mod = content.module
        text = self.FMT_ACT_NOT_SUPPORT % (app, mod, act)
        return self._respond_text(text=text)

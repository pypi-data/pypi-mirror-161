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
    Meta Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import List

from dimp import ID, Meta
from dimp import ReliableMessage
from dimp import Content
from dimp import MetaCommand

from .base import BaseCommandProcessor


class MetaCommandProcessor(BaseCommandProcessor):

    STR_META_CMD_ERROR = 'Meta command error'
    FMT_META_NOT_FOUND = 'Sorry, meta not found for ID: %s'
    FMT_META_NOT_ACCEPTED = 'Meta not accepted: %s'
    FMT_META_ACCEPTED = 'Meta received: %s'

    def __get_meta(self, identifier: ID) -> List[Content]:
        meta = self.facebook.meta(identifier=identifier)
        if meta is None:
            text = self.FMT_META_NOT_FOUND % identifier
            return self._respond_text(text=text)
        else:
            res = MetaCommand.response(identifier=identifier, meta=meta)
            return [res]

    def __put_meta(self, identifier: ID, meta: Meta) -> List[Content]:
        if not self.facebook.save_meta(meta=meta, identifier=identifier):
            text = self.FMT_META_NOT_ACCEPTED % identifier
            return self._respond_text(text=text)
        else:
            text = self.FMT_META_ACCEPTED % identifier
            return self._respond_text(text=text)

    # Override
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, MetaCommand), 'meta command error: %s' % content
        identifier = content.identifier
        meta = content.meta
        if identifier is None:
            # error
            return self._respond_text(text=self.STR_META_CMD_ERROR)
        elif meta is None:
            # query meta for ID
            return self.__get_meta(identifier=identifier)
        else:
            # received a meta for ID
            return self.__put_meta(identifier=identifier, meta=meta)

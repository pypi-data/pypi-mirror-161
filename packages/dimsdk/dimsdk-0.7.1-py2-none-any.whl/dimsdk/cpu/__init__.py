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
    Content/Command Processing Units
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .creator import BaseContentProcessorCreator
from .factory import GeneralContentProcessorFactory

from .base import BaseContentProcessor, BaseCommandProcessor

from .forward import ForwardContentProcessor
from .array import ArrayContentProcessor
from .customized import CustomizedContentProcessor, CustomizedContentHandler
from .meta import MetaCommandProcessor
from .document import DocumentCommandProcessor

from .history import HistoryCommandProcessor, GroupCommandProcessor
from .grp_invite import InviteCommandProcessor
from .grp_expel import ExpelCommandProcessor
from .grp_quit import QuitCommandProcessor
from .grp_reset import ResetCommandProcessor
from .grp_query import QueryCommandProcessor


__all__ = [

    'BaseContentProcessorCreator',
    'GeneralContentProcessorFactory',

    'BaseContentProcessor',
    'BaseCommandProcessor',

    'ForwardContentProcessor',
    'ArrayContentProcessor',
    'CustomizedContentProcessor', 'CustomizedContentHandler',
    'MetaCommandProcessor',
    'DocumentCommandProcessor',

    'HistoryCommandProcessor',
    'GroupCommandProcessor',
    'InviteCommandProcessor', 'ExpelCommandProcessor', 'QuitCommandProcessor',
    'ResetCommandProcessor', 'QueryCommandProcessor',
]

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

from dimp.dkd import *
from dimp import ContentType, Content, Command

from .ans import AddressNameService
from .delegate import CipherKeyDelegate
from .helper import TwinsHelper

from .facebook import Facebook
from .messenger import Messenger
from .packer import MessagePacker
from .processor import MessageProcessor
from .proc_content import ContentProcessor, ContentProcessorFactory, ContentProcessorCreator


def register_core_factories():
    # Register core factories
    register_content_factories()
    register_command_factories()

    # Customized contents
    factory = ContentFactoryBuilder(content_class=AppCustomizedContent)
    Content.register(msg_type=ContentType.APPLICATION, factory=factory)
    Content.register(msg_type=ContentType.CUSTOMIZED, factory=factory)

    # Document commands
    factory = CommandFactoryBuilder(command_class=BaseDocumentCommand)
    Command.register(cmd='profile', factory=factory)
    Command.register(cmd='visa', factory=factory)
    Command.register(cmd='bulletin', factory=factory)


__all__ = [

    'AddressNameService',
    'CipherKeyDelegate',
    'TwinsHelper',
    'Facebook', 'Messenger',
    'MessagePacker', 'MessageProcessor',
    'ContentProcessor', 'ContentProcessorFactory', 'ContentProcessorCreator',

    #
    #   DaoKeDao
    #
    'ContentFactoryBuilder', 'CommandFactoryBuilder',
    'GeneralCommandFactory', 'HistoryCommandFactory', 'GroupCommandFactory',
    'register_content_factories', 'register_command_factories',
    'register_core_factories',
]

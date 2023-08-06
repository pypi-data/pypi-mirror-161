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
    Chatroom
    ~~~~~~~~

    Big group with admins
"""

from abc import abstractmethod
from typing import Optional, List

from dimp import ID, NetworkType
from dimp import GroupDataSource
from dimp import BaseGroup


class ChatroomDataSource(GroupDataSource):
    """This interface is for getting information for chatroom

        Chatroom Data Source
        ~~~~~~~~~~~~~~~~~~~~

        Chatroom admins should be set complying with the consensus algorithm
    """

    @abstractmethod
    def admins(self, identifier: ID) -> Optional[List[ID]]:
        """
        Get all admins in the chatroom

        :param identifier: chatroom ID
        :return: admin ID list
        """
        pass


class Chatroom(BaseGroup):

    def __init__(self, identifier: ID):
        super().__init__(identifier=identifier)
        assert identifier.type == NetworkType.CHATROOM, 'Chatroom ID type error: %s' % identifier

    @BaseGroup.data_source.getter  # Override
    def data_source(self) -> Optional[ChatroomDataSource]:
        facebook = super().data_source
        assert facebook is None or isinstance(facebook, ChatroomDataSource), 'error: %s' % facebook
        return facebook

    # @data_source.setter  # Override
    # def data_source(self, value: ChatroomDataSource):
    #     super(Chatroom, Chatroom).data_source.__set__(self, value)

    @property
    def admins(self) -> Optional[List[ID]]:
        delegate = self.data_source
        assert delegate is not None, 'chatroom delegate not set yet'
        return delegate.admins(identifier=self.identifier)

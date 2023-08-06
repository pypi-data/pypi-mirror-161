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
    Forward Content Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import List

from dimp import ReliableMessage
from dimp import Content, ForwardContent

from .base import BaseContentProcessor


#
#   Forward Content Processor
#
class ForwardContentProcessor(BaseContentProcessor):

    # Override
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, ForwardContent), 'forward content error: %s' % content
        # call messenger to process it
        messenger = self.messenger
        secrets = content.secrets
        responses = []
        for item in secrets:
            results = messenger.process_reliable_message(msg=item)
            if results is None:
                res = ForwardContent.create(messages=[])
            elif len(results) == 1:
                res = ForwardContent.create(message=results[0])
            else:
                res = ForwardContent.create(messages=results)
            responses.append(res)
        return responses

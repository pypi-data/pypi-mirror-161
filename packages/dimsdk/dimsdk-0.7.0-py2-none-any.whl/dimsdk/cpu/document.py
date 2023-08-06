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
    Document Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import Optional, List

from dimp import ID, Meta, Document
from dimp import ReliableMessage
from dimp import Content
from dimp import DocumentCommand

from .meta import MetaCommandProcessor


class DocumentCommandProcessor(MetaCommandProcessor):

    STR_DOC_CMD_ERROR = 'Document command error'
    FMT_DOC_NOT_FOUND = 'Sorry, document not found for ID: %s'
    FMT_DOC_NOT_ACCEPTED = 'Document not accept: %s'
    FMT_DOC_ACCEPTED = 'Document received: %s'

    def __get_doc(self, identifier: ID, doc_type: str = '*') -> List[Content]:
        facebook = self.facebook
        doc = facebook.document(identifier=identifier, doc_type=doc_type)
        if doc is None:
            text = self.FMT_DOC_NOT_FOUND % identifier
            return self._respond_text(text=text)
        else:
            meta = facebook.meta(identifier=identifier)
            res = DocumentCommand.response(document=doc, meta=meta, identifier=identifier)
            return [res]

    def __put_doc(self, identifier: ID, meta: Optional[Meta], document: Document) -> List[Content]:
        facebook = self.facebook
        if meta is not None:
            # received a meta for ID
            if not facebook.save_meta(meta=meta, identifier=identifier):
                text = self.FMT_META_NOT_ACCEPTED % identifier
                return self._respond_text(text=text)
        # received a new document for ID
        if not facebook.save_document(document=document):
            text = self.FMT_DOC_NOT_ACCEPTED % identifier
            return self._respond_text(text=text)
        else:
            text = self.FMT_DOC_ACCEPTED % identifier
            return self._respond_text(text=text)

    # Override
    def process(self, content: Content, msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, DocumentCommand), 'document command error: %s' % content
        identifier = content.identifier
        if identifier is not None:
            doc = content.document
            if doc is None:
                # query entity document for ID
                doc_type = content.get('doc_type')
                if doc_type is None:
                    doc_type = '*'  # ANY
                return self.__get_doc(identifier=identifier, doc_type=doc_type)
            elif identifier == doc.identifier:
                # received a new document for ID
                return self.__put_doc(identifier=identifier, meta=content.meta, document=doc)
        # error
        return self._respond_text(text=self.STR_DOC_CMD_ERROR)

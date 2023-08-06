# coding: utf-8

# """
# --------------------------------------------------------------------------------------------------------------------
#  <copyright company="Aspose" file="test_rewriter_api.py">
#    Copyright (c) 2022 GroupDocs.Rewriter Cloud
#  </copyright>
#  <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# --------------------------------------------------------------------------------------------------------------------
# """

from __future__ import absolute_import

import os
import unittest
import sys
sys.path.append('../')
import groupdocsrewritercloud.models
from groupdocsrewritercloud.models import rewrite_text, rewrite_document, document_response, text_response
from groupdocsrewritercloud.rest import ApiException
from test_helper import TestHelper


class TestRewriterApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = TestHelper.paraphrase
        cls.storageApi = TestHelper.storage

    ###############################################################
    #                          Rewriter tests
    ###############################################################

    def test_text_rewriting(self):
        language = "en"
        text = "Welcome to Paris"
        try:
            rewriter = rewrite_text.RewriteText(language, text)
            request = rewriter.to_string()
            response = self.api.post_rewrite_text(request)
            self.assertEqual(response.status, "ok")
        except ApiException as ex:
            print("Exception")
            print("Info: " + str(ex))
            raise ex

    def test_document_rewriting(self):
        language = "en"
        _format = "docx"
        outformat = "docx"
        storage = "First Storage"
        name = "test_python.docx"
        folder = ""
        savepath = ""
        savefile = "paraphrased_test_python.docx"
        try:
            rewriter = rewrite_document.RewriteDocument(language, _format, outformat, storage, name, folder, savepath, savefile)
            request = rewriter.to_string()
            response = self.api.post_rewrite_document(request)
            self.assertEqual(response.status, "ok")
        except ApiException as ex:
            print("Exception")
            print("Info: " + str(ex))
            raise ex            
    


if __name__ == '__main__':
    unittest.main()

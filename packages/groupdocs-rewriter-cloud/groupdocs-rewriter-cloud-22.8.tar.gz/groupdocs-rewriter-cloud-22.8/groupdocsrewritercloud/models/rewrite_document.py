# coding: utf-8
# """Copyright
# --------------------------------------------------------------------------------------------------------------------
# <copyright company="Aspose" file="rewrite_document.py">
# Copyright (c) 2022 GroupDocs.Rewriter Cloud
# </copyright>
# <summary>
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
# </summary>
# --------------------------------------------------------------------------------------------------------------------
# """

"""
Represents information about strict regions to recognize text
"""
import json


class RewriteDocument:
    """
        Attributes:
          model_types (dict):   The key is attribute name
                                and the value is attribute type.
          attribute_map (dict): The key is attribute name
                                and the value is json key in definition.
        """
    model_types = {
        'Language': 'str',
        'Format': 'str',
        'Outformat': 'str',
        'Storage': 'str',
        'Name': 'str',
        'Folder': 'str',
        'Savepath': 'str',
        'Savefile': 'str'
    }

    attribute_map = {
        'Language': 'language',
        'Format': 'format',
        'Outformat': 'outformat',
        'Storage': 'storage',
        'Name': 'name',
        'Folder': 'folder',
        'Savepath': 'savepath',
        'Savefile': 'savefile'
    }

    def __init__(self, language, _format, outformat, storage, name, folder, savepath, savefile):
        """
        :param str Language: language of document
        :param str Format: format of file for rewriting, put file extension here
        :param str Outformat: format of paraphrased file, put file extension of desired format here
        :param str Storage: name of storage
        :param str Name: name of file to rewrite
        :param str Folder: folder(s) where file is saved
        :param str Savepath: folder(s) for paraphrased file
        :param str Savefile: name of paraphrased file
        """
        self.Language = language
        self.Format = _format
        self.Outformat = outformat
        self.Storage = storage
        self.Name = name
        self.Folder = folder
        self.Savepath = savepath
        self.Savefile = savefile

    def to_string(self):
        request = [{"language": self.Language, "format": self.Format, "outformat": self.Outformat, "storage": self.Storage,
                    "name": self.Name, "folder": self.Folder, "savepath": self.Savepath, "savefile": self.Savefile}]
        return  json.dumps(request)

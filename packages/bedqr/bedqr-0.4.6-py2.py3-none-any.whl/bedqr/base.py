# -*- python -*-
#
# Copyright 2022 Cecelia Chen
# Copyright 2018, 2019, 2020, 2021 Liang Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''
bedqr.base

abstract base class
'''


class FoundMatchSignal(Exception):
    '''
    '''

    def __init__(self, *args, **kwargs):
        found = kwargs.pop('found', None)
        super().__init__(*args, **kwargs)
        self.found = found


class MultiPartFile(object):
    '''
    ABC for file format that contains multiple parts
    '''

    def __init__(self, **kwargs):
        super().__init__()
        # we need to make sure constructing the instance follows the directves in super-class
        # and prevent unwanted side-effect
        self._kwargs = kwargs

    @property
    def parts(self):
        return getattr(self, '_parts')

    def get_part(self, index):
        # make no assumptions about the ordering of the parts here
        _msg = 'sub-class must implement this'
        raise NotImplementedError(_msg)


class FileWithHeaderAndContent(MultiPartFile):
    '''
    file format that has a header part and a content part
    '''

    OFFSET_HEADER = 0
    OFFSET_BODY   = 1

    def get_part(self, index):
        return self.parts[index]

    @property
    def header(self):
        return self.get_part(self.OFFSET_HEADER)

    @property
    def body(self):
        return self.get_part(self.OFFSET_BODY)


class DataRow(object):

    def __init__(self, data):
        super().__init__()
        self._data = data
        assert self._data is not None, 'cannot initialize with empty data'

    def __getitem__(self, cell):
        val = self._data[cell]
        return val

    def __len__(self):
        return len(self._data)


class RowBasedStore(object):

    def get_cells_from_row(self, row):
        '''
        :param row: (string)

        :retrun: (list)
        '''
        ret = row.split(self.FIELD_SEP)
        return ret


class Reader(object):
    '''
    base-class of file reader
    '''

    def load_file_with_parser(self):
        file_content = self._fp.read()
        self.parser = self.parser_cls(file_content)
        return self

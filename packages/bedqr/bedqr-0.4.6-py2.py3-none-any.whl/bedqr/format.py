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
bedqr.format

file format specification: https://genome.ucsc.edu/FAQ/FAQformat.html
'''

from .base import FoundMatchSignal, FileWithHeaderAndContent, DataRow, RowBasedStore


class bedDataRow(DataRow):

    ROW_TYPE = {
        'HEADER' :  0,
        'BODY'   :  1,
        'EMPTY'  : -1,
        'INVALID': -2,
    }

    HEADER_PREFIX = (
        'browser',
        'track',
    )
    FIELD_EMPTY_VALUE = '.'
    FIELD_CHROM_REGEX = (
        'chr[0-9a-zA-Z_]+',
        'scaffold[0-9]+',
    )

    def __init__(self, line, parent=None):
        self._line = line
        self.parent = parent

    @property
    def _data(self):
        val = None
        try:
            val = self.parent.get_cells_from_row(self._line)
        except:
            raise
        return val

    def detect_line_type(self, line):
        CHOICE = self.ROW_TYPE
        ret = CHOICE['INVALID']
        try:
            if len(line) == 0:
                raise FoundMatchSignal(found=CHOICE['EMPTY'])

            header_prefix = self.HEADER_PREFIX
            for item in header_prefix:
                if line.startswith(item):
                    raise FoundMatchSignal(found=CHOICE['HEADER'])

            data_prefix = map(
                lambda x: x.split('[', 1)[0],
                self.FIELD_CHROM_REGEX
            )
            for item in data_prefix:
                if line.startswith(item):
                    raise FoundMatchSignal(found=CHOICE['BODY'])
        except FoundMatchSignal as match:
            ret = match.found
        #except Exception as ex:
        #    raise
        return ret

    @property
    def type(self):
        return self.detect_line_type(self._line)

    def __str__(self):
        return self._line


class BED(FileWithHeaderAndContent, RowBasedStore):
    '''
    Browser Extensible Data (BED)
    '''

    REQUIRED_FIELDS = (
        'chrom',
        'chromStart',
        'chromEnd',
    )
    OPTIONAL_FIELDS = (
        'name',
        'score',
        'strand',
        'thickStart',
        'thickEnd',
        'itemRgb',
        'blockCount',
        'blockSizes',
        'blockStarts',
    )

    def detect_column_count(self):
        val = None
        if len(self.body):
            first_row = self.body[0]
            if isinstance(first_row, (str,)):
                try:
                    converted_row = bedDataRow(
                        first_row,
                        parent=self
                    )
                    val = len(converted_row)
                except:
                    raise ValueError('cannot parse data row')  # caller or somewhere else deal with this exception
            else:
                val = len(first_row)
        return val

    def get_column_names(self):
        ret = self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS
        detected_column_count = self.detect_column_count()

        return ret[:detected_column_count]


class bedDetail(BED):
    '''
    BED detail
    '''

    FIELD_SEP = '\t'

    DETAIL_FIELDS = ('id', 'description')

    def get_column_names(self):
        columns_a = super().get_column_names()
        columns_b = (
            [ None for i in columns_a ] + list(self.DETAIL_FIELDS)
        )[-self.detect_column_count():]
        mapped_names = map(
            lambda x, y: y if y is not None else x,
            columns_a,
            columns_b
        )
        return list(mapped_names)


class BEDParser(object):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self._raw_data = data

    def get_data_object(self):
        self._object = bedDetail()

        lines = [ bedDataRow(item, parent=self._object) for item in self._raw_data.splitlines() if len(item.strip()) > 0 ]

        parts = {
            'header': [ line for line in lines if line.type == line.ROW_TYPE['HEADER'] ],
            'body'  : [ line for line in lines if line.type == line.ROW_TYPE['BODY'] ],
        }

        self._object._parts = list()
        self._object._parts.append(parts['header'])
        self._object._parts.append(parts['body'])

        return self._object

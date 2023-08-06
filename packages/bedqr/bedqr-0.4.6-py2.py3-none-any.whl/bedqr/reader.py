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
bedqr.reader

file I/O wrapper
'''

from .base import Reader
from .format import BEDParser


class QuickReader(Reader):
    '''
    class should be used by general users
    '''

    def __init__(self, fp, parser=BEDParser):
        self._fp = fp
        self.parser_cls = parser
        #
        self.load_file_with_parser()

    @property
    def data(self):
        return self.parser.get_data_object()

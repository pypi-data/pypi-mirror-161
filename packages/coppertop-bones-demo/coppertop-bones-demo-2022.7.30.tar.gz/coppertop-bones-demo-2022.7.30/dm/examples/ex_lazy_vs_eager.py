# **********************************************************************************************************************
#
#                             Copyright (c) 2020-2021 David Briant. All rights reserved.
#
# BSD 3-Clause License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# **********************************************************************************************************************

from coppertop.pipe import *
from dm.core import each, check, equal
from dm.core.range import FnAdapterFR, EMPTY, FnAdapterEager, each_, materialise
from dm.core.datetime import addDays, parseDate, day, toCTimeFormat

YYYY_MM_DD = 'YYYY.MM.DD' >> toCTimeFormat

@coppertop
def _ithDateBetween2(start, end, i):
    ithDate = start >> addDays(_, i)
    return EMPTY if ithDate > end else ithDate

@coppertop(style=binary2)
def datesBetween2(start, end):
     return FnAdapterFR(_ithDateBetween2(start, end, _))

@coppertop(style=binary2)
def datesBetweenEager2(start, end):
     return FnAdapterEager(_ithDateBetween2(start, end, _))


def test_datesBetween_lazy():
    ('2020.01.16' >> parseDate(_, YYYY_MM_DD)) >> datesBetween2 >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD)) \
    >> each_ >> day \
    >> materialise >> check >> equal >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

def test_datesBetween_eager():
    ('2020.01.16' >> parseDate(_, YYYY_MM_DD)) >> datesBetweenEager2 >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD)) \
    >> each >> day \
    >> check >> equal >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

def main():
    test_datesBetween_lazy()
    test_datesBetween_eager()

if __name__ == '__main__':
    main()
    print('pass')


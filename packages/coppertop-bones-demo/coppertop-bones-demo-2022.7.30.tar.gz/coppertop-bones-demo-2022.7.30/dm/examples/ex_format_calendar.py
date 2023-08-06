# **********************************************************************************************************************
#
#                             Copyright (c) 2019-2021 David Briant. All rights reserved.
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

# A python implementation of  https://wiki.dlang.org/Component_programming_with_ranges

import datetime

from coppertop.core import Null
from coppertop.pipe import *
from dm.core import count, pad, join, to, joinAll, check, equal, strip, take, not_, wrapInList, each, PP
from dm.core.datetime import day, weekday, weekdayName, monthLongName, addDays, parseDate, toCTimeFormat

from bones.libs.on_demand.range import IForwardRange

from dm.core.range import ChunkUsingSubRangeGeneratorFR, FnAdapterFR, ChunkFROnChangeOf, getIRIter, ListOR, pushAllTo, \
    EMPTY, toIndexableFR, each_, rUntil, rChain, replaceWith, RaggedZipIR, materialise, front
from ribs.types import txt, date



YYYY_MM_DD = 'YYYY.MM.DD' >> toCTimeFormat

# see notes in format_calendar.py



@coppertop
def datesInYear(year):
     return FnAdapterFR(_ithDateInYear(year, _))

@coppertop
def _ithDateInYear(year, i):
    ithDate = datetime.date(year, 1, 1) >> addDays(_, i)
    return EMPTY if ithDate.year != year else ithDate


@coppertop
def monthChunks(datesR):
    return ChunkFROnChangeOf(datesR, lambda x: x.month)


@coppertop
def _untilWeekdayName(datesR, wdayName):
    return datesR >> rUntil >> (lambda d: d >> weekday >> weekdayName == wdayName)
@coppertop
def weekChunks(r):
    return ChunkUsingSubRangeGeneratorFR(r, _untilWeekdayName(_, 'Sun'))


@coppertop
def dateAsDayString(d):
    return d >> day >> to(_,str) >> pad(_, right=3)


class WeekStringsRange(IForwardRange):
    def __init__(self, rOfWeeks):
        self.rOfWeeks = rOfWeeks

    @property
    def empty(self):
        return self.rOfWeeks.empty

    @property
    def front(self):
        # this exhausts the front week range
        week = self.rOfWeeks.front
        startDay = week.front >> weekday
        preBlanks = ['   '] * startDay
        dayStrings = week >> each_ >> dateAsDayString >> materialise
        postBlanks = ['   '] * (7 - ((dayStrings >> count) + startDay))
        return (preBlanks + dayStrings + postBlanks) >> joinAll

    def popFront(self):
        self.rOfWeeks.popFront()

    def save(self):
        # TODO delete once we've debugged the underlying save issue
        return WeekStringsRange(self.rOfWeeks.save())
weekStrings = coppertop(style=unary1, newName='weekStrings')(WeekStringsRange)

@coppertop
def monthTitle(month, width):
    return month >> monthLongName >> pad(_, center=width)


@coppertop
def monthLines(monthDays):
    return [
        monthDays.front.month >> monthTitle(_, 21) >> wrapInList >> toIndexableFR,
        monthDays >> weekChunks >> weekStrings
    ] >> rChain


@coppertop
def monthStringsToCalendarRow(strings, blank, sep):
    return strings >> materialise >> replaceWith(Null, blank) >> join(_, sep)


def pasteBlocks(rOfMonthChunk):
    return rOfMonthChunk >> RaggedZipIR >> each_ >> monthStringsToCalendarRow(" "*21, " ")


@coppertop
def _ithDateBetween(start, end, i):
    ithDate = start >> addDays(_, i)
    return EMPTY if ithDate > end else ithDate

@coppertop(style=binary2)
def datesBetween(start:date, end:date):
     return FnAdapterFR(_ithDateBetween(start, end, _))



def test_allDaysInYear():
    actual = []
    o = 2020 >> datesInYear >> pushAllTo >> ListOR(actual)
    actual[0] >> check >> equal >> datetime.date(2020, 1, 1)
    actual[-1] >> check >> equal >> datetime.date(2020, 12, 31)
    a = [e for e in 2020 >> datesInYear >> getIRIter]
    b = a >> count
    b \
        >> check \
        >> equal >> 366


def test_datesBetween():
    ('2020.01.16' >> parseDate(_, YYYY_MM_DD)) >> datesBetween >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD)) \
        >> each_ >> day \
        >> materialise \
        >> check >> equal >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]


def test_chunkingIntoMonths():
    2020 >> datesInYear \
        >> monthChunks \
        >> materialise \
        >> count \
        >> check >> equal >> 12


def test_checkNumberOfDaysInEachMonth():
    2020 >> datesInYear \
        >> monthChunks \
        >> materialise \
        >> each >> count \
        >> check >> equal >> [31,29,31,30,31,30,31,31,30,31,30,31]


def test__untilWeekdayName():
    r = 2020 >> datesInYear
    dates = [d for d in r >> _untilWeekdayName(_, 'Sun') >> getIRIter]
    dates[-1] >> check >> equal >> datetime.date(2020, 1, 5)   # the sunday
    r >> front >> check >> equal >> datetime.date(2020, 1, 6) # the monday


def test_WeekChunks():
    datesR = '2020.01.16' >> parseDate(_, YYYY_MM_DD) >> datesBetween >> ('2020.01.29' >> parseDate(_, YYYY_MM_DD))
    weeksR = ChunkUsingSubRangeGeneratorFR(datesR, _untilWeekdayName(_, 'Sun'))
    actual = []
    while not weeksR.empty:
        weekR = weeksR >> front
        actual.append([d >> day for d in weekR >> getIRIter])
        weeksR.popFront()
    actual >> check >> equal >> [[16, 17, 18, 19], [20, 21, 22, 23, 24, 25, 26], [27, 28, 29]]


def test_WeekStrings():
    expectedJan2020 = [
        '        1  2  3  4  5',
        '  6  7  8  9 10 11 12',
        ' 13 14 15 16 17 18 19',
        ' 20 21 22 23 24 25 26',
        ' 27 28 29 30 31      ',
    ]
    weekStringsR = (
        2020 >> datesInYear
        >> monthChunks
        >> front
        >> weekChunks
        >> weekStrings
    )
    weekStringsR2 = weekStringsR.save()
    [ws for ws in weekStringsR >> getIRIter] >> check >> equal >> expectedJan2020

    actual = [ws for ws in weekStringsR2 >> getIRIter]
    if actual >> equal >> expectedJan2020 >> not_:
        "fix WeekStringsRange.save()" >> PP


def test_MonthTitle():
    1 >> monthTitle(_, 21) >> wrapInList >> toIndexableFR \
        >> each_ >> strip >> materialise \
        >> check >> equal >> ['January']


def test_oneMonthsOutput():
    [
        1 >> monthTitle(_, 21) >> wrapInList >> toIndexableFR,
        2020 >> datesInYear
            >> monthChunks
            >> front
            >> weekChunks
            >> weekStrings
    ] >> rChain \
        >> materialise >> check >> equal >> Jan2020TitleAndDateLines

    # equivalently
    check(
        materialise(monthLines(front(monthChunks(datesInYear(2020))))),
        equal,
        Jan2020TitleAndDateLines
    )


def test_firstQuarter():
    2020 >> datesInYear \
        >> monthChunks \
        >> take >> 3 \
        >> RaggedZipIR >> each_ >> monthStringsToCalendarRow(Null, " "*21, " ")



Jan2020DateLines = [
    '        1  2  3  4  5',
    '  6  7  8  9 10 11 12',
    ' 13 14 15 16 17 18 19',
    ' 20 21 22 23 24 25 26',
    ' 27 28 29 30 31      ',
]

Jan2020TitleAndDateLines = ['       January       '] + Jan2020DateLines

Q1_2013TitleAndDateLines = [
    "       January              February                March        ",
    "        1  2  3  4  5                  1  2                  1  2",
    "  6  7  8  9 10 11 12   3  4  5  6  7  8  9   3  4  5  6  7  8  9",
    " 13 14 15 16 17 18 19  10 11 12 13 14 15 16  10 11 12 13 14 15 16",
    " 20 21 22 23 24 25 26  17 18 19 20 21 22 23  17 18 19 20 21 22 23",
    " 27 28 29 30 31        24 25 26 27 28        24 25 26 27 28 29 30",
    "                                             31                  "
]



def main():
    test_allDaysInYear()
    test_datesBetween()
    test_chunkingIntoMonths()
    test_checkNumberOfDaysInEachMonth()
    test__untilWeekdayName()
    test_WeekChunks()
    test_WeekStrings()
    test_MonthTitle()
    test_oneMonthsOutput()
    # test_firstQuarter()


if __name__ == '__main__':
    main()
    print('pass')

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

# see - https://en.wikipedia.org/wiki/Jackson_structured_programming
# this file show four ways to implement the problem of counting repeated lines in a file - two are translations from
# the wikipedia article and the remaining two take the "traditional" program and transform it into range style code

import os
from coppertop.pipe import *
from dm.core import getAttr, _, assertEquals
from dm.core.range import FileLineIR, ListOR, IInputRange, put, pushAllTo


home = os.path.dirname(os.path.abspath(__file__))
filename = "/linesForCounting.txt"
expected = [
    ('aaa\n', 2),
    ('bb\n', 1),
    ('aaa\n', 1),
    ('bb\n', 3),
    ('aaa\n', 1)
]


def countLinesTrad(f):
    answer = []

    count = 0
    firstLineOfGroup = ''
    line = f.readline()
    while line != '':
        if firstLineOfGroup == '' or line != firstLineOfGroup:
            if firstLineOfGroup != '':
                answer.append((firstLineOfGroup, count))
            count = 0
            firstLineOfGroup = line
        count += 1
        line = f.readline()

    if (firstLineOfGroup != ''):
        answer.append((firstLineOfGroup, count))

    return answer



def countLinesRanges1(f):
    r = FileLineIR(f)
    out = ListOR([])

    count = 0
    firstLineOfGroup = ''
    while not r.empty:
        if firstLineOfGroup == '' or r.front != firstLineOfGroup:
            if firstLineOfGroup != '':
                out >> put(_, (firstLineOfGroup, count))
            count = 0
            firstLineOfGroup = r.front
        count += 1
        r.popFront()

    if firstLineOfGroup != '':
        out >> put(_, (firstLineOfGroup, count))

    return out.list



def countLinesRanges2(f):
    out = ListOR([])
    r = FileLineIR(f)
    while not r.empty:
        count = r >> countEquals(_, firstLineOfGroup := r.front)
        out >> put(_, (firstLineOfGroup, count))
    return out.list


@coppertop
def countEquals(r, value):
    count = 0
    while not r.empty and r.front == value:
        count += 1
        r.popFront()
    return count



def countLinesRanges3(f):
    return FileLineIR(f) >> rRepititionCounts >> pushAllTo >> ListOR([]) >> getAttr(_, 'list')


@coppertop
def rRepititionCounts(r):
    return RepititionCountIR(r)

class RepititionCountIR(IInputRange):
    def __init__(self, r):
        self.r = r
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        firstInGroup = self.r.front
        count = 0
        while not self.r.empty and self.r.front ==firstInGroup:
            count += 1
            self.r.popFront()
        return firstInGroup, count
    def popFront(self):
        pass



# "Jackson criticises the traditional version, claiming that it hides the relationships which exist between the
# input lines, compromising the program's understandability and maintainability by, for example, forcing the use
# of a special case for the first line and forcing another special case for a final output operation."

def countLinesJsp(f):
    answer = []

    line = f.readline()
    while line != '':
        count = 0
        firstLineOfGroup = line

        while line != '' and line == firstLineOfGroup:
            count += 1
            line = f.readline()
        answer.append((firstLineOfGroup, count))

    return answer



def main():
    with open(home + filename) as f:
        actual = countLinesJsp(f)
    actual >> assertEquals >> expected

    with open(home + filename) as f:
        actual = countLinesTrad(f)
    actual >> assertEquals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges1(f)
    actual >> assertEquals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges2(f)
    actual >> assertEquals >> expected

    with open(home + filename) as f:
        actual = countLinesRanges3(f)
    actual >> assertEquals >> expected


if __name__ == '__main__':
    main()
    print('pass')


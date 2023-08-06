# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
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



import os

from dm.core import _, join, startsWith, inject, to, take, tvarray, keys, fromCsv, drop, agg, at, \
    atPut, select, stats, check, different, sameShape
import dm.core.vec as vec
from ribs.types import date, num

path = os.path.dirname(os.path.abspath(__file__))


def ex():
    renames = {
        'Date'  : 'date',
        '1 Mo'  : '_1m',
        '2 Mo'  : '_2m',
        '3 Mo'  : '_3m',
        '6 Mo'  : '_6m',
        '1 Yr'  : '_1y',
        '2 Yr'  : '_2y',
        '3 Yr'  : '_3y',
        '5 Yr'  : '_5y',
        '7 Yr'  : '_7y',
        '10 Yr' : '_10y',
        '20 Yr' : '_20y',
        '30 Yr' : '_30y'
    }


    conversions = dict(
        date=vec.to(_, date, 'MM/DD/YY'),
        _1m=vec.to(_, num),
        _2m=vec.to(_, num),
        _3m=vec.to(_, num),
        _6m=vec.to(_, num),
        _1y=vec.to(_, num),
        _2y=vec.to(_, num),
        _3y=vec.to(_, num),
        _5y=vec.to(_, num),
        _7y=vec.to(_, num),
        _10y=vec.to(_, num),
        _20y=vec.to(_, num),
        _30y=vec.to(_, num),
    )


    filename = 'us yields.csv'
    ytms = (path + '/' + filename) >> fromCsv(_, renames, conversions)

    # take logs
    ytms2 = ytms \
        >> keys >> drop >> ['date', '_2m'] \
        >> inject(_, agg(ytms), _) >> (lambda prior, name:
            prior >> atPut(_,
                'log' >> join >> (name >> drop >> 1),
                prior >> at(_, name) >> vec.log
            )
        )


    # select the desired date range
    d1 = '2021.01.01' >> to(_, date, 'YYYY.MM.DD')
    d2 = '2021.04.01' >> to(_, date, 'YYYY.MM.DD')
    usD1ToD2 = ytms2 >> select >> (lambda r: d1 <= r.date and r.date < d2)


    # diff and calc covariance matrices
    usDiffs = usD1ToD2 \
        >> keys >> drop >> 'date' \
        >> inject(_, agg(), _) >> (lambda p, f:
            p >> atPut(_, f, usD1ToD2 >> at(_, f) >> vec.diff)
        )

    t1 = usDiffs >> keys
    t2 = t1 >> select >> startsWith(_, '_')

    usDiffCov = usDiffs \
        >> take >> (usDiffs >> keys >> select >> startsWith(_, '_')) \
        >> to(_, tvarray) >> stats.core.cov

    usLogDiffCov = usDiffs \
        >> take >> (usDiffs >> keys >> select >> startsWith(_, 'log')) \
        >> to(_, tvarray) >> stats.core.cov

    usDiffCov >> check >> sameShape >> usLogDiffCov
    usDiffCov >> check >> different >> usLogDiffCov



def main():
    ex()


if __name__ == '__main__':
    main()
    print('pass')


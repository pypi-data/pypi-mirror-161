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


import sys         
# sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


from coppertop.pipe import *
from coppertop.testing import assertRaises
from bones.lang.metatypes import S, fitsWithin as fullFitsWithin
from ribs.types import T1, T2, tvfloat
from dm.core.types import ccy, fx
from dm.core import check, fitsWithin




GBP = ccy['GBP'][tvfloat].setCoercer(tvfloat)
USD = ccy['USD'][tvfloat].setCoercer(tvfloat)
tvccy = ccy & tvfloat

GBPUSD = fx[S(domestic=GBP, foreign=USD)].nameAs('GBPUSD')[tvfloat].setCoercer(tvfloat)
fxT1T2 = fx[S(domestic=tvccy[T1], foreign=tvccy[T2])] & tvfloat


@coppertop(style=binary2)
def addccy(a:tvccy[T1], b:tvccy[T1]) -> tvccy[T1]:
    return (a + b) | a._t

@coppertop(style=binary2)
def mul(dom:tvccy[T1], fx:fxT1T2, tByT) -> tvccy[T2]:
    assert dom._t == tvccy[tByT[T1]]
    return (dom * fx) | tvccy[tByT[T2]]

@coppertop(style=binary2)
def mul(dom:tvccy[T2], fx:fxT1T2, tByT) -> tvccy[T1]:
    assert dom._t == tvccy[tByT[T2]]
    return (dom / fx) | tvccy[tByT[T1]]


def testFx():
    a = (100|GBP)
    b = (1.3|GBPUSD)
    cacheId1, fits1, tByT1, distance1 = fullFitsWithin(GBP, tvccy[T1])
    cacheId2, fits2, tByT2, distance2 = fullFitsWithin(GBPUSD, fxT1T2)
    assert (100|GBP) >> mul >> (1.3|GBPUSD) >> addccy >> (20|USD) == (150|USD)
    assert (130|USD) >> mul >> (1.3|GBPUSD) == (100|GBP)

    with assertRaises(TypeError):
        (100|GBP) >> addccy >> (100|USD)

    assert (100|GBP) >> addccy >> (100|GBP) == (200|GBP)




def main():
    testFx()


if __name__ == '__main__':
    main()
    print('pass')

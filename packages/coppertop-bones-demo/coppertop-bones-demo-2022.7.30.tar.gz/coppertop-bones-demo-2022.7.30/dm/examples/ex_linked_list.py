# **********************************************************************************************************************
#
#                             Copyright (c) 2022 David Briant. All rights reserved.
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
from bones.core.errors import ProgrammerError
from bones.lang.metatypes import BTProxy, fitsWithin
from ribs.types import index, txt, err, T1, Ta, null
from bones.core.sentinels import Null
from dm.core import check, equal


# an ML linked list
# type 'a LinkedList = EmptyList | Cons of 'a * 'a LinkedList
# let head x = match x with | Cons (x, _) => x | EmptyList => raise Error("cannot take the  head of an empty list")
#
# let someIntList = Cons(5, EmptyList)
# let someStringList = Cons("Hello world", Cons("another string", EmptyList))
#
# let x = head(someIntList)
# let y = head(someStringList)


LList_ = BTProxy("LList")
LList = (null + (Ta*LList_)).nameAs("LList")


@coppertop
def constructLList(head:T1, tail:LList(Ta=T1), tByT) -> LList(Ta=T1):
    return (head, tail) | LList(Ta=tByT(T1))

LList.setConstructor(constructLList)



# style 1 - full dispatch on types in the union
@coppertop
def head1(x:null) -> err:
    return (err&str)("empty list")

@coppertop
def head1(x:T1*(LList(Ta=T1))) -> T1:
    return x[0]


# style 2 - if else / pattern matching
@coppertop
def head2(x):
    t = x >> typeOf
    if fitsWithin(t, null):
        return (err&str)("empty list")

    elif fitsWithin(t, T1*(LList(Ta=T1))):
        return x[0]

    else:
        raise TypeError(f'head3 not implemented for x is {x >> typeOf}')


# style 3 - dispatch on the union (requires pattern matching / if else in the function)
@coppertop
def head3(x:LList(Ta=T1), tByT) -> T1+(err&str):   # TODO fitsWithin does handle this as an output template yet
    t = x >> typeOf
    ta = tByT[T1]
    if fitsWithin(t, null):
        return (err&str)("empty list")
    elif fitsWithin(t, T1*(LList(Ta=ta))):
        return x[0]
    else:
        raise ProgrammerError("bug in fitsWithin")  # matched x is LList(Ta=T1) but not x is null, nor x is T1*(LList(Ta=ta))




def ex_llist():
    ll = Null
    head1(ll) >> check >> typeOf >> err

    ll = LList(4, LList(5, Null))
    ll >> check >> typeOf >> LList(Ta=index)
    head1(ll) >> check >> equal >> 4

    ll = LList('Hello', LList(' world', Null))
    ll >> check >> typeOf >> LList(Ta=str)
    head1(ll) >> check >> equal >> 'Hello'

    ll = Null
    head2(ll) >> check >> typeOf >> err

    ll = LList(4, LList(5, Null))
    ll >> check >> typeOf >> LList(Ta=index)
    head2(ll) >> check >> equal >> 4

    ll = Null
    head3(ll) >> check >> typeOf >> err

    ll = LList(4, LList(5, Null))
    ll >> check >> typeOf >> LList(Ta=index)
    head3(ll) >> check >> equal >> 4



def main():
    ex_llist()


if __name__ == '__main__':
    main()
    print('pass')


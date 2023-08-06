# **********************************************************************************************************************
#
#                             Copyright (c) 2021-2022 David Briant. All rights reserved.
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
from ribs.types import pylist, pytuple, pyset
from bones.libs.on_demand.range import IRandomAccessFinite
# from dm.core import select


# IMPORTANT - for f(x), could equally pass {xs, i} instead of x - does that open anything up for us?

# OPEN: in bones how first class are functions? can the actual functions be known statically without compromising
#       functionality? if it is known statically then it can be thrown at a compiler. My hunch is that we don't
#       need bones to be as dynamic as Smalltalk (e.g. call a function via an interface) it can probably know which
#       function, which opens the road to using optimising compilers in anger (albeit within compile time constraints)
# OPEN: is the _ sufficient to demark optimisation? are visitors sufficient?

# OPTIMSATIONS
# vector - loop over an array with fast machine code (e.g. SIMD) - these can be done at the function level without need
#          for xs >> both >> + >> ys, obvious operations +, -, /, *, **, >, <, <=, in, >>, <<, etc
#          x + xs -> ys,
#          xs + x -> ys,
#          xss >> both >> vwap >> ys
#
# in-place - e.g. xs: xs + ys
#
# amortise allocation - over allocate if memory is plentiful, take longer if it isn't
# allow loops to be exited early - e.g. line >> nextMinima -> {location, line}
#
# imperative style -> pipeline style or functional style
# xs each {x+1} each {x*x} sum
# the compiler could generate optimised code, e.g the imperative style in MC - problem of allowing it to always do
# that is debugging (out of order logging, and hard to follow stepping), also not always worth doing
# PP -> print as business output - lazy / quick and dirty ui
# LL -> log for debugging (this can be reordered
# MM -> log for monitoring purposes (warnings, errors, telemetry)
# TT -> trace (i.e. detailed logging)
#
# on demand
#   forward only - upstream can only be accessed in order and possibly just once (e.g. a real random number gen)
#   expensive - e.g. upstream is expensive so needs caching
#   random access - e.g. array >> select
#
# select: expensive -> expensive
#   keeps an index of next item, can answer max size, once everything filtered can answer size
#
# is it the fn that is expensive or the visitor
#
# why are ranges fast?
# are they as fast as imperative code?
# the compiler gets blocked by the allocation code?
# an advantage of ranges is that one can program in pipeline style whilst keeping the performance of imperative code
# the pipeline style implies extra memory allocations
# and makes the compilers job harder or impossible
# ranges give you a pipeline style but with some snags
# 1) you have to be away you are using a range so have to add array on the end - this awareness jolts me out of algo mode
# 2) debugging is out of order so you loose the cleanness of the pipeline style - again this is jolting
# 3) ranges come in several flavours and don't have a uniform interface, forward only vs random access
#    this makes indexy code more complex as then you need to consider when you collect the results into an indexable form
#
# we could make everything random access - or buffer forward only
# buffered is the norm, each_ allows random access style, library functions to rewrite in visitor style (expert level)




def test():
    xs = [1,2,3,4,5,6,7,8,9,10]

    # random access
    xs >> testTranform
    xs >> testTranformAndSum

    # forward
    xs >> forward >> testTranform
    xs >> forward >> testTranformAndSum

    # expensice
    xs >> expensive >> testTranform
    xs >> expensive >> testTranformAndSum


@coppertop
def testTranform(xs, expectedYs):
    ys = xs >> select >> (lambda x: x > 5) >> collect >> (lambda x: x + 1)
    ys = xs >> select_ >> (lambda x: x > 5) >> collect >> (lambda x: x + 1)
    ys = xs >> select >> (lambda x: x > 5) >> collect_ >> (lambda x: x + 1) >> to(_, pylist)
    ys = xs >> select_ >> (lambda x: x > 5) >> collect_ >> (lambda x: x + 1) >> to(_, pylist)

@coppertop
def testTranformAndSum(xs, expectedSum):
    a = xs >> select_ >> (lambda x: x > 5) >> collect >> (lambda x: x + 1) >> sum
    a = xs >> select_ >> (lambda x: x > 5) >> collect_ >> (lambda x: x + 1) >> sum


@coppertop
def to(x, t):
    pass

@coppertop
def collect(xs:pylist+pytuple+pyset, fn) -> pylist:
    pass

@coppertop
def collect(r, fn):
    pass

@coppertop
def collect_(xs:pylist+pytuple, fn) -> RAV:
    pass

@coppertop
def collect_(xs:pylist+pytuple, fn) -> IRandomAccessFinite:
    pass


# pyseqRAV = S(contained=pylist+pytuple, i1=index, i2=index)
#
# # ranges are inherently mutable
#
# the interface is empty, move, get
#
# so if we wanted to implement reverse in bones how do we do it?
#
# def rev(xs:RAV) -> RAV:
#
#
# we can't efficiently so reverse is atomic
#
# bones cannot see the range api?
#
# i.e. empty,
#
# move is either mutuable (against bones) or CoW (slow)
#
# so HoFs can use visitors under the hood but not the language
#
# forwardOnly
# slow
#
# do I need to prevent operations - e.g. at
#
# filter N in M out -> creates indexes,
# prevent recalc
#     debugging (out of order and seeing more than once - inherent in ranges)
#     slow stuff should be cached - e.g. whole cache or LRU etc
#
# why ever do forward only - speed and memory concerns - e.g. reading a file over a network or a record set from
# a remote db? or is inherently intricate and not worth implementing e.g. random access into a tree / DAG which can
# have a to(,RA)
#
# with mixed SoASoA do we have mixed optimal access?
#
# immutable so don't need output range
#
# generic programs take less space - e.g. map over size vs map over I8, I16, I32, F64 etc
# but maybe slightly slower
#
# (N**T)[RAV]
# (N**T)[seq]
# FOV




# class EachFR(IForwardRange):
#     def __init__(self, r, fn):
#         self.r = r >> toIRangeIfNot
#         if not callable(fn):
#             raise TypeError("RMAP.__init__ fn should be a function but got a %s" % type(fn))
#         self.f = fn
#     @property
#     def empty(self):
#         return self.r.empty
#     @property
#     def front(self):
#         return self.f(self.r.front)
#     def popFront(self):
#         self.r.popFront()
#     def save(self):
#         return EachFR(self.r.save(), self.f)

@coppertop
def collect_(r, fn):
    pass

@coppertop
def select(xs:pylist+pytuple, fn):
    pass

@coppertop
def select(r, fn):
    pass

@coppertop
def select_(xs:pylist+pytuple, fn):
    pass

@coppertop
def select_(r, fn):
    pass

@coppertop
def sum(xs:pylist+pytuple):
    pass

@coppertop
def sum(xs:pylist+pytuple):
    pass


# range summary
# IInputRange <- IForwardRange <- IBidirectionalRange <- IBidirectionalRange
#                              ^- IRandomAccessInfinite
# IInputRange {empty, front (get & set), popFront, moveFront}
# IForwardRange{save}
# IBidirectionalRange {back (get & set), moveBack, popBack}
# IRandomAccessFinite {moveAt, get & set, length}
# IRandomAccessInfinite {moveAt, get}
# IOutputRange {put}


@coppertop
def rTakeBack(r, n):
    raise NotYetImplemented()

@coppertop
def rDropBack(r, n):
    raise NotYetImplemented()

@coppertop
def rFind(r, value):
    while not r.empty:
        if r.front == value:
            break
        r.popFront()
    return r

@coppertop
def put(r, x):
    return r.put(x)

@coppertop(style=unary1)
def front(r):
    return r.front

@coppertop(style=unary1)
def back(r):
    return r.back

@coppertop(style=unary1)
def empty(r):
    return r.empty

@coppertop(style=unary1)
def popFront(r):
    r.popFront()
    return r

@coppertop(style=unary1)
def popBack(r):
    r.popBack()
    return r


each_ = coppertop(style=binary2, newName='each_')(EachFR)
rChain = coppertop(style=unary1, newName='rChain')(ChainAsSingleFR)
rUntil = coppertop(style=binary2, newName='rUntil')(UntilFR)


@coppertop
def replaceWith(haystack, needle, replacement):
    return haystack >> each_ >> (lambda e: replacement if e == needle else e)

@coppertop(style=binary2)
def pushAllTo(inR, outR):
    while not inR.empty:
        outR.put(inR.front)
        inR.popFront()
    return outR

def _materialise(r):
    answer = list()
    while not r.empty:
        e = r.front
        if isinstance(e, IInputRange) and not isinstance(e, IRandomAccessInfinite):
            answer.append(_materialise(e))
            if not r.empty:  # the sub range may exhaust this range
                r.popFront()
        else:
            answer.append(e)
            r.popFront()
    return answer

materialise = coppertop(style=unary1, newName='materialise')(_materialise)






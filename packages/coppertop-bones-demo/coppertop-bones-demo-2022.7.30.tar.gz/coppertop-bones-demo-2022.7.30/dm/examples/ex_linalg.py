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


from coppertop.pipe import *
from dm.core.types import N, num, aliased, anon, pytuple, pylist, tv, named
from bones.lang.metatypes import BTPrimitive
from dm.core import tvarray, check, equal, PP



matrix = N**N**num

colvec = matrix['colvec']
rowvec = matrix['rowvec']

square = BTPrimitive.ensure('square')

colmaj = BTPrimitive.ensure('colmaj').setImplicit
rowmaj = BTPrimitive.ensure('rowmaj').setOrthogonal



lol = BTPrimitive.ensure('lol').setConstructor(tv)

_matrix = matrix & tvarray
_colvec = _matrix & colvec
_rowvec = _matrix & rowvec

_llmatrix = (matrix & lol).setConstructor(tv)        # lol is a tvseq of tvseq, i.e. ragged array that we are making regular
_llcolvec = _llmatrix & colvec
_llrowvec = _llmatrix & rowvec

_lmatrix = matrix & pylist  # store the matrix in a linear fashion starting with n, m (colmaj and possibly transposed are in type)
_lcolvec = matrix & pylist
_lrowvec = matrix & pylist

# square and transposed is more of a dynamic / contingent type than a static type on the value but is static in
# terms of function sig and binding and sometimes static in terms of dispatch


@coppertop(style=unary1)
def T(A: _matrix) -> _matrix:
    return A.T


@coppertop(style=unary1)
def T(A: _llmatrix & aliased & colmaj) -> _llmatrix & anon & colmaj:
    answer = lol(A >> shape, colmaj)
    for i, col in enumerate(A):
        answer
    return answer


@coppertop(style=unary1)
def T(A: _llmatrix & anon & colmaj) -> _llmatrix & anon & colmaj:
    sh = A >> shape
    if sh[0] == sh[1]:
        A | +square >> T  # dispatch to T(A:_lmatrix & anon & colmaj & square)
    else:
        A | -anon >> T  # dispatch to T(A:_lmatrix & aliased & colmaj)


@coppertop(style=unary1)
def T(A: _llmatrix & anon & colmaj & square) -> _llmatrix & anon & colmaj & square:
    answer = lol(A >> shape, colmaj)
    for i, col in enumerate(A):
        answer
    return answer


@coppertop(style=unary1)
def T(A: _llmatrix & aliased & rowmaj) -> _llmatrix & anon & rowmaj:
    answer = [[]]
    for i in x:
        answer
    return answer


@coppertop(style=unary1)
def T(A: _llmatrix & anon & rowmaj) -> _llmatrix & anon & rowmaj:
    for i in x:
        A
    return A


@coppertop(style=unary1)
def T(A: _llmatrix & named & colmaj) -> _llmatrix & anon & colmaj:
    old = A._v
    new = [[] for r in old[0]]
    for i, col in enumerate(old):
        for j, e in enumerate(col):
            new[j].append(e)
    return tv(_llmatrix & anon, new)


@coppertop(style=unary1)
def shape(A: _lmatrix) -> pytuple:
    return tuple(A[0:2])

@coppertop(style=unary1)
def shape(A: _llmatrix) -> pytuple:
    lol = A._v
    return (len(lol[0]) if len(lol) > 0 else 0, len(lol))


def main():
    A = _llmatrix([[1, 2, 3], [3, 4, 5]]) | +named
    A >> shape >> PP
    A >> T >> PP >> shape >> check >> equal >> (2, 3)

# facts
# B: A causes both A and B to change type to aliased
# A's type is now aliased+named+anon as before it was named or anon
# AST Node results can be anon but A (upon assignment can only be named)
# any value addressable in a container is "named", e.g. A: (1,2,3)  - each element is "named"

# can tranpose as a type be static? no - consider rand(1,6) timesRepeat: [A: A T]?



if __name__ == '__main__':
    main()
    print('pass')

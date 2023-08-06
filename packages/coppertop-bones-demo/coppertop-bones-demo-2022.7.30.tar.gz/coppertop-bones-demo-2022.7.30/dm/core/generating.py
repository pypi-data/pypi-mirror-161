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

BONES_MODULE = 'dm.core'

from coppertop.pipe import *
from coppertop.core import NotYetImplemented, Missing
from dm.core.types import index

import numpy


@coppertop(style=unary1)
def til(n:index):
    # First n natural numbers (starting at 0)
    raise NotYetImplemented()

def sequence(p1, p2, n=Missing, step=Missing, sigmas=Missing):
    if step is not Missing and n is not Missing:
        raise TypeError('Must only specify either n or step')
    if step is Missing and n is Missing:
        first , last = p1, p2
        return list(range(first, last+1, 1))
    elif n is not Missing and sigmas is not Missing:
        mu, sigma = p1, p2
        low = mu - sigmas * sigma
        high = mu + sigmas * sigma
        return sequence(low, high, n=n)
    elif n is not Missing and sigmas is Missing:
        first , last = p1, p2
        return list(numpy.linspace(first, last, n))
    elif n is Missing and step is not Missing:
        first , last = p1, p2
        return list(numpy.arange(first, last + step, step))
    else:
        raise NotImplementedError('Unhandled case')

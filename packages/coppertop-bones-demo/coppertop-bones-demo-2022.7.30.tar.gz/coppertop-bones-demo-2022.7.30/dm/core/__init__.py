# **********************************************************************************************************************
#
#                             Copyright (c) 2017-2021 David Briant. All rights reserved.
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

version = '2022.03.06'       # dm.core.version

import sys

if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

import inspect
from coppertop.pipe import _DispatcherBase, _MultiDispatcher, MultiFn, _, sig
from dm.core.structs import tvarray, tvstruct

_mfByName = {}



def _collectDispatchers(mfByName, module):
    members = inspect.getmembers(module)
    members = [(name, o) for (name, o) in members if (name[0:1] != '_')]         # remove private
    members = [(name, mf) for (name, mf) in members if isinstance(mf, MultiFn)]
    for name, mf in members:
        mfByName.setdefault(name, []).append(mf)



# aggregation protocols
from dm.core import accessing as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import combining as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import complex as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import converting as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import dividing as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import generating as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import reordering as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import searching as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import transforming as _mod; _collectDispatchers(_mfByName, _mod)

# other protocols
from dm.core import files as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import linalg as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import maths as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import misc as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import stdio as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import testing as _mod; _collectDispatchers(_mfByName, _mod)
from dm.core import text as _mod; _collectDispatchers(_mfByName, _mod)
# from dm.core import types as _mod; _collectDispatchers(_mfByName, _mod)

# aggregation protocols
from dm.core.accessing import *
from dm.core.combining import *
from dm.core.complex import *
from dm.core.converting import *
from dm.core.dividing import *
from dm.core.generating import *
from dm.core.reordering import *
from dm.core.searching import *
from dm.core.transforming import *

# other protocols
from dm.core.files import *
from dm.core.linalg import *
from dm.core.maths import *
from dm.core.misc import *
from dm.core.stdio import *
from dm.core.testing import *
from dm.core.text import *
# from dm.core.types import *

from dm.core.misc import _t, _v   # needs doing separately as _ generally indicates it is pvt



__all__ = list(_mfByName.keys()) + ['_', 'tvarray', 'agg', '_t', '_v', 'typeOf', 'sig']
__all__.sort()


if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')

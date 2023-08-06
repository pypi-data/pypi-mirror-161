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


from dm.core import stdout, check, equal
from coppertop.pipe import *
from dm.core import to
from bones.lang.metatypes import BType

from ribs.types import str

null = BTNom.ensure('null')


tEntity = BTNom.ensure('entity')
tAsteroid = BTNom.ensure('asteroid')
tShip = BTNom.ensure('ship')
tCollision = BTNom.ensure('collision')
tEvent = BTNom.ensure('event')


@coppertop(unbox=True)
def to(v:txt, t:tShip) -> tShip:
    return v

@coppertop(unbox=True)
def to(v:txt, t:tAsteroid) -> tAsteroid:
    return v

@coppertop(unbox=True)
def to(v:txt, t:tEvent) -> tEvent:
    return v

@coppertop
def to(v:tEvent, t:txt) -> txt:
    return v._v | str


@coppertop
def collide(a:tAsteroid, b:tAsteroid) -> tEvent+null:
    return f'{a._v} split {b._v} (collide<:asteroid,asteroid:>)' >> to(_,tEvent)

@coppertop
def collide(a:tShip, b:tAsteroid) -> tEvent+null:
    return f'{a._v} tried to ram {b._v} (collide<:ship,asteroid:>)' >> to(_,tEvent)

@coppertop
def collide(a:tAsteroid, b:tShip) -> tEvent+null:
    return f'{a._v} destroyed {b._v} (collide<:asteroid,ship:>)' >> to(_,tEvent)

@coppertop
def collide(a:tShip, b:tShip) -> tEvent+null:
    return None | null
#    return f'{a} bounced {b} (collide<:ship,ship:>)' >> to(_,tEvent)


@coppertop
def process(e:tEvent+null) -> txt:
    return 'nothing' >> to(_,str) if e._s == null else (e >> to(_,str))



def testCollide():

    ship1 = 'ship1' >> to(_,tShip)
    ship2 = 'ship2' >> to(_,tShip)
    ast1 = 'big asteroid' >> to(_,tAsteroid)
    ast2 = 'small asteroid' >> to(_,tAsteroid)

    stdout << (ship1 >> collide(_, ship2) >> process >> to(_,str)) << '\n'
    stdout << (ship1 >> collide(_, ast1) >> process >> to(_,str)) << '\n'
    stdout << (ship2 >> collide(ast2, _) >> process >> to(_,str)) << '\n'
    stdout << (ast1 >> collide(_, ast2) >> process >> to(_,str)) << '\n'



def testTo():
    'hello' >> to(_,str) >> check >> equal >> ('hello' | str)
    ('hello' | str) >> to(_,str) >> check >> equal >> 'hello'



def main():
    testTo()
    testCollide()


if __name__ == '__main__':
    main()
    print('pass')

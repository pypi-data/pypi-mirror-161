# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied.
import pathlib

from ckms.types import JSONWebKey


KEY_DIR = pathlib.Path(__file__).parent
KEY_BOB = KEY_DIR.joinpath('bob.key')


alice: JSONWebKey = JSONWebKey.frompem(
    open(KEY_DIR.joinpath('alice.key'), 'rb').read(),
    kid='sig',
    alg='EdDSA',
    use='sig',
    key_ops=['sign']
)


bob: JSONWebKey = JSONWebKey.frompem(
    open(KEY_DIR.joinpath('bob.key'), 'rb').read(),
    kid='sig',
    alg='EdDSA',
    use='sig',
    key_ops=['sign']
)


trudy: JSONWebKey = JSONWebKey.frompem(
    open(KEY_DIR.joinpath('trudy.key'), 'rb').read(),
    kid='sig',
    alg='EdDSA',
    use='sig',
    key_ops=['sign']
)
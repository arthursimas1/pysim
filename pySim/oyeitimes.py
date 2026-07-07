# coding=utf-8
"""Utilities / Functions related to Oyeitimes R16 cards

(C) 2026 by Arthur Simas <hello@arthursimas.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pySim.ts_102_221 import EF_ARR
from pySim.filesystem import CardModel, TransparentEF, CardDF
from pySim.runtime import RuntimeState

class EF_Ki(TransparentEF):
    _test_de_encode = [
        (
            '0102030405060708090a0b0c0d0e0f10'
            ,
            { 'ki': '0102030405060708090a0b0c0d0e0f10' }
        )
    ]

    def __init__(self, fid='ff02', name='EF.Ki', desc='Authentication Key'):
        super().__init__(fid, name=name, desc=desc)
        # TODO: use self._construct = Struct()

    def _decode_hex(self, raw_hex_data: str) -> dict:
        return {'ki': raw_hex_data[:32]}

    def _encode_hex(self, abstract_data: dict, **kwargs) -> str:
        return abstract_data['ki']


class EF_OPc(TransparentEF):
    _test_de_encode = [
        (
            '100f0e0d0c0b0a090807060504030201'
            ,
            { 'opc': '100f0e0d0c0b0a090807060504030201' }
        )
    ]

    def __init__(self, fid='ff01', name='EF.OPc', desc='Operator Key'):
        super().__init__(fid, name=name, desc=desc)
        # TODO: use self._construct = Struct()

    def _decode_hex(self, raw_hex_data: str) -> dict:
        return {'opc': raw_hex_data[:32]}

    def _encode_hex(self, abstract_data: dict, **kwargs) -> str:
        return abstract_data['opc']

# TODO: implement Milenage Configuration EF
# MF/DF.SYSTEM/ff03 : 4000204060
# MF/DF.SYSTEM/ff04[1] : 00000000000000000000000000000000
# MF/DF.SYSTEM/ff04[2] : 00000000000000000000000000000001
# MF/DF.SYSTEM/ff04[3] : 00000000000000000000000000000002
# MF/DF.SYSTEM/ff04[4] : 00000000000000000000000000000004
# MF/DF.SYSTEM/ff04[5] : 00000000000000000000000000000008

# TODO: implement EF_USIM_SQN
#class EF_USIM_SQN(TransparentEF):
#    def __init__(self, fid='', name='EF.USIM_SQN', desc=''):
#        super().__init__(fid, name=name, desc=desc)


class DF_SYSTEM(CardDF):
    def __init__(self, fid='7ff0', name='DF.SYSTEM', desc='CardOS specifics'):
        super().__init__(fid=fid, name=name, desc=desc)
        files = [
            EF_ARR(fid='6f06'),
            EF_Ki(),
            EF_OPc(),
            #EF_USIM_SQN(),
        ]
        self.add_files(files)


class OyeitimesR16(CardModel):
    _atrs = ["3b9f94801fc78031e073fe2113578681098698621880"]

    @classmethod
    def add_files(cls, rs: RuntimeState):
        """Add Oyeitimes specific files to given RuntimeState."""
        rs.mf.add_file(DF_SYSTEM())

### parameters ###
# vendor-specific:
# + Ki
# + OPc
# - Authentication Algorithm (Milenage, TUAK, etc.)
# / Milenage Configuration
# - AMF (Authentication Management Field) - Typically set to 8000 for 5G
# - SQN (Sequence Number)
# 3GPP:
# + IMSI (MCC, MNC, MSIN)
# + SPN (Service Provider Name)

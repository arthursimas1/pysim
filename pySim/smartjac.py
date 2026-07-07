# coding=utf-8
"""Utilities / Functions related to SmartJac SMAOT500B cards

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

from osmocom.utils import h2b, b2h
from pySim.filesystem import CardModel, TransparentEF
from pySim.runtime import RuntimeState

def crc16_xmodem(data: bytes) -> int:
    """
    Compute the CRC-16-XMODEM checksum of the input data.
    """
    crc = 0x0000
    polynomial = 0x1021
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


class EF_Ki(TransparentEF):
    _test_de_encode = [
        (
            '415750012252443c92628902d97266d9' +  # Ki
            '85f0'                                # CRC
            ,
            { 'ki': '415750012252443c92628902d97266d9' }
        )
    ]

    def __init__(self, fid='62fc', name='EF.Ki', desc='Authentication Key'):
        super().__init__(fid, name=name, desc=desc)
        # TODO: use self._construct = Struct()

    def _decode_hex(self, raw_hex_data: str) -> dict:
        # Ki is stored as 16 bytes of key + 2 bytes CRC.
        # This decodes to return the 16 bytes.
        return {'ki': raw_hex_data[:32]}

    def _encode_hex(self, abstract_data: dict, **kwargs) -> str:
        ki_hex = abstract_data['ki']
        crc = crc16_xmodem(h2b(ki_hex))
        return ki_hex + '{:04x}'.format(crc)

# TODO: the trailing bytes in EF.OPc are Milenage parameters. it should be parsed properly. check sysmocom_sja2.py EF_MILENAGE_CFG for reference
class EF_OPc(TransparentEF):
    _test_de_encode = [
        (
            '01' +
            '558934202121291197086328647a239b' +  # OPc
            '88de' +                              # CRC
            '4000204060'
            '00000000000000000000000000000000' +
            '00000000000000000000000000000001' +
            '00000000000000000000000000000002' +
            '00000000000000000000000000000004' +
            '00000000000000000000000000000008'
            ,
            { 'opc': '558934202121291197086328647a239b' }
        ),
        (
            '00' +
            '558934202121291197086328647a239b' +  # OPc
            '88de' +                              # CRC
            '4000204060'
            '00000000000000000000000000000000' +
            '00000000000000000000000000000001' +
            '00000000000000000000000000000002' +
            '00000000000000000000000000000004' +
            '00000000000000000000000000000008'
            ,
            { 'op': '558934202121291197086328647a239b' }
        ),
    ]

    def __init__(self, fid='62fd', name='EF.OPc', desc='Operator Key'):
        super().__init__(fid, name=name, desc=desc)
        # TODO: use self._construct = Struct()

    def _decode_hex(self, raw_hex_data: str) -> dict:
        # 1 byte type, 16 bytes OPc, 2 bytes CRC...
        if raw_hex_data[0:2] == '00': # OP
            return {'op': raw_hex_data[2:34]}
        if raw_hex_data[0:2] == '01': # OPc
            return {'opc': raw_hex_data[2:34]}

    def _encode_hex(self, abstract_data: dict, **kwargs) -> str:
        opc_hex = abstract_data.get('op') or abstract_data.get('opc')
        crc = crc16_xmodem(h2b(opc_hex))
        # Type 01, OPc, CRC, constant trailing bytes
        trailer = (
            '40002040600000'
            '0000000000000000000000000000000000000000000000000000'
            '0000000100000000000000000000000000000002000000000000'
            '0000000000000000000400000000000000000000000000000008'
        )
        return ('00' if abstract_data.get('op') else '01') + opc_hex + '{:04x}'.format(crc) + trailer


# TODO: implement EF_USIM_SQN
#class EF_USIM_SQN(TransparentEF):
#    def __init__(self, fid='', name='EF.USIM_SQN', desc=''):
#        super().__init__(fid, name=name, desc=desc)


class SmartJacSMAOT500B(CardModel):
    _atrs = ["3b9f96801fc78031e073fea11f6441805100829000d5"]

    @classmethod
    def add_files(cls, rs: RuntimeState):
        """Add SmartJac specific files to given RuntimeState."""
        # Find USIM application
        if 'a0000000871002' in rs.mf.applications:
            usim_adf = rs.mf.applications['a0000000871002']
            files_adf_usim = [
                EF_Ki(),
                EF_OPc(),
                #EF_USIM_SQN(),
            ]
            usim_adf.add_files(files_adf_usim)

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

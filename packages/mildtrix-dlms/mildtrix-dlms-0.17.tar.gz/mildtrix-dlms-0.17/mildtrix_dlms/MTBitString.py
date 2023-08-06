#
#  --------------------------------------------------------------------------
#   mildtrix Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) mildtrix Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of mildtrix Device Framework.
#
#  mildtrix Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  mildtrix Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of mildtrix products: http://www.mildtrix.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
#
#  --------------------------------------------------------------------------
#
from .MTUInt8 import MTUInt8

# BitString class is used with Bit strings.
class MTBitString:

    #
    # Constructor.
    #
    # @param val
    # Bit string value.
    #
    def __init__(self, val, count=None):
        if isinstance(val, (MTUInt8)):
            val = MTBitString.___toBitString(val, 8)
            if count:
                val = val[0:count]
        self.value = val

    @classmethod
    def ___toBitString(cls, value, count):
        count = min(count, 8)
        pos = 0
        sb = ""
        while pos != count:
            if (value & (1 << pos)) != 0:
                sb += "1"
            else:
                sb += "0"
            pos = 1 + pos
        return sb

    # Convert integer value to BitString.
    # value: Value to convert.
    # count: Amount of bits.
    # Returns: Bitstring.
    @classmethod
    def toBitString(cls, value, count):
        sb = cls.___toBitString(value & 0xFF, count)
        if count > 8:
            sb += cls.___toBitString((value >> 8) & 0xFF, count - 8)
            if count > 16:
                sb += cls.___toBitString((value >> 16) & 0xFF, count - 16)
                if count > 24:
                    sb += cls.___toBitString((value >> 24) & 0xFF, count - 24)
        if len(sb) > count:
            return sb[0, count]
        return sb

    def __str__(self):
        return self.value

    #
    # Bit string value as byte.
    #
    def toInteger(self):
        val = 0
        if self.value:
            pos = 0
            for it in self.value:
                if it == '1':
                    val |= (1 << pos)
                elif it != '0':
                    raise ValueError("Invalid parameter.")
                pos = 1 + pos
        return val

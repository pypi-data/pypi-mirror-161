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
from .MTDLMSObject import MTDLMSObject
from .IMTDLMSBase import IMTDLMSBase
from ..enums import ErrorCode
from ..internal._MTCommon import _MTCommon
from ..MTByteBuffer import MTByteBuffer
from ..enums import ObjectType, DataType

# pylint: disable=too-many-instance-attributes
class MTDLMSMacAddressSetup(MTDLMSObject, IMTDLMSBase):
    """
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSMacAddressSetup
    """
    def __init__(self, ln="0.0.25.2.0.255", sn=0):
        """
        Constructor.

        ln : Logical Name of the object.
        sn : Short Name of the object.
        """
        #pylint: disable=super-with-arguments
        super(MTDLMSMacAddressSetup, self).__init__(ObjectType.MAC_ADDRESS_SETUP, ln, sn)
        self.macAddress = None

    def getValues(self):
        return [self.logicalName,
                self.macAddress]

    #
    # Returns collection of attributes to read.  If attribute is static
    #      and
    # already read or device is returned HW error it is not returned.
    #
    def getAttributeIndexToRead(self, all_):
        attributes = list()
        #  LN is static and read only once.
        if all_ or not self.logicalName:
            attributes.append(1)
        #  MacAddress
        if all_ or not self.isRead(2):
            attributes.append(2)
        return attributes

    #
    # Returns amount of attributes.
    #
    def getAttributeCount(self):
        return 2

    #
    # Returns amount of methods.
    #
    def getMethodCount(self):
        return 0

    def getDataType(self, index):
        if index == 1:
            return DataType.OCTET_STRING
        if index == 2:
            return DataType.OCTET_STRING
        raise ValueError("getDataType failed. Invalid attribute index.")

    #
    # Returns value of given attribute.
    #
    def getValue(self, settings, e):
        if e.index == 1:
            return _MTCommon.logicalNameToBytes(self.logicalName)
        if e.index == 2:
            if not self.macAddress:
                return self.macAddress
            return MTByteBuffer.hexToBytes(self.macAddress.replace(":", " "))
        e.error = ErrorCode.READ_WRITE_DENIED
        return None

    #
    # Set value of given attribute.
    #
    def setValue(self, settings, e):
        if e.index == 1:
            self.logicalName = _MTCommon.toLogicalName(e.value)
        elif e.index == 2:
            add = MTByteBuffer.hex(e.value)
            self.macAddress = add.replace(" ", ":")
        else:
            e.error = ErrorCode.READ_WRITE_DENIED

    def load(self, reader):
        self.macAddress = reader.readElementContentAsString("MacAddress")

    def save(self, writer):
        writer.writeElementString("MacAddress", self.macAddress)

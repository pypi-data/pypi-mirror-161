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
from .MTDLMSObjectDefinition import MTDLMSObjectDefinition

# pylint: disable=too-many-instance-attributes
class MTDLMSRegisterActivation(MTDLMSObject, IMTDLMSBase):
    """
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSRegisterActivation
    """

    #
    # Constructor.
    #
    # @param ln
    #            Logical Name of the object.
    # @param sn
    #            Short Name of the object.
    #
    def __init__(self, ln=None, sn=0):
        #pylint: disable=super-with-arguments
        super(MTDLMSRegisterActivation, self).__init__(ObjectType.REGISTER_ACTIVATION, ln, sn)
        self.registerAssignment = list()
        self.maskList = list()
        self.activeMask = bytearray()

    def getValues(self):
        return [self.logicalName,
                self.registerAssignment,
                self.maskList,
                self.activeMask]

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
        if all_ or not self.isRead(2):
            attributes.append(2)
        #  MaskList
        if all_ or not self.isRead(3):
            attributes.append(3)
        #  ActiveMask
        if all_ or not self.isRead(4):
            attributes.append(4)
        return attributes

    #
    # Returns amount of attributes.
    #
    def getAttributeCount(self):
        return 4

    #
    # Returns amount of methods.
    #
    def getMethodCount(self):
        return 3

    def getDataType(self, index):
        if index == 1:
            ret = DataType.OCTET_STRING
        elif index == 2:
            ret = DataType.ARRAY
        elif index == 3:
            ret = DataType.ARRAY
        elif index == 4:
            ret = DataType.OCTET_STRING
        else:
            raise ValueError("getDataType failed. Invalid attribute index.")
        return ret

    #
    # Returns value of given attribute.
    #
    def getValue(self, settings, e):
        if e.index == 1:
            return _MTCommon.logicalNameToBytes(self.logicalName)
        if e.index == 2:
            data = MTByteBuffer()
            data.setUInt8(DataType.ARRAY)
            if not self.registerAssignment:
                data.setUInt8(0)
            else:
                data.setUInt8(len(self.registerAssignment))
                for it in self.registerAssignment:
                    data.setUInt8(DataType.STRUCTURE)
                    data.setUInt8(2)
                    _MTCommon.setData(settings, data, DataType.UINT16, it.objectType)
                    _MTCommon.setData(settings, data, DataType.OCTET_STRING, _MTCommon.logicalNameToBytes(it.logicalName))
            return data
        if e.index == 3:
            data = MTByteBuffer()
            data.setUInt8(DataType.ARRAY)
            data.setUInt8(len(self.maskList))
            for k, v in self.maskList:
                data.setUInt8(DataType.STRUCTURE)
                data.setUInt8(2)
                _MTCommon.setData(settings, data, DataType.OCTET_STRING, k)
                data.setUInt8(DataType.ARRAY)
                data.setUInt8(len(v))
                for b in v:
                    _MTCommon.setData(settings, data, DataType.UINT8, b)
            return data
        if e.index == 4:
            return self.activeMask
        e.error = ErrorCode.READ_WRITE_DENIED
        return None

    #
    # Set value of given attribute.
    #
    def setValue(self, settings, e):
        if e.index == 1:
            self.logicalName = _MTCommon.toLogicalName(e.value)
        elif e.index == 2:
            self.registerAssignment = []
            if e.value:
                for it in e.value:
                    item = MTDLMSObjectDefinition()
                    item.objectType = ObjectType(it[0])
                    item.logicalName = _MTCommon.toLogicalName(it[1])
                    self.registerAssignment.append(item)
        elif e.index == 3:
            self.maskList = []
            if e.value:
                for it in e.value:
                    self.maskList.append((it[0], it[1]))
        elif e.index == 4:
            if not e.value:
                self.activeMask = None
            else:
                self.activeMask = e.value
        else:
            e.error = ErrorCode.READ_WRITE_DENIED

    def load(self, reader):
        self.registerAssignment = []
        if reader.isStartElement("RegisterAssignment", True):
            while reader.isStartElement("Item", True):
                it = MTDLMSObjectDefinition()
                it.objectType = ObjectType(reader.readElementContentAsInt("ObjectType"))
                it.logicalName = reader.readElementContentAsString("LN")
                self.registerAssignment.append(it)
        self.maskList = []
        if reader.isStartElement("MaskList", True):
            while reader.isStartElement("Item", True):
                mask = MTByteBuffer.hexToBytes(reader.readElementContentAsString("Mask"))
                str_ = reader.readElementContentAsString("Index")
                i = MTByteBuffer.hexToBytes(str_.replace(";", " "))
                self.maskList.append((mask, i))
            reader.readEndElement("MaskList")
        self.activeMask = MTByteBuffer.hexToBytes(reader.readElementContentAsString("ActiveMask"))

    def save(self, writer):
        if self.registerAssignment:
            writer.writeStartElement("RegisterAssignment")
            for it in self.registerAssignment:
                writer.writeStartElement("Item")
                writer.writeElementString("ObjectType", int(it.objectType))
                writer.writeElementString("LN", it.logicalName)
                writer.writeEndElement()
            writer.writeEndElement()

        if self.maskList:
            writer.writeStartElement("MaskList")
            for k, v in self.maskList:
                writer.writeStartElement("Item")
                writer.writeElementString("Mask", MTByteBuffer.hex(k))
                writer.writeElementString("Index", MTByteBuffer.hex(v).replace(" ", ";"))
                writer.writeEndElement()
            writer.writeEndElement()
        if self.activeMask:
            writer.writeElementString("ActiveMask", MTByteBuffer.hex(self.activeMask))

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
#  mildtrix Device Framework is Open Source software you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation version 2 of the License.
#  mildtrix Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
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
from .enums import Weekdays
from ..enums import ObjectType, DataType
from .MTDLMSScheduleEntry import MTDLMSScheduleEntry
from ..MTDate import MTDate
from ..MTTime import MTTime
from ..MTByteBuffer import MTByteBuffer
from ..MTBitString import MTBitString

# pylint: disable=too-many-instance-attributes
class MTDLMSSchedule(MTDLMSObject, IMTDLMSBase):
    """
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSSchedule
    """
    def __init__(self, ln=None, sn=0):
        """
        Constructor.

        ln : Logical Name of the object.
        sn : Short Name of the object.
        """
        #pylint: disable=super-with-arguments
        super(MTDLMSSchedule, self).__init__(ObjectType.SCHEDULE, ln, sn)
        # Specifies the scripts to be executed at given times.
        self.entries = list()

    def getValues(self):
        return [self.logicalName,
                self.entries]

    #
    # Add entry to entries list.
    #
    # client: DLMS client.
    # entry: Schedule entry.
    # Returns Action bytes.
    def insert(self, client, entry):
        data = MTByteBuffer()
        self.addEntry(entry, data)
        return client.method(self, 2, data.array(), DataType.STRUCTURE)

    #
    # Remove entry from entries list.
    #
    # client: DLMS client.
    # entry: Schedule entry.
    # Returns Action bytes.
    def delete(self, client, entry):
        data = MTByteBuffer()
        data.setUInt8(DataType.STRUCTURE)
        #Add structure size.
        data.setUInt8(2)
        #firstIndex
        _MTCommon.setData(None, data, DataType.UINT16, entry.index)
        #lastIndex
        _MTCommon.setData(None, data, DataType.UINT16, entry.index)
        return client.method(self, 3, data.array(), DataType.STRUCTURE)

    #
    # Enable entry from entries list.
    #
    # client: DLMS client.
    # entry: Schedule entries.
    # Returns Action bytes.
    def enable(self, client, entry):
        data = MTByteBuffer()
        data.setUInt8(DataType.STRUCTURE)
        #Add structure size.
        data.setUInt8(4)
        #firstIndex
        _MTCommon.setData(None, data, DataType.UINT16, entry.index)
        #lastIndex
        _MTCommon.setData(None, data, DataType.UINT16, entry.index)
        _MTCommon.setData(None, data, DataType.UINT16, 0)
        _MTCommon.setData(None, data, DataType.UINT16, 0)
        return client.method(self, 1, data.array(), DataType.STRUCTURE)

    #
    # Disable entry from entries list.
    #
    # client: DLMS client.
    # entry: Schedule entries.
    # Returns Action bytes.
    def disable(self, client, entry):
        data = MTByteBuffer()
        data.setUInt8(DataType.STRUCTURE)
        #Add structure size.
        data.setUInt8(4)
        #firstIndex
        _MTCommon.setData(None, data, DataType.UINT16, 0)
        _MTCommon.setData(None, data, DataType.UINT16, 0)
        _MTCommon.setData(None, data, DataType.UINT16, entry.index)
        #lastIndex
        _MTCommon.setData(None, data, DataType.UINT16, entry.index)
        return client.method(self, 1, data.array(), DataType.STRUCTURE)

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
        #  Entries
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
        return 3

    def getDataType(self, index):
        if index == 1:
            return DataType.OCTET_STRING
        if index == 2:
            return DataType.ARRAY
        raise ValueError("getDataType failed. Invalid attribute index.")

    @classmethod
    def addEntry(cls, it, data):
        data.setUInt8(DataType.STRUCTURE)
        data.setUInt8(10)
        #Add index.
        data.setUInt8(DataType.UINT16)
        data.setUInt16(it.index)
        #Add enable.
        data.setUInt8(DataType.BOOLEAN)
        data.setUInt8(it.enable)
        #Add logical Name.
        data.setUInt8(DataType.OCTET_STRING)
        data.setUInt8(6)
        data.set(_MTCommon.logicalNameToBytes(it.logicalName))
        #Add script selector.
        data.setUInt8(DataType.UINT16)
        data.setUInt16(it.scriptSelector)
        #Add switch time.
        _MTCommon.setData(None, data, DataType.OCTET_STRING, MTTime(it.switchTime))
        #Add validity window.
        data.setUInt8(DataType.UINT16)
        data.setUInt16(it.validityWindow)
        #Add exec week days.
        _MTCommon.setData(None, data, DataType.BITSTRING, MTBitString.toBitString(it.execWeekdays, 7))
        #Add exec spec days.
        _MTCommon.setData(None, data, DataType.BITSTRING, it.execSpecDays)
        #Add begin date.
        _MTCommon.setData(None, data, DataType.OCTET_STRING, MTDate(it.beginDate))
        #Add end date.
        _MTCommon.setData(None, data, DataType.OCTET_STRING, MTDate(it.endDate))

    #
    # Returns value of given attribute.
    #
    def getValue(self, settings, e):
        if e.index == 1:
            return _MTCommon.logicalNameToBytes(self.logicalName)
        if e.index == 2:
            data = MTByteBuffer()
            data.setUInt8(DataType.ARRAY)
            _MTCommon.setObjectCount(len(self.entries), data)
            for it in self.entries:
                self.addEntry(it, data)
            return data.array()
        e.error = ErrorCode.READ_WRITE_DENIED
        return None

    #
    # Create a new entry.
    #
    @classmethod
    def createEntry(cls, settings, it):
        item = MTDLMSScheduleEntry()
        item.index = it[0]
        item.enable = it[1]
        item.logicalName = _MTCommon.toLogicalName(it[2])
        item.scriptSelector = it[3]
        item.switchTime = _MTCommon.changeType(settings, it[4], DataType.TIME)
        item.validityWindow = it[5]
        item.execWeekdays = Weekdays(it[6].toInteger())
        item.execSpecDays = str(it[7])
        item.beginDate = _MTCommon.changeType(settings, it[8], DataType.DATE)
        item.endDate = _MTCommon.changeType(settings, it[9], DataType.DATE)
        return item

    #
    # Set value of given attribute.
    #
    def setValue(self, settings, e):
        if e.index == 1:
            self.logicalName = _MTCommon.toLogicalName(e.value)
        elif e.index == 2:
            self.entries = []
            if e.value:
                for it in e.value:
                    self.entries.append(self.createEntry(settings, it))
        else:
            e.error = ErrorCode.READ_WRITE_DENIED

    def load(self, reader):
        self.entries = []
        if reader.isStartElement("Entries", True):
            while reader.isStartElement("Item", True):
                it = MTDLMSScheduleEntry()
                it.index = reader.readElementContentAsInt("Index")
                it.enable = reader.readElementContentAsInt("Enable") != 0
                it.logicalName = reader.readElementContentAsString("LogicalName")
                it.scriptSelector = reader.readElementContentAsInt("ScriptSelector")
                it.switchTime = reader.readElementContentAsTime("SwitchTime")
                it.validityWindow = reader.readElementContentAsInt("ValidityWindow")
                it.execWeekdays = Weekdays(reader.readElementContentAsInt("ExecWeekdays"))
                it.execSpecDays = reader.readElementContentAsString("ExecSpecDays")
                it.beginDate = reader.readElementContentAsDate("BeginDate")
                it.endDate = reader.readElementContentAsDate("EndDate")
                self.entries.append(it)
            reader.readEndElement("Entries")

    def save(self, writer):
        if self.entries:
            writer.writeStartElement("Entries")
            for it in self.entries:
                writer.writeStartElement("Item")
                writer.writeElementString("Index", it.index)
                writer.writeElementString("Enable", it.enable)
                writer.writeElementString("LogicalName", it.logicalName)
                writer.writeElementString("ScriptSelector", it.scriptSelector)
                writer.writeElementString("SwitchTime", it.switchTime)
                writer.writeElementString("ValidityWindow", it.validityWindow)
                writer.writeElementString("ExecWeekdays", int(it.execWeekdays))
                writer.writeElementString("ExecSpecDays", it.execSpecDays)
                writer.writeElementString("BeginDate", it.beginDate)
                writer.writeElementString("EndDate", it.endDate)
                writer.writeEndElement()
            writer.writeEndElement()

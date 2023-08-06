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
from ..enums import ObjectType, DataType
from ..MTByteBuffer import MTByteBuffer
from .MTMacMulticastEntry import MTMacMulticastEntry
from .MTMacDirectTable import MTMacDirectTable
from .MTMacAvailableSwitch import MTMacAvailableSwitch
from .MTMacPhyCommunication import MTMacPhyCommunication

# pylint: disable=too-many-instance-attributes
class MTDLMSPrimeNbOfdmPlcMacNetworkAdministrationData(MTDLMSObject, IMTDLMSBase):
    """
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSPrimeNbOfdmPlcMacNetworkAdministrationData
    """

    def __init__(self, ln="0.0.28.5.0.255", sn=0):
        """
        Constructor.

        ln : Logical Name of the object.
        sn : Short Name of the object.
        """
        MTDLMSObject.__init__(self, ObjectType.PRIME_NB_OFDM_PLC_MAC_NETWORK_ADMINISTRATION_DATA, ln, sn)
        # List of entries in multicast switching table.
        self.multicastEntries = list()
        # Switch table.
        self.switchTable = list()
        # List of entries in multicast switching table.
        self.directTable = list()
        # List of available switches.
        self.availableSwitches = list()
        # List of PHY communication parameters.
        self.communications = list()

    def getValues(self):
        return [self.logicalName,
                self.multicastEntries,
                self.switchTable,
                self.directTable,
                self.availableSwitches,
                self.communications]

    def reset(self, client):
        """Reset the values."""
        return client.method(self.getName(), self.objectType, 1, 0, DataType.INT8)

    def invoke(self, settings, e):
        #  Resets the value to the default value.
        #  The default value is an instance specific constant.
        if e.index == 1:
            self.multicastEntries = list()
            self.switchTable = list()
            self.directTable = list()
            self.availableSwitches = list()
            self.communications = list()
        else:
            e.error = ErrorCode.READ_WRITE_DENIED
    #
    # Returns collection of attributes to read.  If attribute is static and
    # already read or device is returned HW error it is not returned.
    #
    def getAttributeIndexToRead(self, all_):
        attributes = list()
        #  LN is static and read only once.
        if all_ or not self.logicalName:
            attributes.append(1)
        #  MulticastEntries
        if all_ or self.canRead(2):
            attributes.append(2)
        #  SwitchTable
        if all_ or self.canRead(3):
            attributes.append(3)
        #  DirectTable
        if all_ or self.canRead(4):
            attributes.append(4)
        #  AvailableSwitches
        if all_ or self.canRead(5):
            attributes.append(5)
        #  Communications
        if all_ or self.canRead(6):
            attributes.append(6)
        return attributes

    #
    # Returns amount of attributes.
    #
    def getAttributeCount(self):
        return 6

    #
    # Returns amount of methods.
    #
    def getMethodCount(self):
        return 1

    def getDataType(self, index):
        if index == 1:
            return DataType.OCTET_STRING
        if index in (2, 3, 4, 5, 6):
            return DataType.ARRAY
        raise ValueError("getDataType failed. Invalid attribute index.")

    def __getMulticastEntries(self, settings):
        bb = MTByteBuffer()
        bb.setUInt8(DataType.ARRAY)
        if not self.multicastEntries:
            _MTCommon.setObjectCount(0, bb)
        else:
            _MTCommon.setObjectCount(len(self.multicastEntries), bb)
            for it in self.multicastEntries:
                bb.setUInt8(DataType.STRUCTURE)
                bb.setUInt8(2)
                _MTCommon.setData(settings, bb, DataType.INT8, it.id)
                _MTCommon.setData(settings, bb, DataType.INT16, it.members)
        return bb.array()

    def __getSwitchTable(self, settings):
        bb = MTByteBuffer()
        bb.setUInt8(DataType.ARRAY)
        if not self.switchTable:
            _MTCommon.setObjectCount(0, bb)
        else:
            _MTCommon.setObjectCount(len(self.switchTable), bb)
            for it in self.switchTable:
                _MTCommon.setData(settings, bb, DataType.INT16, it)
        return bb.array()

    def __getDirectTable(self, settings):
        bb = MTByteBuffer()
        bb.setUInt8(DataType.ARRAY)
        if not self.directTable:
            _MTCommon.setObjectCount(0, bb)
        else:
            _MTCommon.setObjectCount(len(self.directTable), bb)
            for it in self.directTable:
                bb.setUInt8(DataType.STRUCTURE)
                bb.setUInt8(7)
                _MTCommon.setData(settings, bb, DataType.INT16, it.sourceSId)
                _MTCommon.setData(settings, bb, DataType.INT16, it.sourceLnId)
                _MTCommon.setData(settings, bb, DataType.INT16, it.sourceLcId)
                _MTCommon.setData(settings, bb, DataType.INT16, it.destinationSId)
                _MTCommon.setData(settings, bb, DataType.INT16, it.destinationLnId)
                _MTCommon.setData(settings, bb, DataType.INT16, it.destinationLcId)
                _MTCommon.setData(settings, bb, DataType.OCTET_STRING, it.did)
        return bb.array()

    def __getAvailableSwitches(self, settings):
        bb = MTByteBuffer()
        bb.setUInt8(DataType.ARRAY)
        if not self.availableSwitches:
            _MTCommon.setObjectCount(0, bb)
        else:
            _MTCommon.setObjectCount(len(self.availableSwitches), bb)
            for it in self.availableSwitches:
                bb.setUInt8(DataType.STRUCTURE)
                bb.setUInt8(5)
                _MTCommon.setData(settings, bb, DataType.OCTET_STRING, it.sna)
                _MTCommon.setData(settings, bb, DataType.INT16, it.lsId)
                _MTCommon.setData(settings, bb, DataType.INT8, it.level)
                _MTCommon.setData(settings, bb, DataType.INT8, it.rxLevel)
                _MTCommon.setData(settings, bb, DataType.INT8, it.rxSnr)
        return bb.array()

    def __getCommunications(self, settings):
        bb = MTByteBuffer()
        bb.setUInt8(DataType.ARRAY)
        if not self.communications:
            _MTCommon.setObjectCount(0, bb)
        else:
            _MTCommon.setObjectCount(len(self.communications), bb)
            for it in self.communications:
                bb.setUInt8(DataType.STRUCTURE)
                bb.setUInt8(9)
                _MTCommon.setData(settings, bb, DataType.OCTET_STRING, it.eui)
                _MTCommon.setData(settings, bb, DataType.INT8, it.txPower)
                _MTCommon.setData(settings, bb, DataType.INT8, it.txCoding)
                _MTCommon.setData(settings, bb, DataType.INT8, it.rxCoding)
                _MTCommon.setData(settings, bb, DataType.INT8, it.rxLvl)
                _MTCommon.setData(settings, bb, DataType.INT8, it.snr)
                _MTCommon.setData(settings, bb, DataType.INT8, it.txPowerModified)
                _MTCommon.setData(settings, bb, DataType.INT8, it.txCodingModified)
                _MTCommon.setData(settings, bb, DataType.INT8, it.rxCodingModified)
        return bb.array()

    #
    # Returns value of given attribute.
    #
    def getValue(self, settings, e):
        if e.index == 1:
            ret = _MTCommon.logicalNameToBytes(self.logicalName)
        elif e.index == 2:
            ret = self.__getMulticastEntries(settings)
        elif e.index == 3:
            ret = self.__getSwitchTable(settings)
        elif e.index == 4:
            ret = self.__getDirectTable(settings)
        elif e.index == 5:
            ret = self.__getAvailableSwitches(settings)
        elif e.index == 6:
            ret = self.__getCommunications(settings)
        else:
            ret = None
            e.error = ErrorCode.READ_WRITE_DENIED
        return ret

    @classmethod
    def __setMulticastEntry(cls, value):
        data = list()
        if value:
            for it in value:
                v = MTMacMulticastEntry()
                v.id = it[0]
                v.members = it[1]
                data.append(v)
        return data

    @classmethod
    def __setSwitchTable(cls, value):
        data = list()
        if value:
            for it in value:
                data.append(it)
        return data

    @classmethod
    def __setDirectTable(cls, value):
        data = list()
        if value:
            for it in value:
                v = MTMacDirectTable()
                v.sourceSId = it[0]
                v.sourceLnId = it[1]
                v.sourceLcId = it[2]
                v.destinationSId = it[3]
                v.destinationLnId = it[4]
                v.destinationLcId = it[5]
                v.did = it[6]
                data.append(v)
        return data

    @classmethod
    def __setAvailableSwitches(cls, value):
        data = list()
        if value:
            for it in value:
                v = MTMacAvailableSwitch()
                v.sna = it[0]
                v.lsId = it[1]
                v.level = it[2]
                v.rxLevel = it[3]
                v.rxSnr = it[4]
                data.append(v)
        return data

    @classmethod
    def __setCommunications(cls, value):
        data = list()
        if value:
            for it in value:
                v = MTMacPhyCommunication()
                v.eui = it[0]
                v.txPower = it[1]
                v.txCoding = it[2]
                v.rxCoding = it[3]
                v.rxLvl = it[4]
                v.snr = it[5]
                v.txPowerModified = it[6]
                v.txCodingModified = it[7]
                v.rxCodingModified = it[8]
                data.append(v)
        return data

    #
    # Set value of given attribute.
    #
    def setValue(self, settings, e):
        if e.index == 1:
            self.logicalName = _MTCommon.toLogicalName(e.value)
        elif e.index == 2:
            self.multicastEntries = self.__setMulticastEntry(e.value)
        elif e.index == 3:
            self.switchTable = self.__setSwitchTable(e.value)
        elif e.index == 4:
            self.directTable = self.__setDirectTable(e.value)
        elif e.index == 5:
            self.availableSwitches = self.__setAvailableSwitches(e.value)
        elif e.index == 6:
            self.communications = self.__setCommunications(e.value)
        else:
            e.error = ErrorCode.READ_WRITE_DENIED

    @classmethod
    def __loadMulticastEntries(cls, reader):
        list_ = list()
        if reader.isStartElement("MulticastEntries", True):
            while reader.isStartElement("Item", True):
                it = MTMacMulticastEntry()
                list_.append(it)
                it.id = reader.readElementContentAsInt("Id")
                it.members = reader.readElementContentAsInt("Members")
            reader.readEndElement("MulticastEntries")
        return list_

    @classmethod
    def __loadSwitchTable(cls, reader):
        list_ = list()
        if reader.isStartElement("SwitchTable", True):
            while reader.isStartElement("Item", False):
                list_.append(reader.readElementContentAsInt("Item"))
            reader.readEndElement("SwitchTable")
        return list_

    @classmethod
    def __loadDirectTable(cls, reader):
        list_ = list()
        if reader.isStartElement("DirectTable", True):
            while reader.isStartElement("Item", True):
                it = MTMacDirectTable()
                list_.append(it)
                it.sourceSId = reader.readElementContentAsInt("SourceSId")
                it.sourceLnId = reader.readElementContentAsInt("SourceLnId")
                it.sourceLcId = reader.readElementContentAsInt("SourceLcId")
                it.destinationSId = reader.readElementContentAsInt("DestinationSId")
                it.destinationLnId = reader.readElementContentAsInt("DestinationLnId")
                it.destinationLcId = reader.readElementContentAsInt("DestinationLcId")
                it.did = MTByteBuffer.hexToBytes(reader.readElementContentAsString("Did"))
            reader.readEndElement("DirectTable")
        return list_

    @classmethod
    def __loadAvailableSwitches(cls, reader):
        list_ = list()
        if reader.isStartElement("AvailableSwitches", True):
            while reader.isStartElement("Item", True):
                it = MTMacAvailableSwitch()
                list_.append(it)
                it.sna = MTByteBuffer.hexToBytes(reader.readElementContentAsString("Sna"))
                it.lsId = reader.readElementContentAsInt("LsId")
                it.level = reader.readElementContentAsInt("Level")
                it.rxLevel = reader.readElementContentAsInt("RxLevel")
                it.rxSnr = reader.readElementContentAsInt("RxSnr")
            reader.readEndElement("AvailableSwitches")
        return list_

    @classmethod
    def __loadCommunications(cls, reader):
        list_ = list()
        if reader.isStartElement("Communications", True):
            while reader.isStartElement("Item", True):
                it = MTMacPhyCommunication()
                list_.append(it)
                it.eui = MTByteBuffer.hexToBytes(reader.readElementContentAsString("Eui"))
                it.txPower = reader.readElementContentAsInt("TxPower")
                it.txCoding = reader.readElementContentAsInt("TxCoding")
                it.rxCoding = reader.readElementContentAsInt("RxCoding")
                it.rxLvl = reader.readElementContentAsInt("RxLvl")
                it.snr = reader.readElementContentAsInt("Snr")
                it.txPowerModified = reader.readElementContentAsInt("TxPowerModified")
                it.txCodingModified = reader.readElementContentAsInt("TxCodingModified")
                it.rxCodingModified = reader.readElementContentAsInt("RxCodingModified")
            reader.readEndElement("Communications")
        return list_

    def load(self, reader):
        self.multicastEntries = self.__loadMulticastEntries(reader)
        self.switchTable = self.__loadSwitchTable(reader)
        self.directTable = self.__loadDirectTable(reader)
        self.availableSwitches = self.__loadAvailableSwitches(reader)
        self.communications = self.__loadCommunications(reader)

    def __saveMulticastEntries(self, writer):
        writer.writeStartElement("MulticastEntries")
        if self.multicastEntries:
            for it in self.multicastEntries:
                writer.writeStartElement("Item")
                writer.writeElementString("Id", it.id)
                writer.writeElementString("Members", it.members)
                writer.writeEndElement()
        writer.writeEndElement()

    def __saveSwitchTable(self, writer):
        writer.writeStartElement("SwitchTable")
        if self.switchTable:
            for it in self.switchTable:
                writer.writeElementString("Item", it)
        writer.writeEndElement()

    def __saveDirectTable(self, writer):
        writer.writeStartElement("DirectTable")
        if self.directTable:
            for it in self.directTable:
                writer.writeStartElement("Item")
                writer.writeElementString("SourceSId", it.sourceSId)
                writer.writeElementString("SourceLnId", it.sourceLnId)
                writer.writeElementString("SourceLcId", it.sourceLcId)
                writer.writeElementString("DestinationSId", it.destinationSId)
                writer.writeElementString("DestinationLnId", it.destinationLnId)
                writer.writeElementString("DestinationLcId", it.destinationLcId)
                writer.writeElementString("Did", MTByteBuffer.hex(it.did, False))
                writer.writeEndElement()
        writer.writeEndElement()

    def __saveAvailableSwitches(self, writer):
        writer.writeStartElement("AvailableSwitches")
        if self.availableSwitches:
            for it in self.availableSwitches:
                writer.writeStartElement("Item")
                writer.writeElementString("Sna", MTByteBuffer.hex(it.sna, False))
                writer.writeElementString("LsId", it.lsId)
                writer.writeElementString("Level", it.level)
                writer.writeElementString("RxLevel", it.rxLevel)
                writer.writeElementString("RxSnr", it.rxSnr)
                writer.writeEndElement()
        writer.writeEndElement()

    def __saveCommunications(self, writer):
        writer.writeStartElement("Communications")
        if self.communications:
            for it in self.communications:
                writer.writeStartElement("Item")
                writer.writeElementString("Eui", MTByteBuffer.hex(it.eui, False))
                writer.writeElementString("TxPower", it.txPower)
                writer.writeElementString("TxCoding", it.txCoding)
                writer.writeElementString("RxCoding", it.rxCoding)
                writer.writeElementString("RxLvl", it.rxLvl)
                writer.writeElementString("Snr", it.snr)
                writer.writeElementString("TxPowerModified", it.txPowerModified)
                writer.writeElementString("TxCodingModified", it.txCodingModified)
                writer.writeElementString("RxCodingModified", it.rxCodingModified)
                writer.writeEndElement()
        writer.writeEndElement()

    def save(self, writer):
        self.__saveMulticastEntries(writer)
        self.__saveSwitchTable(writer)
        self.__saveDirectTable(writer)
        self.__saveAvailableSwitches(writer)
        self.__saveCommunications(writer)

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
from .TranslatorOutputType import TranslatorOutputType
from .enums.InterfaceType import InterfaceType
from .MTCiphering import MTCiphering
from .enums.AssociationResult import AssociationResult
from .enums.SourceDiagnostic import SourceDiagnostic
from .MTByteBuffer import MTByteBuffer
from .MTDLMSSettings import MTDLMSSettings
# pylint:disable=bad-option-value,old-style-class
class MTDLMSXmlSettings:
    #
    # Constructor.
    #
    # pylint: disable=too-many-instance-attributes
    #
    def __init__(self, type_, numericsAsHex, isHex, list_):
        self.settings = MTDLMSSettings(True)
        self.outputType = type_
        # Are numeric values shows as hex.
        self.showNumericsAsHex = self.outputType != TranslatorOutputType.STANDARD_XML and numericsAsHex
        self.showStringAsHex = isHex
        self.settings.interfaceType = InterfaceType.PDU
        self.settings.cipher = MTCiphering("ABCDEFGH".encode())
        self.tags = list_
        self.result = AssociationResult.ACCEPTED
        self.diagnostic = SourceDiagnostic.NONE
        self.reason = 0
        self.command = 0
        self.gwCommand = 0
        #  GW newtork ID.
        self.networkId = 0
        self.physicalDeviceAddress = []
        self.count = 0
        self.requestType = 0xFF
        self.attributeDescriptor = MTByteBuffer()
        self.data = MTByteBuffer()
        self.time = None
        # Is xml used as a reply template.
        self.template = False

    def parseInt(self, value):
        if not value:
            return 0
        if self.showNumericsAsHex:
            return int(value, 16)
        return int(value)

    def parseShort(self, value):
        if not value:
            return 0
        if self.showNumericsAsHex:
            return int(value, 16)
        return int(value)

    def parseLong(self, value):
        if not value:
            return 0
        if self.showNumericsAsHex:
            return int(value, 16)
        return int(value)

    #
    # the outputType
    #
    def getOutputType(self):
        return self.outputType

    def getNetworkId(self):
        return self.networkId

    def setNetworkId(self, value):
        self.networkId = value

    def getPhysicalDeviceAddress(self):
        return self.physicalDeviceAddress

    def setPhysicalDeviceAddress(self, value):
        self.physicalDeviceAddress = value

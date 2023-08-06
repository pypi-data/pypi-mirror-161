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
from .InactivityMode import InactivityMode
from .StartProtocolType import StartProtocolType
from .MTObisCodeCollection import MTObisCodeCollection
#
class MTManufacturer:
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        """
        Constructor.
        """
        self.inactivityMode = InactivityMode.KEEPALIVE
        self.useIEC47 = False
        self.forceInactivity = False
        self.useLogicalNameReferencing = False
        self.identification = None
        self.obisCodes = MTObisCodeCollection()
        self.name = None
        self.settings = list()
        self.serverSettings = list()
        self.keepAliveInterval = 40000
        self.startProtocol = StartProtocolType.IEC
        self.webAddress = None
        self.info = None


    def getServer(self, address):
        for it in self.serverSettings:
            if it.HDLCAddress == address:
                return it
        return None

    #
    # Get authentication settings.
    #
    # @param authentication
    #            Authentication type.
    # Authentication settings.
    #
    def getAuthentication(self, authentication):
        for it in self.settings:
            if it.type_ == authentication:
                return it
        return None

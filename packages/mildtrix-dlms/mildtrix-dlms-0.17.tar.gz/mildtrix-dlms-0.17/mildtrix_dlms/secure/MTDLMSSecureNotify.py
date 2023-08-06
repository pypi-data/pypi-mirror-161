#
#  --------------------------------------------------------------------------
#   mildtrix Ltd
#
#
#
#  Filename:        $HeadURL$
#
#  Version:         $Revision$,
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
from ..MTDLMSNotify import MTDLMSNotify
from ..MTCiphering import MTCiphering
#  This class is used to send data notify and push messages to the clients.
#
class MTDLMSSecureNotify(MTDLMSNotify):
    #
    #      * Constructor.
    #      *
    #      * @param useLogicalNameReferencing
    #      *            Is Logical Name referencing used.
    #      * @param clientAddress
    #      *            Server address.
    #      * @param serverAddress
    #      *            Client address.
    #      * @param interfaceType
    #      *            Object type.
    #
    def __init__(self, useLogicalNameReferencing, clientAddress, serverAddress, interfaceType):
        #pylint:disable=super-with-arguments
        super(MTDLMSSecureNotify, self).__init__(useLogicalNameReferencing, clientAddress, serverAddress, interfaceType)
        self.ciphering = MTCiphering("ABCDEFGH".encode())
        self.cipher = self.ciphering

    #
    #      * @return Ciphering settings.
    #
    def getCiphering(self):
        return self.ciphering

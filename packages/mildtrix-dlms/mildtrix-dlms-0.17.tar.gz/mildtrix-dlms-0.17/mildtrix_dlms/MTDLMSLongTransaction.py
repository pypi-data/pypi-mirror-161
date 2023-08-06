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
from .MTByteBuffer import MTByteBuffer
# Long get or set information is saved here.
#
class MTDLMSLongTransaction:
    #
    # Constructor.
    #
    # @param forTargets
    #            Targets.
    # @param forCommand
    #            Command.
    # @param forData
    #            Data.
    #
    def __init__(self, forTargets, forCommand, forData=None):
        # Targets.
        self.targets = forTargets
        # Executed command.
        self.command = forCommand
        # Extra data from PDU.
        self.data = MTByteBuffer()
        if forData:
            self.data.set(forData)

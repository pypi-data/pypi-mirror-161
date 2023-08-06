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
from ..MTByteBuffer import MTByteBuffer

###Python 2 requires this
#pylint: disable=bad-option-value,old-style-class,too-few-public-methods
class MTDLMSImageActivateInfo:
    def __init__(self, size=0, identification=None, signature=None):
        """
        Constructor.

        size: Size.
        identification: Identification.
        signature: Signature.
        """
        self.size = size
        self.identification = identification
        self.signature = signature

    def __str__(self):
        sb = ""
        if MTByteBuffer.isAsciiString(self.identification):
            sb += str(self.identification)
        else:
            sb += MTByteBuffer.hex(self.identification, True)
        sb += " "
        if MTByteBuffer.isAsciiString(self.signature):
            sb += str(self.signature)
        else:
            sb += MTByteBuffer.hex(self.signature, True)
        sb += " "
        sb += str(self.size)
        return sb

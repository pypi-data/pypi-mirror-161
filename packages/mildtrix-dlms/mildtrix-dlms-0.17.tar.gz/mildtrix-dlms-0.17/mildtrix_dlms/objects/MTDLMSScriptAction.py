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
from .enums import ScriptActionType
from ..enums import ObjectType
from ..enums import DataType
from ..MTByteBuffer import MTByteBuffer

#pylint: disable=bad-option-value,old-style-class,too-few-public-methods,too-many-instance-attributes
class MTDLMSScriptAction:
    #
    # Constructor.
    #
    def __init__(self):
        self.type_ = ScriptActionType.NOTHING
        self.objectType = ObjectType.NONE
        self.parameterDataType = DataType.NONE
        # Executed object.
        self.target = None
        self.logicalName = None
        self.index = 0
        self.parameter = None

    def __str__(self):
        tmp = None
        if isinstance(self.parameter, bytearray):
            tmp = MTByteBuffer.hex(self.parameter, True)
        else:
            tmp = str(self.parameter)
        if self.target:
            return self.type_.__str__() + " " + str(self.target.objectType) + " " + self.target.logicalName + " " + str(self.index) + " " + tmp
        return self.type_.__str__() + " " + str(self.objectType) + " " + self.logicalName + " " + str(self.index) + " " + tmp

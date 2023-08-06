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
from .enums import DataType

# pylint: disable=bad-option-value,old-style-class,too-few-public-methods
class MTWriteItem:
    #
    # Constructor.
    #
    # @param object
    #            Object to write.
    # @param attributeIndex
    #            Attribute index.
    #
    def __init__(self, object_=None, attributeIndex=0):
        self.dataType = DataType.NONE
        self.target = object_
        # Attribute index to write.
        self.index = attributeIndex
        # Written object.
        self.target = None
        # Data type to write.
        self.dataType = None
        # Parameter selector.
        self.selector = 0
        # Optional parameters.
        self.parameters = None

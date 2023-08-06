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
from .MTIntEnum import MTIntEnum

class ActionRequestType(MTIntEnum):
    """
    Enumerates Action request types.
    """

    #Normal action.
    NORMAL = 1

    #Next block.
    NEXT_BLOCK = 2

    #Action with list.
    WITH_LIST = 3

    #Action with first block.
    WITH_FIRST_BLOCK = 4

    #Action with list and first block.
    WITH_LIST_AND_FIRST_BLOCK = 5

    #Action with block.
    WITH_BLOCK = 6

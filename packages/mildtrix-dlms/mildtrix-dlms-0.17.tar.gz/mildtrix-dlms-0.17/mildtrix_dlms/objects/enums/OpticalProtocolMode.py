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
from mildtrix_dlms.MTIntEnum import MTIntEnum

class OpticalProtocolMode(MTIntEnum):
    """
    Defines the protocol used by the meter on the port.
    """
    #pylint: disable=too-few-public-methods

    #
    # Protocol according to IEC 62056-21 (modes A-E)
    #
    DEFAULT = 0
    #
    # Protocol according to IEC 62056-46.  Using this enumeration value all
    # other attributes of this IC are not applicable.
    #
    NET = 1
    #
    # Protocol not specified.  Using this enumeration value, ProposedBaudrate
    # is
    # used for setting the communication speed on the port.  All other
    # attributes are not applicable.
    #
    UNKNOWN = 2

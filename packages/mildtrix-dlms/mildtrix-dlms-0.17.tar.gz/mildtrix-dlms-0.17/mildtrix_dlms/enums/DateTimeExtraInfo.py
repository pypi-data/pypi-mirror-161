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
#  Copyright =c mildtrix Ltd
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
from ..MTIntFlag import MTIntFlag

class DateTimeExtraInfo(MTIntFlag):
    """Date time extra info."""
    #pylint: disable=too-few-public-methods

    # No extra info.
    NONE = 0
    # Daylight savings begin.
    DST_BEGIN = 0x1
    # Daylight savings end.
    DST_END = 0x2
    # Last day of month.
    LAST_DAY = 0x4
    # 2nd last day of month
    LAST_DAY2 = 0x8

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
from mildtrix_dlms.MTIntFlag import MTIntFlag

class CreditConfiguration(MTIntFlag):
    """
    Enumerated Credit configuration values.
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSAccount
    """
    #pylint: disable=too-few-public-methods

	#
    # None.
    #
    NONE = 0x0

	#
    # Requires visual indication.
    #
    VISUAL = 0x1

    #
    # Requires confirmation before it can be selected/invoked
    #
    CONFIRMATION = 0x2

    #
    # Requires the credit amount to be paid back.
    #
    PAID_BACK = 0x4

    #
    # Resettable.
    #
    RESETTABLE = 0x8

    #
    # Able to receive credit amounts from tokens.
    #
    TOKENS = 0x10

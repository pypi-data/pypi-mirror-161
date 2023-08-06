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

class AccountCreditStatus(MTIntFlag):
    """Enumerates account credit status modes.
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSAccount
    """
    #pylint: disable=too-few-public-methods

    #
    # In credit.
    #
    IN_CREDIT = 0x1

    #
    # Low credit.
    #
    LOW_CREDIT = 0x2

    #
    # Next credit enabled.
    #
    NEXT_CREDIT_ENABLED = 0x4

    #
    # Next credit selectable.
    #
    NEXT_CREDIT_SELECTABLE = 0x8

    #
    # Credit reference list.
    #
    CREDIT_REFERENCE_LIST = 0x10

    #
    # Selectable credit in use.
    #
    SELECTABLE_CREDIT_IN_USE = 0x20

    #
    # Out of credit.
    #
    OUT_OF_CREDIT = 0x40

    #
    # Reserved.
    #
    RESERVED = 0x80

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

class TokenStatusCode(MTIntEnum):
    """Enumerates token status codes.
    Online help:
    http://www.mildtrix.fi/mildtrix.DLMS.Objects.MTDLMSTokenGateway
    """
    #pylint: disable=too-few-public-methods

    #
    # Token format result OK.
    #
    FORMAT_OK = 0
    #
    # Authentication result OK.
    #
    AUTHENTICATION_OK = 1
    #
    # Validation result OK.
    #
    VALIDATION_OK = 2
    #
    # Token execution result OK.
    #
    TOKEN_EXECUTION_OK = 3
    #
    # Token format failure.
    #
    TOKEN_FORMAT_FAILURE = 4
    #
    # Authentication failure.
    #
    AUTHENTICATION_FAILURE = 5
    #
    # Validation result failure.
    #
    VALIDATION_RESULT_FAILURE = 6
    #
    # Token execution result failure.
    #
    TOKEN_EXECUTION_RESULT_FAILURE = 7
    #
    # Token received and not yet processed.
    #
    TOKEN_RECEIVED = 8

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
from ..MTIntEnum import MTIntEnum

class ApplicationReference(MTIntEnum):
    """
    Application reference describes application errors.
    """
    #pylint: disable=too-few-public-methods

    # Other error is occurred.
    OTHER = 0

    # Time elapsed.
    TIME_ELAPSED = 1

    # Application unreachable.
    APPLICATION_UNREACHABLE = 2

    # Application reference is invalid.
    APPLICATION_REFERENCE_INVALID = 3

    # Application context unsupported.
    APPLICATION_CONTEXT_UNSUPPORTED = 4

    # Provider communication error.
    PROVIDER_COMMUNICATION_ERROR = 5

    # Deciphering error.
    DECIPHERING_ERROR = 6

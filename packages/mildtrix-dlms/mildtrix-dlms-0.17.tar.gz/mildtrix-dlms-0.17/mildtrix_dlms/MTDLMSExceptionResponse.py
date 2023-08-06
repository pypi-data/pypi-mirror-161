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
from .enums.StateError import StateError
from .enums.ExceptionServiceError import ExceptionServiceError

class MTDLMSExceptionResponse(Exception):
    """
    DLMS specific exception class that has error description available from getDescription method.
    """

    #
    # Constructor for Confirmed ServiceError.
    #
    # @param service
    # @param type
    # @param value
    #
    def __init__(self, error=None, type_=None, value=0):
        Exception.__init__(self, self.__getStateError(error) + ". " + self.__getServiceError(type_))
        self.exceptionStateError = error
        self.exceptionServiceError = type_
        self.serviceErrorValue = value

    @classmethod
    def __getStateError(cls, stateError):
        str_ = ""
        if stateError == StateError.SERVICE_NOT_ALLOWED:
            str_ = "Service not allowed"
        elif stateError == StateError.SERVICE_UNKNOWN:
            str_ = "Service unknown"
        return str_

    @classmethod
    def __getServiceError(cls, error):
        str_ = ""
        if error == ExceptionServiceError.OPERATION_NOT_POSSIBLE:
            str_ = "Operation not possible"
        elif error == ExceptionServiceError.SERVICE_NOT_SUPPORTED:
            str_ = "Service not supported"
        elif error == ExceptionServiceError.OTHER_REASON:
            str_ = "Other reason"
        elif error == ExceptionServiceError.PDU_TOO_LONG:
            str_ = "PDU is too long"
        elif error == ExceptionServiceError.DECIPHERING_ERROR:
            str_ = "Ciphering failed"
        elif error == ExceptionServiceError.INVOCATION_COUNTER_ERROR:
            str_ = "Invocation counter is invalid."
        return str_

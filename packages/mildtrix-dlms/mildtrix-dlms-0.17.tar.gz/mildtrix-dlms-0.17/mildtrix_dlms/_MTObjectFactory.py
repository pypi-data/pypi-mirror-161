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
from .enums import ObjectType
#pylint: disable=bad-option-value,too-many-locals,
#cyclic-import,old-style-class,too-few-public-methods
from .objects.MTDLMSAssociationLogicalName import MTDLMSAssociationLogicalName
from .objects.MTDLMSObject import MTDLMSObject
from .objects.MTDLMSActionSchedule import MTDLMSActionSchedule
from .objects.MTDLMSActivityCalendar import MTDLMSActivityCalendar
from .objects.MTDLMSAssociationShortName import MTDLMSAssociationShortName
from .objects.MTDLMSAutoAnswer import MTDLMSAutoAnswer
from .objects.MTDLMSAutoConnect import MTDLMSAutoConnect
from .objects.MTDLMSClock import MTDLMSClock
from .objects.MTDLMSData import MTDLMSData
from .objects.MTDLMSDemandRegister import MTDLMSDemandRegister
from .objects.MTDLMSMacAddressSetup import MTDLMSMacAddressSetup
from .objects.MTDLMSRegister import MTDLMSRegister
from .objects.MTDLMSExtendedRegister import MTDLMSExtendedRegister
from .objects.MTDLMSGprsSetup import MTDLMSGprsSetup
from .objects.MTDLMSHdlcSetup import MTDLMSHdlcSetup
from .objects.MTDLMSIECLocalPortSetup import MTDLMSIECLocalPortSetup
from .objects.MTDLMSIecTwistedPairSetup import MTDLMSIecTwistedPairSetup
from .objects.MTDLMSIp4Setup import MTDLMSIp4Setup
from .objects.MTDLMSIp6Setup import MTDLMSIp6Setup
from .objects.MTDLMSMBusSlavePortSetup import MTDLMSMBusSlavePortSetup
from .objects.MTDLMSImageTransfer import MTDLMSImageTransfer
from .objects.MTDLMSSecuritySetup import MTDLMSSecuritySetup
from .objects.MTDLMSDisconnectControl import MTDLMSDisconnectControl
from .objects.MTDLMSLimiter import MTDLMSLimiter

from .objects.MTDLMSMBusClient import MTDLMSMBusClient
from .objects.MTDLMSModemConfiguration import MTDLMSModemConfiguration
from .objects.MTDLMSPppSetup import MTDLMSPppSetup
from .objects.MTDLMSProfileGeneric import MTDLMSProfileGeneric
from .objects.MTDLMSRegisterMonitor import MTDLMSRegisterMonitor
from .objects.MTDLMSRegisterActivation import MTDLMSRegisterActivation
from .objects.MTDLMSSapAssignment import MTDLMSSapAssignment
from .objects.MTDLMSSchedule import MTDLMSSchedule
from .objects.MTDLMSScriptTable import MTDLMSScriptTable
from .objects.MTDLMSSpecialDaysTable import MTDLMSSpecialDaysTable
from .objects.MTDLMSTcpUdpSetup  import MTDLMSTcpUdpSetup
from .objects.MTDLMSPushSetup import MTDLMSPushSetup
from .objects.MTDLMSMBusMasterPortSetup import MTDLMSMBusMasterPortSetup
from .objects.MTDLMSGSMDiagnostic import MTDLMSGSMDiagnostic
from .objects.MTDLMSAccount import MTDLMSAccount
from .objects.MTDLMSCredit import MTDLMSCredit
from .objects.MTDLMSCharge import MTDLMSCharge
from .objects.MTDLMSTokenGateway import MTDLMSTokenGateway
from .objects.MTDLMSParameterMonitor import MTDLMSParameterMonitor
from .objects.MTDLMSUtilityTables import MTDLMSUtilityTables
from .objects.MTDLMSLlcSscsSetup import MTDLMSLlcSscsSetup
from .objects.MTDLMSPrimeNbOfdmPlcPhysicalLayerCounters import MTDLMSPrimeNbOfdmPlcPhysicalLayerCounters
from .objects.MTDLMSPrimeNbOfdmPlcMacSetup import MTDLMSPrimeNbOfdmPlcMacSetup
from .objects.MTDLMSPrimeNbOfdmPlcMacFunctionalParameters import MTDLMSPrimeNbOfdmPlcMacFunctionalParameters
from .objects.MTDLMSPrimeNbOfdmPlcMacCounters import MTDLMSPrimeNbOfdmPlcMacCounters
from .objects.MTDLMSPrimeNbOfdmPlcMacNetworkAdministrationData import MTDLMSPrimeNbOfdmPlcMacNetworkAdministrationData
from .objects.MTDLMSPrimeNbOfdmPlcApplicationsIdentification import MTDLMSPrimeNbOfdmPlcApplicationsIdentification
from .objects.MTDLMSNtpSetup import MTDLMSNtpSetup

class _MTObjectFactory:
    #Reserved for internal use.

    #
    # Constructor.
    def __init__(self):
        pass

    @classmethod
    def createObject(cls, ot):
        #pylint: disable=bad-option-value,redefined-variable-type
        #  If IC is manufacturer specific or unknown.
        if ot is None:
            raise ValueError("Invalid object type.")

        if ot == ObjectType.ACTION_SCHEDULE:
            ret = MTDLMSActionSchedule()
        elif ot == ObjectType.ACTIVITY_CALENDAR:
            ret = MTDLMSActivityCalendar()
        elif ot == ObjectType.ASSOCIATION_LOGICAL_NAME:
            ret = MTDLMSAssociationLogicalName()
        elif ot == ObjectType.ASSOCIATION_SHORT_NAME:
            ret = MTDLMSAssociationShortName()
        elif ot == ObjectType.AUTO_ANSWER:
            ret = MTDLMSAutoAnswer()
        elif ot == ObjectType.AUTO_CONNECT:
            ret = MTDLMSAutoConnect()
        elif ot == ObjectType.CLOCK:
            ret = MTDLMSClock()
        elif ot == ObjectType.DATA:
            ret = MTDLMSData()
        elif ot == ObjectType.DEMAND_REGISTER:
            ret = MTDLMSDemandRegister()
        elif ot == ObjectType.MAC_ADDRESS_SETUP:
            ret = MTDLMSMacAddressSetup()
        elif ot == ObjectType.REGISTER:
            ret = MTDLMSRegister()
        elif ot == ObjectType.EXTENDED_REGISTER:
            ret = MTDLMSExtendedRegister()
        elif ot == ObjectType.GPRS_SETUP:
            ret = MTDLMSGprsSetup()
        elif ot == ObjectType.IEC_HDLC_SETUP:
            ret = MTDLMSHdlcSetup()
        elif ot == ObjectType.IEC_LOCAL_PORT_SETUP:
            ret = MTDLMSIECLocalPortSetup()
        elif ot == ObjectType.IEC_TWISTED_PAIR_SETUP:
            ret = MTDLMSIecTwistedPairSetup()
        elif ot == ObjectType.IP4_SETUP:
            ret = MTDLMSIp4Setup()
        elif ot == ObjectType.IP6_SETUP:
            ret = MTDLMSIp6Setup()
        elif ot == ObjectType.MBUS_SLAVE_PORT_SETUP:
            ret = MTDLMSMBusSlavePortSetup()
        elif ot == ObjectType.IMAGE_TRANSFER:
            ret = MTDLMSImageTransfer()
        elif ot == ObjectType.SECURITY_SETUP:
            ret = MTDLMSSecuritySetup()
        elif ot == ObjectType.DISCONNECT_CONTROL:
            ret = MTDLMSDisconnectControl()
        elif ot == ObjectType.LIMITER:
            ret = MTDLMSLimiter()
        elif ot == ObjectType.MBUS_CLIENT:
            ret = MTDLMSMBusClient()
        elif ot == ObjectType.MODEM_CONFIGURATION:
            ret = MTDLMSModemConfiguration()
        elif ot == ObjectType.PPP_SETUP:
            ret = MTDLMSPppSetup()
        elif ot == ObjectType.PROFILE_GENERIC:
            ret = MTDLMSProfileGeneric()
        elif ot == ObjectType.REGISTER_MONITOR:
            ret = MTDLMSRegisterMonitor()
        elif ot == ObjectType.REGISTER_ACTIVATION:
            ret = MTDLMSRegisterActivation()
        elif ot == ObjectType.REGISTER_TABLE:
            ret = MTDLMSObject(ot)
        elif ot == ObjectType.ZIG_BEE_SAS_STARTUP:
            ret = MTDLMSObject(ot)
        elif ot == ObjectType.ZIG_BEE_SAS_JOIN:
            ret = MTDLMSObject(ot)
        elif ot == ObjectType.SAP_ASSIGNMENT:
            ret = MTDLMSSapAssignment()
        elif ot == ObjectType.SCHEDULE:
            ret = MTDLMSSchedule()
        elif ot == ObjectType.SCRIPT_TABLE:
            ret = MTDLMSScriptTable()
        elif ot == ObjectType.SPECIAL_DAYS_TABLE:
            ret = MTDLMSSpecialDaysTable()
        elif ot == ObjectType.STATUS_MAPPING:
            ret = MTDLMSObject(ot)
        elif ot == ObjectType.TCP_UDP_SETUP:
            ret = MTDLMSTcpUdpSetup()
        elif ot == ObjectType.ZIG_BEE_SAS_APS_FRAGMENTATION:
            ret = MTDLMSObject(ot)
        elif ot == ObjectType.UTILITY_TABLES:
            ret = MTDLMSUtilityTables()
        elif ot == ObjectType.PUSH_SETUP:
            ret = MTDLMSPushSetup()
        elif ot == ObjectType.MBUS_MASTER_PORT_SETUP:
            ret = MTDLMSMBusMasterPortSetup()
        elif ot == ObjectType.GSM_DIAGNOSTIC:
            ret = MTDLMSGSMDiagnostic()
        elif ot == ObjectType.ACCOUNT:
            ret = MTDLMSAccount()
        elif ot == ObjectType.CREDIT:
            ret = MTDLMSCredit()
        elif ot == ObjectType.CHARGE:
            ret = MTDLMSCharge()
        elif ot == ObjectType.TOKEN_GATEWAY:
            ret = MTDLMSTokenGateway()
        elif ot == ObjectType.PARAMETER_MONITOR:
            ret = MTDLMSParameterMonitor()
        elif ot == ObjectType.LLC_SSCS_SETUP:
            ret = MTDLMSLlcSscsSetup()
        elif ot == ObjectType.PRIME_NB_OFDM_PLC_PHYSICAL_LAYER_COUNTERS:
            ret = MTDLMSPrimeNbOfdmPlcPhysicalLayerCounters()
        elif ot == ObjectType.PRIME_NB_OFDM_PLC_MAC_SETUP:
            ret = MTDLMSPrimeNbOfdmPlcMacSetup()
        elif ot == ObjectType.PRIME_NB_OFDM_PLC_MAC_FUNCTIONAL_PARAMETERS:
            ret = MTDLMSPrimeNbOfdmPlcMacFunctionalParameters()
        elif ot == ObjectType.PRIME_NB_OFDM_PLC_MAC_COUNTERS:
            ret = MTDLMSPrimeNbOfdmPlcMacCounters()
        elif ot == ObjectType.PRIME_NB_OFDM_PLC_MAC_NETWORK_ADMINISTRATION_DATA:
            ret = MTDLMSPrimeNbOfdmPlcMacNetworkAdministrationData()
        elif ot == ObjectType.PRIME_NB_OFDM_PLC_APPLICATIONS_IDENTIFICATION:
            ret = MTDLMSPrimeNbOfdmPlcApplicationsIdentification()
        elif ot == ObjectType.NTP_SETUP:
            ret = MTDLMSNtpSetup()
        else:
            ret = MTDLMSObject(ot)
        return ret

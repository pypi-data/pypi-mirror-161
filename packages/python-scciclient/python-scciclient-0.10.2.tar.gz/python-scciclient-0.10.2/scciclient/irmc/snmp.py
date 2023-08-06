# Copyright 2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from pysnmp import error as snmp_error
from pysnmp import hlapi as snmp
import six


BMC_NAME_OID = '1.3.6.1.4.1.231.2.10.2.2.10.3.4.1.3.1.1'
IRMC_FW_VERSION_OID = '1.3.6.1.4.1.231.2.10.2.2.10.3.4.1.4.1.1'
BIOS_FW_VERSION_OID = '1.3.6.1.4.1.231.2.10.2.2.10.4.1.1.11.1'
SERVER_MODEL_OID = '1.3.6.1.4.1.231.2.10.2.2.10.2.3.1.4.1'

SNMP_V1 = '1'
SNMP_V2C = '2c'
SNMP_V3 = '3'

SNMP_FAILURE_MSG = "SNMP operation '%s' failed: %s"


class SNMPFailure(Exception):
    """SNMP Failure

    This exception is used when invalid inputs are passed to
    the APIs exposed by this module.
    """
    def __init__(self, message):
        super(SNMPFailure, self).__init__(message)


class SNMPIRMCFirmwareFailure(SNMPFailure):
    """SNMP iRMC Firmware Failure

    This exception is used when error occurs when collecting iRMC firmware.
    """
    def __init__(self, message):
        super(SNMPIRMCFirmwareFailure, self).__init__(message)


class SNMPBIOSFirmwareFailure(SNMPFailure):
    """SNMP BIOS Firmware Failure

    This exception is used when error occurs when collecting BIOS firmware.
    """
    def __init__(self, message):
        super(SNMPBIOSFirmwareFailure, self).__init__(message)


class SNMPServerModelFailure(SNMPFailure):
    """SNMP Server Model Failure

    This exception is used when error occurs when collecting server model.
    """
    def __init__(self, message):
        super(SNMPServerModelFailure, self).__init__(message)


def get_irmc_firmware_version(snmp_client):
    """Get irmc firmware version of the node.

    :param snmp_client: an SNMP client object.
    :raises: SNMPFailure if SNMP operation failed.
    :returns: a string of bmc name and irmc firmware version.
    """

    try:
        bmc_name = snmp_client.get(BMC_NAME_OID)
        irmc_firm_ver = snmp_client.get(IRMC_FW_VERSION_OID)
        return ('%(bmc)s%(sep)s%(firm_ver)s' %
                {'bmc': bmc_name if bmc_name else '',
                 'firm_ver': irmc_firm_ver if irmc_firm_ver else '',
                 'sep': '-' if bmc_name and irmc_firm_ver else ''})
    except SNMPFailure as e:
        raise SNMPIRMCFirmwareFailure(
            SNMP_FAILURE_MSG % ("GET IRMC FIRMWARE VERSION", e))


def get_bios_firmware_version(snmp_client):
    """Get bios firmware version of the node.

    :param snmp_client: an SNMP client object.
    :raises: SNMPFailure if SNMP operation failed.
    :returns: a string of bios firmware version.
    """

    try:
        bios_firmware_version = snmp_client.get(BIOS_FW_VERSION_OID)
        return six.text_type(bios_firmware_version)
    except SNMPFailure as e:
        raise SNMPBIOSFirmwareFailure(
            SNMP_FAILURE_MSG % ("GET BIOS FIRMWARE VERSION", e))


def get_server_model(snmp_client):
    """Get server model of the node.

    :param snmp_client: an SNMP client object.
    :raises: SNMPFailure if SNMP operation failed.
    :returns: a string of server model.
    """

    try:
        server_model = snmp_client.get(SERVER_MODEL_OID)
        return six.text_type(server_model)
    except SNMPFailure as e:
        raise SNMPServerModelFailure(
            SNMP_FAILURE_MSG % ("GET SERVER MODEL", e))


class SNMPClient(object):
    """SNMP client object.

    Performs low level SNMP get and set operations. Encapsulates all
    interaction with PySNMP to simplify dynamic importing and unit testing.
    """

    def __init__(self, address, port, version,
                 read_community=None, write_community=None,
                 user=None, auth_proto=None, auth_key=None,
                 priv_proto=None, priv_key=None,
                 context_engine_id=None, context_name=None):
        self.address = address
        self.port = port
        self.version = version
        if self.version == SNMP_V3:
            self.user = user
            self.auth_proto = auth_proto
            self.auth_key = auth_key
            self.priv_proto = priv_proto
            self.priv_key = priv_key
        else:
            self.read_community = read_community
            self.write_community = write_community

        self.context_engine_id = context_engine_id
        self.context_name = context_name or ''
        self.snmp_engine = snmp.SnmpEngine()

    def _get_auth(self, write_mode=False):
        """Return the authorization data for an SNMP request.

        :param write_mode: `True` if write class SNMP command is
            executed. Default is `False`.
        :returns: Either
            :class:`pysnmp.hlapi.CommunityData`
            or :class:`pysnmp.hlapi.UsmUserData`
            object depending on SNMP version being used.
        """
        if self.version == SNMP_V3:
            # Handling auth/encryption credentials is not (yet) supported.
            # This version supports a security name analogous to community.
            return snmp.UsmUserData(self.user,
                                    authKey=self.auth_key,
                                    authProtocol=self.auth_proto,
                                    privKey=self.priv_key,
                                    privProtocol=self.priv_proto)
        else:
            mp_model = 1 if self.version == SNMP_V2C else 0
            return snmp.CommunityData(
                self.write_community if write_mode else self.read_community,
                mpModel=mp_model
            )

    def _get_transport(self):
        """Return the transport target for an SNMP request.

        :returns: A :class:
            `pysnmp.hlapi.UdpTransportTarget` object.
        :raises: :class:`pysnmp.error.PySnmpError` if the transport address
            is bad.
        """
        # The transport target accepts timeout and retries parameters, which
        # default to 1 (second) and 5 respectively. These are deemed sensible
        # enough to allow for an unreliable network or slow device.
        return snmp.UdpTransportTarget((self.address, self.port))

    def _get_context(self):
        """Return the SNMP context for an SNMP request.

        :returns: A :class:
            `pysnmp.hlapi.ContextData` object.
        :raises: :class:`pysnmp.error.PySnmpError` if SNMP context data
            is bad.
        """
        return snmp.ContextData(contextEngineId=self.context_engine_id,
                                contextName=self.context_name)

    def get(self, oid):
        """Use PySNMP to perform an SNMP GET operation on a single object.

        :param oid: The OID of the object to get.
        :raises: SNMPFailure if an SNMP request fails.
        :returns: The value of the requested object.
        """
        try:
            snmp_gen = snmp.getCmd(self.snmp_engine,
                                   self._get_auth(),
                                   self._get_transport(),
                                   self._get_context(),
                                   snmp.ObjectType(snmp.ObjectIdentity(oid)))
        except snmp_error.PySnmpError as e:
            raise SNMPFailure(SNMP_FAILURE_MSG % ("GET", e))

        error_indication, error_status, error_index, var_binds = next(snmp_gen)

        if error_indication:
            # SNMP engine-level error.
            raise SNMPFailure(SNMP_FAILURE_MSG % ("GET", error_indication))

        if error_status:
            # SNMP PDU error.
            raise SNMPFailure(
                "SNMP operation '%(operation)s' failed: %(error)s at"
                " %(index)s" %
                {'operation': "GET", 'error': error_status.prettyPrint(),
                 'index':
                     error_index and var_binds[int(error_index) - 1] or '?'})

        # We only expect a single value back
        name, val = var_binds[0]
        return val

    def get_next(self, oid):
        """Use PySNMP to perform an SNMP GET NEXT operation on a table object.

        :param oid: The OID of the object to get.
        :raises: SNMPFailure if an SNMP request fails.
        :returns: A list of values of the requested table object.
        """
        try:
            snmp_gen = snmp.nextCmd(self.snmp_engine,
                                    self._get_auth(),
                                    self._get_transport(),
                                    self._get_context(),
                                    snmp.ObjectType(snmp.ObjectIdentity(oid)),
                                    lexicographicMode=False)
        except snmp_error.PySnmpError as e:
            raise SNMPFailure(SNMP_FAILURE_MSG % ("GET_NEXT", e))

        vals = []
        for (error_indication, error_status, error_index,
                var_binds) in snmp_gen:
            if error_indication:
                # SNMP engine-level error.
                raise SNMPFailure(SNMP_FAILURE_MSG % ("GET_NEXT",
                                                      error_indication))

            if error_status:
                # SNMP PDU error.
                raise SNMPFailure(
                    "SNMP operation '%(operation)s' failed: %(error)s at"
                    " %(index)s" %
                    {'operation': "GET_NEXT",
                     'error': error_status.prettyPrint(),
                     'index':
                        error_index and var_binds[int(error_index) - 1]
                        or '?'})

            name, value = var_binds[0]
            vals.append(value)

        return vals

    def set(self, oid, value):
        """Use PySNMP to perform an SNMP SET operation on a single object.

        :param oid: The OID of the object to set.
        :param value: The value of the object to set.
        :raises: SNMPFailure if an SNMP request fails.
        """
        try:
            snmp_gen = snmp.setCmd(self.snmp_engine,
                                   self._get_auth(write_mode=True),
                                   self._get_transport(),
                                   self._get_context(),
                                   snmp.ObjectType(snmp.ObjectIdentity(oid),
                                                   value))
        except snmp_error.PySnmpError as e:
            raise SNMPFailure(SNMP_FAILURE_MSG % ("SET", e))

        error_indication, error_status, error_index, var_binds = next(snmp_gen)

        if error_indication:
            # SNMP engine-level error.
            raise SNMPFailure(SNMP_FAILURE_MSG % ("SET", error_indication))

        if error_status:
            # SNMP PDU error.
            raise SNMPFailure(
                "SNMP operation '%(operation)s' failed: %(error)s at"
                " %(index)s" %
                {'operation': "SET", 'error': error_status.prettyPrint(),
                 'index':
                     error_index and var_binds[int(error_index) - 1] or '?'})

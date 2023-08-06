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

"""
Test class for snmp module.
"""

from unittest import mock

from pysnmp import error as snmp_error
from pysnmp import hlapi as pysnmp
import testtools

from scciclient.irmc import snmp


class IRMCSnmpTestCase(testtools.TestCase):
    """Tests for SNMP module

    Unit Test Cases for getting information via snmp module
    """

    def setUp(self):
        super(IRMCSnmpTestCase, self).setUp()

    def test_get_irmc_firmware_version(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = ['iRMC S4', '7.82F']
        cmd1 = snmp.BMC_NAME_OID
        cmd2 = snmp.IRMC_FW_VERSION_OID
        actual_out = snmp.get_irmc_firmware_version(snmp_client)
        self.assertEqual('iRMC S4-7.82F', actual_out)
        snmp_client.get.assert_has_calls([mock.call(cmd1),
                                          mock.call(cmd2)])

    def test_get_irmc_firmware_version_BMC_only(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = ['iRMC S4', '']
        cmd1 = snmp.BMC_NAME_OID
        cmd2 = snmp.IRMC_FW_VERSION_OID
        actual_out = snmp.get_irmc_firmware_version(snmp_client)
        self.assertEqual('iRMC S4', actual_out)
        snmp_client.get.assert_has_calls([mock.call(cmd1),
                                          mock.call(cmd2)])

    def test_get_irmc_firmware_version_FW_only(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = ['', '7.82F']
        cmd1 = snmp.BMC_NAME_OID
        cmd2 = snmp.IRMC_FW_VERSION_OID
        actual_out = snmp.get_irmc_firmware_version(snmp_client)
        self.assertEqual('7.82F', actual_out)
        snmp_client.get.assert_has_calls([mock.call(cmd1),
                                          mock.call(cmd2)])

    def test_get_irmc_firmware_version_blank(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = ['', '']
        cmd1 = snmp.BMC_NAME_OID
        cmd2 = snmp.IRMC_FW_VERSION_OID
        actual_out = snmp.get_irmc_firmware_version(snmp_client)
        self.assertEqual('', actual_out)
        snmp_client.get.assert_has_calls([mock.call(cmd1),
                                          mock.call(cmd2)])

    def test_get_irmc_firmware_version_exception(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = snmp.SNMPFailure('Error')
        cmd1 = snmp.BMC_NAME_OID
        e = self.assertRaises(snmp.SNMPIRMCFirmwareFailure,
                              snmp.get_irmc_firmware_version,
                              snmp_client)
        snmp_client.get.assert_has_calls([mock.call(cmd1)])
        self.assertEqual('SNMP operation \'GET IRMC FIRMWARE VERSION\''
                         ' failed: Error', str(e))

    def test_get_bios_firmware_version(self):
        snmp_client = mock.Mock()
        snmp_client.return_value = 'V4.6.5.4 R1.15.0 for D3099-B1x'
        snmp_client.get.return_value = 'V4.6.5.4 R1.15.0 for D3099-B1x'
        cmd = snmp.BIOS_FW_VERSION_OID
        actual_out = snmp.get_bios_firmware_version(snmp_client)
        self.assertEqual('V4.6.5.4 R1.15.0 for D3099-B1x', actual_out)
        snmp_client.get.assert_called_once_with(cmd)

    def test_get_bios_firmware_version_exception(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = snmp.SNMPFailure('Error')
        cmd = snmp.BIOS_FW_VERSION_OID
        e = self.assertRaises(snmp.SNMPBIOSFirmwareFailure,
                              snmp.get_bios_firmware_version,
                              snmp_client)
        snmp_client.get.assert_called_once_with(cmd)
        self.assertEqual('SNMP operation \'GET BIOS FIRMWARE VERSION\''
                         ' failed: Error', str(e))

    def test_get_server_model(self):
        snmp_client = mock.Mock()
        snmp_client.return_value = 'TX2540M1F5'
        snmp_client.get.return_value = 'TX2540M1F5'
        cmd = snmp.SERVER_MODEL_OID
        actual_out = snmp.get_server_model(snmp_client)
        self.assertEqual('TX2540M1F5', actual_out)
        snmp_client.get.assert_called_once_with(cmd)

    def test_get_server_model_exception(self):
        snmp_client = mock.Mock()
        snmp_client.get.side_effect = snmp.SNMPFailure('Error')
        cmd = snmp.SERVER_MODEL_OID
        e = self.assertRaises(snmp.SNMPServerModelFailure,
                              snmp.get_server_model,
                              snmp_client)
        snmp_client.get.assert_called_once_with(cmd)
        self.assertEqual('SNMP operation \'GET SERVER MODEL\''
                         ' failed: Error', str(e))


class SNMPClientTestCase(testtools.TestCase):
    def setUp(self):
        super(SNMPClientTestCase, self).setUp()
        self.address = '1.2.3.4'
        self.port = '6700'
        self.oid = 'oid'
        self.value = 'value'

    @mock.patch.object(pysnmp, 'SnmpEngine', authspec=True)
    def test___init__(self, mock_snmpengine):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V1)
        mock_snmpengine.assert_called_once_with()
        self.assertEqual(self.address, client.address)
        self.assertEqual(self.port, client.port)
        self.assertEqual(snmp.SNMP_V1, client.version)
        self.assertIsNone(client.read_community)
        self.assertIsNone(client.write_community)
        self.assertNotIn('user', client.__dict__)
        self.assertEqual(mock_snmpengine.return_value, client.snmp_engine)

    @mock.patch.object(pysnmp, 'CommunityData', autospec=True)
    def test__get_auth_v1_read(self, mock_community):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V1,
                                 read_community='public',
                                 write_community='private')
        client._get_auth()
        mock_community.assert_called_once_with(client.read_community,
                                               mpModel=0)

    @mock.patch.object(pysnmp, 'CommunityData', autospec=True)
    def test__get_auth_v1_write(self, mock_community):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V1,
                                 read_community='public',
                                 write_community='private')
        client._get_auth(write_mode=True)
        mock_community.assert_called_once_with(client.write_community,
                                               mpModel=0)

    @mock.patch.object(pysnmp, 'CommunityData', autospec=True)
    def test__get_auth_v2c(self, mock_community):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V2C)
        client._get_auth()
        mock_community.assert_called_once_with(client.read_community,
                                               mpModel=1)

    @mock.patch.object(pysnmp, 'UsmUserData', autospec=True)
    def test__get_auth_v3(self, mock_user):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        client._get_auth()
        mock_user.assert_called_once_with(client.user,
                                          authKey=client.auth_key,
                                          authProtocol=client.auth_proto,
                                          privKey=client.priv_key,
                                          privProtocol=client.priv_proto)

    @mock.patch.object(pysnmp, 'UdpTransportTarget', autospec=True)
    def test__get_transport(self, mock_transport):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        client._get_transport()
        mock_transport.assert_called_once_with((client.address, client.port))

    @mock.patch.object(pysnmp, 'UdpTransportTarget', autospec=True)
    def test__get_transport_err(self, mock_transport):
        mock_transport.side_effect = snmp_error.PySnmpError
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp_error.PySnmpError, client._get_transport)
        mock_transport.assert_called_once_with((client.address, client.port))

    @mock.patch.object(pysnmp, 'ContextData', authspec=True)
    def test__get_context(self, mock_context):
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V1)
        client._get_context()
        mock_context.assert_called_once_with(contextEngineId=None,
                                             contextName='')

    @mock.patch.object(pysnmp, 'getCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_get(self, mock_auth, mock_context, mock_transport,
                 mock_getcmd):
        var_bind = (self.oid, self.value)
        mock_getcmd.return_value = iter([("", None, 0, [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        val = client.get(self.oid)
        self.assertEqual(var_bind[1], val)
        self.assertEqual(1, mock_getcmd.call_count)

    @mock.patch.object(pysnmp, 'nextCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_get_next(self, mock_auth, mock_context, mock_transport,
                      mock_nextcmd):
        var_bind = (self.oid, self.value)
        mock_nextcmd.return_value = iter([("", None, 0, [var_bind]),
                                          ("", None, 0, [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        val = client.get_next(self.oid)
        self.assertEqual([self.value, self.value], val)
        self.assertEqual(1, mock_nextcmd.call_count)

    @mock.patch.object(pysnmp, 'getCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_get_err_transport(self, mock_auth, mock_context, mock_transport,
                               mock_getcmd):
        mock_transport.side_effect = snmp_error.PySnmpError
        var_bind = (self.oid, self.value)
        mock_getcmd.return_value = iter([("engine error", None, 0,
                                         [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp.SNMPFailure, client.get, self.oid)
        self.assertFalse(mock_getcmd.called)

    @mock.patch.object(pysnmp, 'nextCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_get_next_err_transport(self, mock_auth, mock_context,
                                    mock_transport, mock_nextcmd):
        mock_transport.side_effect = snmp_error.PySnmpError
        var_bind = (self.oid, self.value)
        mock_nextcmd.return_value = iter([("engine error", None, 0,
                                         [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp.SNMPFailure, client.get_next, self.oid)
        self.assertFalse(mock_nextcmd.called)

    @mock.patch.object(pysnmp, 'getCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_get_err_engine(self, mock_auth, mock_context, mock_transport,
                            mock_getcmd):
        var_bind = (self.oid, self.value)
        mock_getcmd.return_value = iter([("engine error", None, 0,
                                         [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp.SNMPFailure, client.get, self.oid)
        self.assertEqual(1, mock_getcmd.call_count)

    @mock.patch.object(pysnmp, 'nextCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_get_next_err_engine(self, mock_auth, mock_context, mock_transport,
                                 mock_nextcmd):
        var_bind = (self.oid, self.value)
        mock_nextcmd.return_value = iter([("engine error", None, 0,
                                         [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp.SNMPFailure, client.get_next, self.oid)
        self.assertEqual(1, mock_nextcmd.call_count)

    @mock.patch.object(pysnmp, 'setCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_set(self, mock_auth, mock_context, mock_transport,
                 mock_setcmd):
        var_bind = (self.oid, self.value)
        mock_setcmd.return_value = iter([("", None, 0, [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        client.set(self.oid, self.value)
        self.assertEqual(1, mock_setcmd.call_count)

    @mock.patch.object(pysnmp, 'setCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_set_err_transport(self, mock_auth, mock_context, mock_transport,
                               mock_setcmd):
        mock_transport.side_effect = snmp_error.PySnmpError
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp.SNMPFailure,
                          client.set, self.oid, self.value)
        self.assertFalse(mock_setcmd.called)

    @mock.patch.object(pysnmp, 'setCmd', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_transport', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_context', authspec=True)
    @mock.patch.object(snmp.SNMPClient, '_get_auth', authspec=True)
    def test_set_err_engine(self, mock_auth, mock_context, mock_transport,
                            mock_setcmd):
        var_bind = (self.oid, self.value)
        mock_setcmd.return_value = iter([("engine error", None, 0,
                                         [var_bind])])
        client = snmp.SNMPClient(self.address, self.port, snmp.SNMP_V3)
        self.assertRaises(snmp.SNMPFailure,
                          client.set, self.oid, self.value)
        self.assertEqual(1, mock_setcmd.call_count)

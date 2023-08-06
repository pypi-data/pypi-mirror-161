""" Interface for the Nordic Access Point. """
from copy import deepcopy
from logging import getLogger
from uuid import uuid4
from struct import pack_into, calcsize

from conductor.airfinder.devices.access_point import AccessPoint, AccessPointMessageSpecV1_1_0, CommandBase
from conductor.airfinder.messages import ControlMessageNotSupported, MissingDownlinkArgument
from conductor.util import Version

LOG = getLogger(__name__)


class AntennaPort(CommandBase):
    """ Which Antenna Port to Utilize. """
    ANT_A = 0
    ANT_B = 1


class ApType(CommandBase):
    """ Whether an AP will function as a Location or an Access Point. """
    CONNECTABLE = 0x0,
    LOCATION = 0x01


class ScanMode(CommandBase):
    """ Types of Scans the AP can perform for GWs. """
    NORMAL = 0x01,
    INFO = 0x02


class VFotaSpread(CommandBase):
    """ How to spread the image when transferring a viral Fota image. """
    TERMINAL = 0x00
    VIRAL = 0x01


class VFotaImageSource(CommandBase):
    """ Where the viral Fota will source its image from. """
    DEV_FLASH = 0x00
    SPI_FLASH = 0x01


class VFotaTestState(CommandBase):
    """ The resultant state of the test downlink. """
    PASS = 0x00
    RETRY = 0x01
    FAIL = 0x02


class NordicAPMessageSpecV2_0_0(AccessPointMessageSpecV1_1_0):
    """ Message Spec for the Access Point v2.0.0 """

    def __init__(self):
        super().__init__()
        self.header.update({
            'def': ['msg_type', 'msg_spec_vers_major', 'msg_spec_vers_minor', 'msg_spec_vers_tag', 'msg_len'],
            'struct': '>BBBBB',
            'defaults': [None, 0x02, 0x00, 0x00, None]
        })

        self.msg_types.update({
            'ConfigurationQuery': {
                'type': 0xA1,
                'def': ['uuid'],
                'struct': 'I'
            }
        })
        self.control_types = deepcopy(self.control_types)
        self.control_types.update({
            'CONFIG_BLE_FRONT_END': {
                'type': 0x010A,
                'def': ['config'],
                'struct': '>B'
            },
            'SAMPLE_BATT': {
                'type': 0x0103
            },
            'SET_DST': {
                'type': 0x0021,
                'def': ['enable'],
                'struct': '>B'
            },
            'SET_DUTY_CYCLE': {
                'type': 0x0022,
                'def': ['window'],
                'struct': '>B'
            }
        })


class NordicAPMessageSpecV2_0_1(NordicAPMessageSpecV2_0_0):
    """ Message Spec for the Access Point v2.0.1 """

    def __init__(self):
        super().__init__()
        self.header['defaults'] = [None, 0x02, 0x00, 0x01, None]
        self.control_types = deepcopy(self.control_types)
        self.control_types.update({
            'SET_NET_TOKEN': {
                'type': 0x0001,
                'def': ['net_tok'],
                'struct': '>I',
                'defaults': [0x4f50454e]
            },
            'SET_DL_BAND': {
                'type': 0x00A0,
                'def': ['band_edge_lower', 'band_edge_upper',
                        'band_edge_guard', 'band_edge_ch_step',
                        'band_edge_ch_offset'],
                'struct': '>IIIBB'
            },
            'SET_DS_NET_TOKEN': {
                'type': 0x00A1,
                'def': ['net_tok'],
                'struct': '>I',
                'defaults': [0x4f50454e]
            },
        })


class NordicAPMessageSpecV2_0_2(NordicAPMessageSpecV2_0_1):
    """ Message Spec for the Access Point v2.0.2 """

    def __init__(self):
        super().__init__()
        self.header['defaults'] = [None, 0x02, 0x00, 0x02, None]
        self.control_types = deepcopy(self.control_types)
        self.control_types.update({
            'SET_NORDIC_GW_RSSI': {
                'type': 0x00B0,
                'def': ['rssi'],
                'struct': '>i'
            },
            'SET_SYM_SCAN_MODE': {
                'type': 0x00B1,
                'def': ['mode'],
                'struct': '>H'
            },
            'SET_SYM_SCAN_ATTEMPTS': {
                'type': 0x00B2,
                'def': ['attempts'],
                'struct': '>B'
            },
            'SET_SYM_HOP_INT': {
                'type': 0x00B3,
                'def': ['interval'],
                'struct': '>I'
            },
            'SET_MAX_GW_ERROR': {
                'type': 0x00B4,
                'def': ['max_err'],
                'struct': '>B'
            },
            'SET_SYM_INFO_SCAN_INT': {
                'type': 0x00B5,
                'def': ['interval'],
                'struct': '>I'
            },
            'SET_SYM_GW_RSSI': {
                'type': 0x00B0,
                'def': ['rssi'],
                'struct': '>H'
            },
            'TRIGGER_BOOTLOADER': {
                'type': 0x0600,
                'def': ['hash'],
                'struct': '>I'
            },
            'GET_NORDIC_MAC': {
                'type': 0x0601,
                'def': ['mac'],
                'struct': '>h'
            }
        })


class NordicAPMessageSpecV2_0_3(NordicAPMessageSpecV2_0_2):
    """ Message Spec for the Access Point v2.0.3 """

    def __init__(self):
        super().__init__()
        self.header['defaults'] = [None, 0x02, 0x00, 0x03, None]


class NordicAPMessageSpecV2_0_4(NordicAPMessageSpecV2_0_3):
    """ Message Spec for the Access Point v2.0.4 """

    def __init__(self):
        super().__init__()
        self.header['defaults'] = [None, 0x02, 0x00, 0x04, None]
        self.control_types = deepcopy(self.control_types)
        self.control_types.update({
            'vFOTA_CONTROL': {
                'type': 0x0602,
                'def': ['version', 'command', 'data'],
                'struct': '>BB{}s'
            },
            'TRIGGER_BOOTLOADER': {
                'type': 0x0604,
                'def': ['interval'],
                'struct': '>I'
            }
        })
        self.vfota_version = 0
        self.vfota_control_types = {
            'UPDATE': {
                'type': 0x01,
                'def': ['file_version', 'file_id', 'time_to_live', 'length_of_target_list', 'spread_image', 'img_src',
                        'scan_target', 'target_list'],
                'struct': '>IIHBBB4s{}s'
            },
            "CANCEL": {
                'type': 0x02,
            },
            "FW_ID_REQ": {
                'type': 0x03,
            },
            "PROCESS_REPORT_REQ": {
                'type': 0x04,
            },
            "TEST_MODE": {
                'type': 0x05,
                'def': ['state'],
                'struct': '>B'
            },
            "DEVICE_REPORT_REQ": {
                'type': 0x06,
            },
            "DAT_FILE_REQ": {
                'type': 0x07,
                'def': ['dat_length', 'dat_file'],
                'struct': '>B{}s'
            },
            "STATUS_REQ": {
                'type': 0x08,
            }
        }

    def build_vfota_message(self, ctrl_cmd, **kwargs):

        ctrl_msg = self.vfota_control_types.get(ctrl_cmd)
        if not ctrl_msg:
            raise ControlMessageNotSupported()

        ctrl_def = ctrl_msg.get('def')
        ctrl_struct = ctrl_msg.get('struct')
        cmd = ctrl_msg.get('type')
        buff = None

        # Determine size of variable target list, when applicable.
        if ctrl_def:
            if "target_list" in ctrl_def:
                ctrl_struct = ctrl_struct.format(kwargs.get("length_of_target_list")*6)
            if "dat_file" in ctrl_def:
                ctrl_struct = ctrl_struct.format(kwargs.get("dat_length"))

        if ctrl_def and ctrl_struct:
            ctrl_len = calcsize(ctrl_struct)
            buff = bytearray(b'\x00' * ctrl_len)
            w_list = []

            # Build Control Message
            for i in range(len(ctrl_def)):
                key = ctrl_def[i]
                val = kwargs.get(key)

                if val is None:
                    raise MissingDownlinkArgument(key)
                else:
                    LOG.debug("{}: {} [SPECIFIED]".format(key, val))

                w_list.append(val)
                LOG.debug(w_list)

            LOG.debug("Writing: {} into {}".format(w_list, ctrl_struct))
            pack_into(ctrl_struct, buff, 0, *w_list)

        return self.build_ctrl_message("vFOTA_CONTROL", version=self.vfota_version, command=cmd, data=buff)


class NordicAPMessageSpecV2_0_5(NordicAPMessageSpecV2_0_4):
    """ Message Spec for the Access Point v2.0.5 """

    def __init__(self):
        super().__init__()
        self.header['defaults'] = [None, 0x02, 0x00, 0x05, None]


class NordicAccessPoint(AccessPoint):

    ###########################################################################
    # Nordic Access Point Properties.
    ###########################################################################

    application = 'c47e949cc0428bdac390'

    @property
    def msg_spec_version(self):
        """ Message Spec Version of the AP """
        major = self._md.get('msgSpecVersionMajor')
        minor = self._md.get('msgSpecVersionMinor')
        tag = self._md.get('msgSpecVersionTag')
        if not major or not minor or not tag:
            return Version(2, 0, 0)
        return Version(int(major), int(minor), int(tag))

    @property
    def bootloader_version(self):
        """ Message Spec Version of the AP """
        major = self._md.get('symbleAPBootloaderVersionMajor')
        minor = self._md.get('symbleAPBootloaderVersionMinor')
        tag = self._md.get('symbleAPBootloaderVersionTag')
        if not major or not minor or not tag:
            # Check legacy keys
            vers = self._md.get("bootloaderVersion")
            if not vers:
                return None  # No version found.
            v = "{:08x}".format(vers)
            return Version(int(v[:2], 16), int(v[2:4], 16), int(v[4:], 16))
        return Version(int(major), int(minor), int(tag))

    @property
    def dfu_app_file_id(self):
        return self._make_prop("", str)

    @property
    def dfu_target(self):
        return self._make_prop('targetAddress', str)

    @property
    def dfu_state(self):
        return self._make_prop('symDfuState', str)

    @property
    def dfu_stop_reason(self):
        return self._make_prop('stopReason', str)

    @property
    def dfu_status(self):
        return self._make_prop('status', str)

    @property
    def scan_attempts(self):
        return self._make_prop('scanAttempts', str)

    @property
    def scan_mode(self):
        return self._make_prop('scanMode', str)

    @property
    def scan_response_name(self):
        return self._make_prop('scanResponseName', str)

    @property
    def dfu_passed_units(self):
        return self._make_prop('passedUpdates', int)

    @property
    def dfu_percentage(self):
        return self._make_prop('percentComplete', int)

    @property
    def dfu_ext_err_code(self):
        return self._make_prop('extendedErrorCode', int)

    @property
    def dfu_failed_updates(self):
        return self._make_prop('failedUpdates', int)

    @property
    def dfu_file_id(self):
        header_file_id = self._md.get("spiHeaderFileID")
        if header_file_id is not None:
            return header_file_id
        return self._md.get('fileID')

    @property
    def dfu_file_version(self):
        version = self._md.get('spiHeaderVersion')
        if version is not None:
            v = "{:08X}".format(version)
            # v = hex(int(version))[2:]
        if version is None:
            v = self._md.get('version')
        try:
            return Version(int(v[:2], 16), int(v[2:4], 16), int(v[4:], 16)) if v else None
        except IndexError:
            return None

    @property
    def dfu_result(self):
        return self._make_prop('dfuResult', int)

    @property
    def dfu_app_file_version(self):
        v = self._md.get('appVersion')
        major, minor, tag = v[:2], v[2:4], v[4:]
        try:
            # Expect value in decimal.
            return Version(major, minor, tag) if v else None
        except ValueError:
            # Values need to be parsed from hex.
            return Version(int(major, 16), int(minor, 16), int(tag, 16))
        except IndexError:
            return None  # No version string to parse.

    @classmethod
    def _get_spec(cls, vers):
        if vers == Version(2, 0, 0):
            return NordicAPMessageSpecV2_0_0()
        elif vers == Version(2, 0, 1):
            return NordicAPMessageSpecV2_0_1()
        elif vers == Version(2, 0, 2):
            return NordicAPMessageSpecV2_0_2()
        elif vers == Version(2, 0, 3):
            return NordicAPMessageSpecV2_0_3()
        elif vers == Version(2, 0, 4):
            return NordicAPMessageSpecV2_0_4()
        elif vers == Version(2, 0, 5):
            return NordicAPMessageSpecV2_0_5()
        else:
            raise Exception("Unsupported Message Specification!")

    ###########################################################################
    # Configuration Methods.
    ###########################################################################

    def send_configuration_query(self, gateway_addr=None, time_to_live_s=60.0, port=0, priority=10):
        """ Sends a message targeted at the SymBLE endnode to the AP.

        Args:
            uuid (bytearray):
                A Universally Unique Id, to prevent the symble endnodes from
                receiving the same message more than once.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class`conductor.subject.DownlinkMessage`

        """
        # TODO: Not unit-tested.
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message('ConfigurationQuery',
                                                 uuid=uuid4().fields[0])
        return self.send_message(pld, gateway_addr=gateway_addr, time_to_live_s=time_to_live_s, port=port,
                                 priority=priority)

    @classmethod
    def multicast_configuration_query(cls, time_to_live_s, vers, gateways):
        """ Sends a message targeted at the SymBLE endnode to the AP.

        Args:
            uuid (bytearray):
                A Universally Unique Id, to prevent the symble endnodes from
                receiving the same message more than once.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class`conductor.subject.DownlinkMessage`

        """
        # TODO: Not unit-tested.
        pld = cls._get_spec(vers).build_message('ConfigurationQuery', uuid=uuid4().fields[0])
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def config_ble_front_end(self, enable, antenna, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0,
                             priority=10):
        """
        Sends a CONFIG_BLE_FRONT_END message

        Args:
            enable (bool): True if front-end is to be enabled.
            antenna (:type`.AntennaPort`): Antenna port setting
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        val = 0x01 if enable else 0x00
        val += 0x02 if antenna == AntennaPort.ANT_B else 0x00
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("CONFIG_BLE_FRONT_END", config=val)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_config_ble_front_end(cls, enable, antenna, time_to_live_s, vers, gateways):
        """
        Sends a CONFIG_BLE_FRONT_END message

        Args:
            enable (bool): True if front-end is to be enabled.
            antenna (:type`.AntennaPort`): Antenna port setting
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.


            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        val = 0x01 if enable else 0x00
        val += 0x02 if antenna == AntennaPort.ANT_B else 0x00
        pld = cls._get_spec(vers).build_ctrl_message("CONFIG_BLE_FRONT_END",
                                                     config=val)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def sample_batt(self, gateway_addr=None, acked=True, time_to_live_s=60.0,
                    port=0, priority=10):
        """
        Sends a SAMPLE_BATT message

        Args:
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SAMPLE_BATT")
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_sample_batt(cls, time_to_live_s, vers, gateways):
        """
        Sends a SAMPLE_BATT message

        Args:
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        pld = cls._get_spec(vers).build_ctrl_message("SAMPLE_BATT")
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_duty_cycle(self, duty_cycle, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_DUTY_CYCLE message. Number of minutes in a single window (1 hr.) that the AP should be active.
        Default = 60 mins.

        Args:
            duty_cycle (int): AP Window Duty Cycle (active minutes per hour, range 0-60)
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if duty_cycle > 60:
            raise ValueError('Sync duty cycle cannot be > 60!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_DUTY_CYCLE", window=duty_cycle)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_sync_duty_cycle(cls, duty_cycle, time_to_live_s, vers, gateways, port=0, priority=10):
        """
        Sends a SET_SYNC_DC message

        Args:
            duty_cycle (int): The Sync Advertisement Duty Cycle.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.


            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if duty_cycle > 60:
            raise ValueError('Sync duty cycle cannot be > 60!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_DUTY_CYCLE", window=duty_cycle)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def sync_duty_cycle(self, duty_cycle, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_SYNC_DC message

        Args:
            duty_cycle (int): The Sync Advertisement Duty Cycle.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if duty_cycle > 3:
            raise ValueError('Sync duty cycle cannot be > 3 (10/100)!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_SYNC_DC", sync=duty_cycle)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_set_duty_cycle(cls, duty_cycle, time_to_live_s, vers, gateways, port=0, priority=10):
        """
        Sends a SET_SYNC_DC message

        Args:
            duty_cycle (int): The Sync Advertisement Duty Cycle.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.


            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if duty_cycle > 3:
            raise ValueError('Sync duty cycle cannot be > 3 (10/100)!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_SYNC_DC", sync=duty_cycle)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_sym_info_scan_int(self, interval, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_SYM_GW_RSSI message

        Args:
            interval (int): The number of seconds to wait before performing an information scan.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if interval < 1800 or interval > 4294967:
            raise ValueError('Interval must be within 1800 and 4294967!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_SYM_INFO_SCAN_INT", interval=interval)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_set_sym_info_scan_int(cls, interval, time_to_live_s, vers, gateways):
        """
        Sends a SET_SYM_INFO_SCAN_INT message

        Args:
            interval (int): The number of seconds to wait before performing an information scan.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if interval < 1800 or interval > 4294967:
            raise ValueError('Interval must be within 1800 and 4294967!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_SYM_INFO_SCAN_INT", interval=interval)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_sym_gw_rssi(self, rssi, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_SYM_GW_RSSI message

        Args:
            rssi (int): The minimum RSSI to connnect to a Gateway.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if rssi < -121 or rssi > -40:
            raise ValueError('RSSI must be within -121 and -40!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_SYM_GW_RSSI", rssi=rssi)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_set_sym_gw_rssi(cls, rssi, time_to_live_s, vers, gateways):
        """
        Sends a SET_SYM_GW_RSSI message

        Args:
            rssi (int): The minimum RSSI to connnect to a Gateway.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if rssi < -121 or rssi > -40:
            raise ValueError('RSSI must be within -121 and -40!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_SYM_GW_RSSI",
                                                     rssi=rssi)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_nordic_gw_rssi(self, rssi, gateway_addr=None, acked=True,
                           time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_NORDIC_GW_RSSI message

        Args:
            rssi (int): The minimum RSSI to connnect to a Gateway.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """

        if rssi < -121 or rssi > -40:
            raise ValueError('RSSI must be within -121 and -40!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_NORDIC_GW_RSSI",
                                                      rssi=rssi)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_nordic_gw_rssi(cls, rssi, time_to_live_s, vers, gateways):
        """
        Sends a SET_NORDIC_GW_RSSI message

        Args:
            rssi (int): The minimum RSSI to connnect to a Gateway.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if rssi < -121 or rssi > -40:
            raise ValueError('RSSI must be within -121 and -40!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_NORDIC_GW_RSSI",
                                                     rssi=rssi)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_scan_mode(self, scan_mode, gateway_addr=None, acked=True,
                      time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_SYM_SCAN_MODE message

        Args:
            scan_mode (int): The ScanMode of the Module.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if not ScanMode.has_value(scan_mode):
            raise ValueError('Scan mode must be in ScanMode Enum!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_SYM_SCAN_MODE",
                                                      mode=scan_mode)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_scan_mode(cls, scan_mode, time_to_live_s, vers,
                                gateways):
        """
        Sends a SET_SYM_SCAN_MODE message

        Args:
            scan_mode (int): The ScanMode of the Module.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if not ScanMode.has_value(scan_mode):
            raise ValueError('Scan mode must be in ScanMode Enum!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_SYM_SCAN_MODE",
                                                     mode=scan_mode)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_max_scan_attempts(self, attempts, gateway_addr=None, acked=True,
                              time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_SYM_SCAN_ATTEMPTS message

        Args:
            attempts (int): The maximum amount of scan attempts.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if attempts < 2 or attempts > 10:
            raise ValueError('Scan attempts must be between 2 and 10!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_SYM_SCAN_ATTEMPTS",
                                                      attempts=attempts)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_max_scan_attempts(cls, attempts, time_to_live_s, vers, gateways):
        """
        Sends a SET_SYM_SCAN_ATTEMPTS message

        Args:
            attempts (int): The maximum amount of scan attempts.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.


            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if attempts < 2 or attempts > 10:
            raise ValueError('Scan attempts must be between 2 and 10!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_SYM_SCAN_ATTEMPTS",
                                                     attempts=attempts)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_hop_interval(self, interval, gateway_addr=None, acked=True,
                         time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_SYM_HOP_INT message

        Args:
            interval (int): The interval to connect to a new gateway.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if interval < 600 or interval > 1382400:
            raise ValueError('Hop Interval must range from 600 - 1382400'
                             ' seconds (16 days)!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_SYM_HOP_INT",
                                                      interval=interval)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_hop_interval(cls, interval, time_to_live_s, vers,
                                   gateways):
        """
        Sends a SET_SYM_HOP_INT message

        Args:
            interval (int): The interval to connect to a new gateway.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if interval < 600 or interval > 1382400:
            raise ValueError('Hop Interval must range from 600 - 1382400'
                             ' seconds (16 days)!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_SYM_HOP_INT",
                                                     interval=interval)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_max_gw_errors(self, errors, gateway_addr=None, acked=True,
                          time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a SET_MAX_GW_ERROR message

        Args:
            errors (int): The maxmimum amount of errors the AP will accept
                before switching gateways.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if errors < 2 or errors > 50:
            raise ValueError('Error must be from (2-50)!')
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_MAX_GW_ERROR",
                                                      max_err=errors)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_max_gw_errors(cls, errors, time_to_live_s, vers,
                                    gateways):
        """
        Sends a SET_MAX_GW_ERROR message

        Args:
            errors (int): The maxmimum amount of errors the AP will accept
                before switching gateways.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if errors < 2 or errors > 50:
            raise ValueError('Error must be from (2-50)!')
        pld = cls._get_spec(vers).build_ctrl_message("SET_MAX_GW_ERROR", max_err=errors)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_network_token(self, net_tok, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Sets the Network Token of the Access Point.

        Args:
            net_tok(int): The network token that the AccessPoint should have.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_NET_TOKEN",
                                                      net_tok=net_tok)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_network_token(cls, net_tok, time_to_live_s, vers,
                                    gateways):
        """ Sets the Network Token of many Access Points.

        Args:
            net_tok(int): The network token that the AccessPoint should have.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        pld = cls._get_spec(vers).build_ctrl_message("SET_NET_TOKEN",
                                                     net_tok=net_tok)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_dl_band(self, edge_lower, edge_upper, edge_guard, edge_ch_step,
                    edge_ch_offset, gateway_addr=None, acked=True,
                    time_to_live_s=60.0, port=0, priority=10):
        """
        Sets the Downlink Link Band Configuration for the Symphony Link Module.

        Args:
            edge_lower (int): band edge lower frequency.
            edge_upper (int): band edge upper frequency.
            edge_guard (int): band edge guard.
            step_size (int): channel step size.
            step_offset: (int) channel step offset.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message(
                "SET_DL_BAND", band_edge_lower=edge_lower,
                band_edge_upper=edge_upper,
                band_edge_guard=edge_guard,
                band_edge_ch_step=edge_ch_step,
                band_edge_ch_offset=edge_ch_offset)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s,
                                 port, priority)

    @classmethod
    def multicast_set_dl_band(cls, edge_lower, edge_upper, edge_guard,
                              edge_ch_step, edge_ch_offset, time_to_live_s,
                              vers, gateways):
        """
        Sets the Downlink Link Band Configuration for the Symphony Link Module.

        Args:
            edge_lower (int): band edge lower frequency.
            edge_upper (int): band edge upper frequency.
            edge_guard (int): band edge guard.
            step_size (int): channel step size.
            step_offset: (int) channel step offset.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        pld = cls._get_spec(vers).build_ctrl_message(
                "SET_DL_BAND", band_edge_lower=edge_lower,
                band_edge_upper=edge_upper,
                band_edge_guard=edge_guard,
                band_edge_ch_step=edge_ch_step,
                band_edge_ch_offset=edge_ch_offset)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def set_ds_network_token(self, net_tok, gateway_addr=None, acked=True,
                             time_to_live_s=60.0, port=0, priority=10):
        """
        Sets the SymBLE Network Token that SymBLE Endnodes see when
        connecting to an Access Point.

        Args:
            net_tok(int): The downstream network token.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route
                the DownlinkMessage through the given gateway address when
                supplied. Defaults to `None` to send through all possible
                routes.
            acked (bool): [Optional] Determines whether the AccessPoint will
                return an acknowledgement upon receiving the DownlinkMessage.
                Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the
                DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the
                message. Higher priority messages will be sent before lower
                priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_ctrl_message("SET_DS_NET_TOKEN", net_tok=net_tok)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_set_ds_network_token(cls, net_tok, time_to_live_s, vers, gateways):
        """
        Sets the SymBLE Network Token that SymBLE Endnodes see when
        connecting to an Access Point.

        Args:
            net_tok(int): The downstream network token.
            time_to_live_s (int): [Optional] The number of seconds that the
                AccessPoint has to check its mailbox before the message becomes
                `expired` and will no longer be valid to send to the
                AccessPoint. Defaults to 60 seconds, one minute.
            vers (:class:`.Version`): The AP message spec version of the
                message to build.
            gateways (list): The list of :class:`.Gateway` objects that
                should receive the multicast message.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        pld = cls._get_spec(vers).build_ctrl_message("SET_DS_NET_TOKEN", net_tok=net_tok)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_update(self, file_id, file_version, targets, time_to_live, spread_image, image_source, scan_target,
                     gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Initialize a viral Firmware-Over-The-Air transfer from Access Point to SymBLE endnode or Access Point.

        Args:
            file_id (int): Unique file identifier, representing the firmware image being sent.
            file_version (:class:`.Version`): File Version of the file_id, that is being sent.
            targets (list): List of mac addresses to target the viral FOTA at.
            time_to_live (int): The number of minutes to let the viral FOTA go before terminating.
            spread_image (:class:`.VFotaSpread`): To continue to spread image, or not.
            image_source (:class:`.VFotaImageSource`): To clone own flash, or use Network FOTA image.
            scan_target (str): Prefix to filter for when using viral Fota.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        # Device Validation
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        # Parameter Validation
        if len(targets) > 10:
            raise Exception("Too many targets! Cannot fit target list in downlink payload.")
        if not isinstance(spread_image, VFotaSpread):
            raise ValueError("`spread_image` must be of type `nordic_access_point.VFotaSpread`.")
        if not isinstance(image_source, VFotaImageSource):
            raise ValueError("`image_source` must be of type `nordic_access_point.VFotaImageSource`.")
        spec = self._get_spec(self.msg_spec_version)
        target_list = bytearray.fromhex("".join([target.replace(':', '') for target in targets]))
        pld = spec.build_vfota_message("UPDATE", file_id=file_id, file_version=file_version.to_int(),
                                       spread_image=int(spread_image), img_src=int(image_source),
                                       target_list=target_list, time_to_live=time_to_live,
                                       length_of_target_list=len(targets),
                                       scan_target=scan_target)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_update(cls, file_id, file_version, targets, time_to_live, spread_image, image_source,
                               scan_target, vers, gateways, time_to_live_s=60.0):
        """ Initialize a viral Firmware-Over-The-Air transfer from Access Point to SymBLE endnode or Access Point.

        Args:
            file_id (int): Unique file identifier, representing the firmware image being sent.
            file_version (:class:`.Version`): File Version of the file_id, that is being sent.
            targets (list): List of mac addresses to target the viral FOTA at.
            time_to_live (int): The number of minutes to let the viral FOTA go before terminating.
            spread_image (:class:`.VFotaSpread`): To continue to spread image, or not.
            image_source (:class:`.VFotaImageSource`): To clone own flash, or use Network FOTA image.
            scan_target (str): Prefix to filter for when using viral Fota.
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        # Device Validation
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        # Parameter Validation
        if len(targets) > 17:
            raise Exception("Too many targets! Cannot fit target list in downlink payload.")
        if not isinstance(spread_image, VFotaSpread):
            raise ValueError("`spread_image` must be of type `nordic_access_point.VFotaSpread`.")
        if not isinstance(image_source, VFotaImageSource):
            raise ValueError("`image_source` must be of type `nordic_access_point.VFotaImageSource`.")
        spec = cls._get_spec(vers)
        target_list = bytearray.fromhex("".join([target.replace(':', '') for target in targets]))
        pld = spec.build_vfota_message("UPDATE", file_id=file_id, file_version=file_version.to_bytes(),
                                       spread_image=spread_image, image_source=image_source, target_list=target_list,
                                       time_to_live=time_to_live, length_of_target_list=len(targets),
                                       scan_target=scan_target)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_cancel(self, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Cancel a viral Firmware-Over-The-Air transfer from Access Point to SymBLE endnode or Access Point.

        Args:
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = self._get_spec(self.msg_spec_version)
        pld = spec.build_vfota_message("CANCEL")
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_cancel(cls, vers, gateways, time_to_live_s=60.0):
        """ Cancel a viral Firmware-Over-The-Air transfer from Access Point to SymBLE endnode or Access Point.

        Args:
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = cls._get_spec(vers)
        pld = spec.build_vfota_message("CANCEL")
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_request_firmware_id(self, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Requests the firmware ID of the firmware on the Access Point.

        Args:
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = self._get_spec(self.msg_spec_version)
        pld = spec.build_vfota_message("FW_ID_REQ")
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_request_firmware_id(cls, vers, gateways, time_to_live_s=60.0):
        """ Requests the firmware ID of the firmware on the Access Point.

        Args:
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = cls._get_spec(vers)
        pld = spec.build_vfota_message("FW_ID_REQ")
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_request_report(self, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Requests a transfer report from the

        Args:
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = self._get_spec(self.msg_spec_version)
        pld = spec.build_vfota_message("REPORT_REQ")
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_request_report(cls, vers, gateways, time_to_live_s=60.0):
        """ Requests a transfer report from the

        Args:
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = cls._get_spec(vers)
        pld = spec.build_vfota_message("REPORT_REQ")
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_set_test_mode(self, state, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Emulate a completed vFota transfer, to trigger a report from an Access Point.

        Args:
            test_state (VFotaTestState): Reported state for the Access Point to handle.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        if not isinstance(state, VFotaTestState):
            raise ValueError("'state' must be of type 'VFotaTestState`!")
        spec = self._get_spec(self.msg_spec_version)
        pld = spec.build_vfota_message("TEST_MODE", state=state)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_set_test_mode(cls, state, vers, gateways, time_to_live_s=60.0):
        """ Emulate a completed vFota transfer, to trigger a report from an Access Point.

        Args:
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            state (VFotaTestState): Reported state for the Access Point to handle.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        if not isinstance(state, VFotaTestState):
            raise ValueError("'state' must be of type 'VFotaTestState`!")
        spec = cls._get_spec(vers)
        pld = spec.build_vfota_message("TEST_MODE", state=state)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_send_dat(self, dat_data, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Cancel a viral Firmware-Over-The-Air transfer from Access Point to SymBLE endnode or Access Point.

        Args:
            dat_data (bytearray): The dat file to send to an Access Point.
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        if len(dat_data) > 118:
            raise ValueError("Dat File is too large to transfer over Symphony Link! (118 bytes).")
        spec = self._get_spec(self.msg_spec_version)
        pld = spec.build_vfota_message("CANCEL", dat_length=len(dat_data), dat_file=dat_data)
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_send_dat(cls, dat_data, vers, gateways, time_to_live_s=60.0):
        """ Cancel a viral Firmware-Over-The-Air transfer from Access Point to SymBLE endnode or Access Point.

        Args:
            dat_data (bytearray): The dat file to send to an Access Point.
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        if len(dat_data) > 118:
            raise ValueError("Dat File is too large to transfer over Symphony Link! (118 bytes).")
        spec = cls._get_spec(vers)
        pld = spec.build_vfota_message("CANCEL", dat_length=len(dat_data), dat_file=dat_data)
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

    def vfota_request_status(self, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """ Requests the status of a viral Firmware-Over-The-Air transfer from an Access Point.

        Args:
            gateway_addr (str or :class`.Gateway`): [Optional] Will only route the DownlinkMessage through the given
                gateway address when supplied. Defaults to `None` to send through all possible routes.
            acked (bool): [Optional] Determines whether the AccessPoint will return an acknowledgement upon receiving
                the DownlinkMessage. Defaults to True.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.
            port (int): [Optional] The Symphony Link port to send the DownlinkMessage on. Defaults to 0.
            priority (int): [Optional] The Symphony Link priority of the message. Higher priority messages will be sent
                before lower priority messages when multiple are queued. Default is 10.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if self.msg_spec_version < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = self._get_spec(self.msg_spec_version)
        pld = spec.build_vfota_message("STATUS_REQ")
        return self.send_message(pld, gateway_addr, acked, time_to_live_s, port, priority)

    @classmethod
    def multicast_vfota_request_status(cls, vers, gateways, time_to_live_s=60.0):
        """ Requests the status of a viral Firmware-Over-The-Air transfer from an Access Point.

        Args:
            vers (:class:`.Version`): The AP message spec version of the message to build.
            gateways (list): The list of :class:`.Gateway` objects that should receive the multicast message.
            time_to_live_s (int): [Optional] The number of seconds that the AccessPoint has to check its mailbox before
                the message becomes `expired` and will no longer be valid to send to the AccessPoint. Defaults to 60
                seconds, one minute.

        Returns:
            :class:`conductor.subject.DownlinkMessage`
        """
        if vers < Version(2, 0, 4):
            raise Exception("This Access Point does not support this feature!")
        spec = cls._get_spec(vers)
        pld = spec.build_vfota_message("STATUS_REQ")
        return cls._issue_multicast(pld, time_to_live_s, vers, gateways)

from conductor.airfinder.devices.supertag import Supertag, SupertagDownlinkMessageSpecV2
from conductor.airfinder.messages import ConfigurationProfile
from conductor.util import Version


class SercommDownlinkMessageSpecV2_0(SupertagDownlinkMessageSpecV2):
    """ Sercomm Message Spec V2.0.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x02]})

        # Remove Ack from Message Spec.
        self.msg_types.pop('Ack')

        # Update new message types
        #   - Update Configuration
        #       + Removed Shock Threshold
        #       + Added Sym Retries
        #       + Added Network Token
        #   - Added Battery Consumption Window
        #   - Added Setting Diagnostic Mode
        #   - Added Requesting Consumption
        #   - Added Setting Throttling
        #   - Added FTP Information
        self.msg_types.update({
            'Configuration': {
                'def': ['mask', 'sym_heartbeat', 'lb_only_heartbeat', 'st_mode_heartbeat',
                        'sym_location_update_rate',
                        'lb_only_location_update_rate', 'st_mode_location_update_rate', 'transition_base_update_rate',
                        'transition_increasing_interval_enable', 'scans_per_fix', 'max_wifi_aps', 'max_cell_ids',
                        'location_update_order', 'acc_enable', 'acc_duration', 'acc_threshold', 'cache_enable',
                        'cache_length', 'gps_power_mode', 'gps_timeout', 'network_lost_timeout', 'ref_lost_timeout',
                        'network_scan_interval', 'max_symble_retries', 'network_token'],
                'struct': '>IIIIIIIIBBBBBBHHBBBHHHHBI',
                'defaults': [0x00000000, 0x0000003c, 0x00015180, 0x00015180, 0x0000000b, 0x0000003c, 0x00005460,
                             0x0000000b, 0x00, 0x04, 0x0a, 0x00, 0x1b, 0x01, 0x0003, 0x0050, 0x00, 0x00, 0x00, 0x00b4,
                             0x0258, 0x0258, 0x00b4, 0x05, 0x4f50454e]
            },
            'BattConsumptionWindow': {
                'def': ['mask', 'battery_capacity', 'shipping_mode_power', 'start_up_power', 'alive_time_power',
                        'psm_sleep_power', 'location_update_power', 'network_scan_power', 'ble_connection_power',
                        'lte_success_power', 'lte_failed_power', 'lte_registration_power',
                        'gps_avg_power', 'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power',
                        'ftp_power'],
                'struct': '>IIIIIIHHHIIIIIHHII',
                'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x0000, 0x00000000,
                             0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x00000000, 0x00000000, 0x0, 0x0]
            },
            'SetDiagnosticMode': {
                'def': ['enable'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'ConsumptionRequest': {},
            'SetThrottling': {
                'def': ['mask', 'enable', 'mode', 'win_len', 'min_batt', 'win_limit', 'batt_cap'],
                'struct': '>HBBIIBI',
                'defaults': [0x00, 0x00, 0x01, 0x0000001e, 0x00011940, 0x5a, 0x01010100]
            },
            'FtpAvailable': {
                'def': ['app_vers_major', 'app_vers_minor', 'app_vers_tag', 'modem_vers_major', 'modem_vers_minor',
                        'modem_vers_tag'],
                'struct': '>BBHBBH',
                'defaults': [0x00, 0x00, 0x0000, 0x00, 0x00, 0x0000]
            }
        })


class SercommDownlinkMessageSpecV2_1(SercommDownlinkMessageSpecV2_0):
    """ Sercomm Message Spec V2.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x02]})

        # Update new message types
        #   - Update Configuration
        #       + Removed Shock Threshold
        #       + Added Sym Retries
        #       + Added Network Token
        #   - Added Battery Consumption Window
        #   - Added Setting Diagnostic Mode
        #   - Added Requesting Consumption
        #   - Added Setting Throttling
        #   - Added FTP Information
        self.msg_types.update({
            'Configuration': {
                'def': ['mask', 'sym_heartbeat', 'lb_only_heartbeat', 'st_mode_heartbeat', 'sym_location_update_rate',
                        'lb_only_location_update_rate', 'st_mode_location_update_rate', 'transition_base_update_rate',
                        'transition_increasing_interval_enable', 'scans_per_fix', 'max_wifi_aps', 'max_cell_ids',
                        'location_update_order', 'acc_enable', 'acc_duration', 'acc_threshold', 'cache_enable',
                        'cache_length', 'gps_power_mode', 'gps_timeout', 'network_lost_timeout', 'ref_lost_timeout',
                        'network_scan_interval', 'max_symble_retries', 'network_token'],
                'struct': '>IIIIIIIIBBBBBBHHBBBHHHHBI',
                'defaults': [0x00000000, 0x0000003c, 0x00015180, 0x00015180, 0x0000000b, 0x0000003c, 0x00005460,
                             0x0000000b, 0x00, 0x04, 0x0a, 0x00, 0x1b, 0x01, 0x0003, 0x0050, 0x00, 0x00, 0x00, 0x00b4,
                             0x0258, 0x0258, 0x00b4, 0x05, 0x4f50454e]
            },
            'BattConsumptionWindow': {
                'def': ['mask', 'battery_capacity', 'shipping_mode_power', 'start_up_power', 'alive_time_power',
                        'psm_sleep_power', 'location_update_power', 'network_scan_power', 'ble_connection_power',
                        'lte_success_power', 'lte_failed_power', 'lte_registration_power',
                        'gps_avg_power', 'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power',
                        'ftp_power'],
                'struct': '>IIIIIIHHHIIIIIHHII',
                'defaults': [0xffffffff, 2099999, 40000, 40000, 47000, 85000, 216, 216, 910, 350000, 1550000, 350000,
                             61000000, 56000000, 100, 100, 20000000, 12500000]
            },
            'SetDiagnosticMode': {
                'def': ['enable'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'ConsumptionRequest': {},
            'SetThrottling': {
                'def': ['mask', 'enable', 'mode', 'win_len', 'min_batt', 'win_limit', 'batt_cap'],
                'struct': '>HBBIIBI',
                'defaults': [0x00, 0x00, 0x01, 0x0000001e, 0x00011940, 0x5a, 0x01010100]
            },
            'FtpAvailable': {
                'def': ['app_vers_major', 'app_vers_minor', 'app_vers_tag', 'modem_vers_major', 'modem_vers_minor',
                        'modem_vers_tag'],
                'struct': '>BBHBBH',
                'defaults': [0x00, 0x00, 0x0000, 0x00, 0x00, 0x0000]
            }
        })


class SercommDownlinkMessageSpecV2_2(SercommDownlinkMessageSpecV2_1):
    """ Sercomm Message Spec V2.1.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x02]})

        # Update new message types
        #   - Update Configuration
        #       + Added Transition Base Update
        #       + Added Transition Increasing Int En
        #   - Added CoAP Server Downlink
        #   - Update Battery Consumption
        #       + Shipping Mode Power
        #       + PSM Sleep Power
        # self.msg_types.update({
        #     'BattConsumptionWindow': {
        #         'def': ['mask', 'battery_capacity', 'shipping_mode_power', 'start_up_power', 'alive_time_power',
        #                 'psm_sleep_power', 'location_update_power', 'network_scan_power', 'ble_connection_power',
        #                 'lte_success_power', 'lte_failed_power', 'lte_registration_power',
        #                 'gps_avg_power', 'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power',
        #                 'ftp_power'],
        #         'struct': '>IIIIIIHHHIIIIIHHII',
        #         'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x0000, 0x00000000,
        #                      0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x00000000, 0x00000000]
        #     },
        # })


class SupertagProfile(ConfigurationProfile):
    msg_struct = '>HHHHHHBHHH'

    def __init__(self, **kwargs):
        self.values = [
            kwargs.get('sym_mode_heartbeat'),
            kwargs.get('stationary_sym_mode_location_update_rate'),
            kwargs.get('moving_sym_mode_location_update_rate'),
            kwargs.get('sym_mode_mailbox_check_interval'),
            kwargs.get('stationary_network_scan_interval'),
            kwargs.get('moving_network_scan_interval'),
            kwargs.get('acc_enable'),
            kwargs.get('acc_duration'),
            kwargs.get('acc_threshold'),
            kwargs.get('beacon_flags')
        ]


class SercommDownlinkMessageSpecV3_0(SercommDownlinkMessageSpecV2_2):
    """ Sercomm Message Spec V3.0.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x03]})

        # Re-write Message Specification
        self.msg_types.update({
            'ProfileConfiguration': {
                'type': 0x01,
                'def': ['mask', 'profile0', 'profile1', 'profile4', 'profile5', 'max_symble_retries'],
                'struct': ">B19s19s19s19sB",
                'defaults': [0x0000000, bytearray(b'\xff' * 19), bytearray(b'\xff' * 19), bytearray(b'\xff' * 19),
                             bytearray(b'\xff' * 19), 0x03]
            },
            'SetCoAPServer': {
                'type': 0x02,
                'def': ['server'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'BatteryConsumption': {
                'type': 0x03,
                'def': ['mask', 'battery_capacity', 'shipping_power', 'start_up_power', 'alive_time_power',
                        'idle_time_max_power', 'location_scan_power', 'network_scan_power', 'ble_connection_power',
                        'lte_average_power', 'lte_failed_power', 'lte_registration_power', 'gps_avg_power',
                        'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power', 'ftp_power',
                        'polte_power', 'cell_scan_power', 'modem_reset_power'],
                'struct': '>IIIIIIHHHIIIIIHHIIIII',
                'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x0000, 0x00000000,
                             0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x00000000, 0x00000000]
            },
            'SetDiagnosticMode': {
                'type': 0x04,
                'def': ['enable'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'ConsumptionRequest': {
                'type': 0x05
            },
            'SetThrottling': {
                'type': 0x06,
                'def': ['mask', 'enable', 'mode', 'window_length', 'min_battery', 'window_limit', 'battery_capacity'],
                'struct': '>HBBIIBI',
                'defaults': [0x00, 0x00, 0x01, 0x0000001e, 0x00011940, 0x5a, 0x01010100]
            },
            'FtpAvailable': {
                'type': 0x07,
                'def': ['app_vers_major', 'app_vers_minor', 'app_vers_tag', 'modem_vers_major', 'modem_vers_minor',
                        'modem_vers_tag'],
                'struct': '>BBHBBH',
                'defaults': [0x00, 0x00, 0x0000, 0x00, 0x00, 0x0000]
            },
            'Reset': {
                'type': 0x09,
                'def': ['reset_code'],
                'defaults': [0xd5837ed6]
            },
            'ParamRequestMessage': {
                'type': 0x0A,
            },
            'LowVoltageThresholdConfiguration': {
                'type': 0x0B,
                'def': ['low_voltage_threshold'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'Configuration': {
                'type': 0x0C,  # NOTE: Not msg type 0x01 anymore.
                'def': ['mask', 'lb_only_heartbeat', 'st_mode_heartbeat',
                        'stationary_lb_only_location_update_rate', 'moving_lb_only_location_update_rate',
                        'stationary_st_mode_location_update_rate', 'moving_st_mode_location_update_rate',
                        'transition_base_update_rate', 'movement_scan_type', 'trusted_places_scan_interval',
                        'send_on_stop_wait_time_s', 'gps_location_order', 'wifi_location_order', 'cell_location_order', 'polte_location_order',
                        'cache_length', 'gps_power_mode', 'gps_timeout', 'network_lost_max_count',
                        'lb_lost_max_count', 'network_token'],
                'struct': '>IIIIIIIIBHHBBBBBBHHHI',
                'defaults': [0x00000000, 0x0000003c, 0x00015180]
            },
            'SetTrustedPlaces': {
                'type': 0x0D,
                'def': ['update_type', 'num_lb', 'data', 'num_wifi_bssid', 'data'],
                'struct': '>BB{}sB{}s',
                'defaults': [0x00, 0x00, bytearray(b'\x00'), 0x00, bytearray(b'\x00')]
            },
            'AddCurrentLocationToTrustedPlaces': {
                'type': 0x0E,
                'def': ['max_additions'],
                'struct': '>B',
                'defaults': [0x01]
            },
            'ForceLocationScan': {
                'type': 0x0F,
            }
        })


class SercommDownlinkMessageSpecV3_3(SercommDownlinkMessageSpecV3_0):
    """ Sercomm Message Spec V3.3.0. """

    def __init__(self):
        super(SercommDownlinkMessageSpecV3_3, self).__init__()


class SercommDownlinkMessageSpecV4_0(SercommDownlinkMessageSpecV3_3):
    """ Sercomm Message Spec V4.0.0. """

    def __init__(self):
        super(SercommDownlinkMessageSpecV4_0, self).__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x04]})

        self.msg_types.update({
            # Added average SSF filter scan power.
            'BatteryConsumption': {
                'type': 0x03,
                'def': ['mask', 'battery_capacity', 'shipping_power', 'start_up_power', 'alive_time_power',
                        'idle_time_max_power', 'location_scan_power', 'network_scan_power', 'ble_connection_power',
                        'lte_average_power', 'lte_failed_power', 'lte_registration_power', 'gps_avg_power',
                        'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power', 'ftp_power',
                        'polte_power', 'cell_scan_power', 'modem_reset_power', 'ssf_average_scan_power'],
                'struct': '>IIIIIIHHHIIIIIHHIIIIII',
                'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x0000, 0x00000000,
                             0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x00000000, 0x00000000]
            },
            # New Message Types
            'SetGeofenceList': {
                'type': 0x10,
                'def': ['update_type', 'num_geo_points', 'data'],
                'struct': '>BB{}s',
                'defaults': [0x00, 0x00, bytearray(b'\x00')]
            },
            'SetSSFConfiguration': {
                'type': 0x11,
                'def': ['mask', 'stationary_sym_mode_adv_scan', 'moving_sym_mode_adv_scan',
                        'stationary_lb_mode_adv_scan', 'moving_lb_mode_adv_scan',
                        'stationary_st_mode_adv_scan', 'moving_st_mode_adv_scan'
                                                       'adv_beacon_scan_length', 'min_beacon_uplink_rate_s',
                        'ssf_scan_flags'],
                'struct': '>HIIIIIIHIB',
                'defaults': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
            },
            'RequestSSFScan': {
                'type': 0x12
            },
            'SSFFilterConfiguration': {
                'type': 0x13,
                'def': ['op_code', 'filter_id', 'filter_priority', 'min_minutes_between_events', 'min_adv_rssi_level',
                        'adv_length', 'num_sub_filter', 'sub_filter1_start_addr', 'sub_filter_masks'],
                # TODO: Create/use Filter Object as an array of SubFilters that computes expected bytes.
                'struct': '>',
                'defaults': [0x01]
            },
            'SSFClearFilters': {
                'type': 0x013,
                'def': ['op_code'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'SSFFilterDownlinkRequest': {
                'type': 0x13,
                'def': ['op_code', 'filter_idx', ],
                'struct': '>BB',
                'defaults': [0x04, 0x00]
            },
            'AccelerometerConfiguration': {
                'type': 0x14,
                'def': ['mask', 'sensitivity', 'resolution', 'interrupt_threshold', 'interrupt_duration',
                        'shock_threshold'],
                'struct': '>BBBBBH',
                'defaults': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
            }
        })


class SercommDownlinkMessageSpecV4_1(SercommDownlinkMessageSpecV4_0):
    """ Sercomm Message Spec V4.1.0. """

    def __init__(self):
        super(SercommDownlinkMessageSpecV4_1, self).__init__()


class SercommSupertag(Supertag):
    """ """

    application = "d29b3be8f2cc9a1a7051"

    @property
    def msg_spec_version(self):
        major_str = self._md.get("msgSpecVersion")
        # NOTE: Must use firmware version to know the minor version of the message spec!
        if self.version < Version(1, 1, 6):
            minor = 5
        elif self.version < Version(1, 2, 4):
            minor = 0
        elif self.version < Version(1, 3, 4):
            minor = 1
        elif self.version < Version(2, 0, 0):
            minor = 2
        else:
            minor = 0  # Default case.
        return Version(int(major_str), minor, 0) if major_str else None

    @property
    def symble_version(self):
        raise NotImplementedError()

    @property
    def hw_id(self):
        return self._make_prop(str, "hwId")

    @property
    def transition_base_update_rate(self):
        return self._make_prop(int, "transitionBaseInterval")

    @property
    def moving_lb_only_location_update_rate(self):
        return self._make_prop(int, "lbModeLocUpdateRate_Moving")

    @property
    def stationary_lb_only_location_update_rate(self):
        return self._make_prop(int, "lbModeLocUpdateRate_Stationary")

    @property
    def moving_st_mode_location_update_rate(self):
        return self._make_prop(int, "stModeLocUpdateRate_Moving")

    @property
    def stationary_st_mode_location_update_rate(self):
        return self._make_prop(int, "stModeLocUpdateRate_Stationary")

    @property
    def profiles(self):
        profiles_arr = []
        for i in range(0, 5):
            profiles_arr.append(SupertagProfile(
                sym_mode_heartbeat=int(self._md.get(f"PRO_{i}_symModeHeartbeatInterval")),
                stationary_sym_mode_location_update_rate=int(self._md.get(f"PRO_{i}_symModeLocInterval_Stationary")),
                moving_sym_mode_location_update_rate=int(self._md.get(f"PRO_{i}_symModeLocInterval_Moving")),
                sym_mode_mailbox_check_interval=int(self._md.get(f"PRO_{i}_symModeMailboxInterval")),
                stationary_network_scan_interval=int(self._md.get(f"PRO_{i}_networkScanInterval_Stationary")),
                moving_network_scan_interval=int(self._md.get(f"PRO_{i}_networkScanInterval_Moving")),
                acc_enable=bool(self._md.get(f"PRO_{i}_accelerometerEnable")),
                acc_duration=int(self._md.get(f"PRO_{i}_accelerometerMovementDuration")),
                acc_threshold=int(self._md.get(f"PRO_{i}_accelerometerThreshold")),
                beacon_flags=int(self._md.get(f"PRO_{i}_beaconFlags"))
            ))
        return profiles_arr

    @property
    def profile0(self):
        try:
            return self.profiles[0]
        except IndexError:
            return None

    @property
    def profile1(self):
        try:
            return self.profiles[1]
        except IndexError:
            return None

    @property
    def profile2(self):
        try:
            return self.profiles[2]
        except IndexError:
            return None

    @property
    def profile3(self):
        try:
            return self.profiles[3]
        except IndexError:
            return None

    @property
    def profile4(self):
        try:
            return self.profiles[4]
        except IndexError:
            return None

    @property
    def stationary_location_update_rate(self):
        return self._make_prop(int, "")

    @property
    def movement_scan_type(self):
        scan_type = self._md.get("motionScanType")
        scan_type_int = int(scan_type) if scan_type else None
        if scan_type_int == 0x2:
            return "CellID"
        elif scan_type_int == 0x04:
            return "WiFi"
        return "None"

    @property
    def trusted_places_scan_interval(self):
        return self._make_prop(int, "trustedPlacesScanInterval_s")

    @property
    def beacon_flags(self):
        return self._make_prop(int, '')

    @property
    def send_on_stop_wait_time_s(self):
        return self._make_prop(int, "sendOnStopWaitTime_s")

    @property
    def gps_location_order(self):
        if "gpsOrder" in self._md:
            return self._make_prop(int, "gpsOrder")
        return self._make_prop(int, "gpsLocationOrder")

    @property
    def wifi_location_order(self):
        if "wifiOrder" in self._md:
            return self._make_prop(int, "wifiOrder")
        return self._make_prop(int, "wifiLocationOrder")

    @property
    def cell_location_order(self):
        if "cellOrder" in self._md:
            return self._make_prop(int, "cellOrder")
        return self._make_prop(int, "cellLocationOrder")

    @property
    def polte_location_order(self):
        return self._make_prop(int, "polteOrder")

    @property
    def transition_increasing_interval_enable(self):
        return self._make_prop(bool, "transitionIntervalEnable")

    @property
    def scans_per_fix(self):
        return self._make_prop(int, "scansPerFix")

    @property
    def max_wifi_aps(self):
        return self._make_prop(int, "maxWifis")

    @property
    def max_cell_ids(self):
        return self._make_prop(int, "maxCellIds")

    @property
    def location_update_order(self):
        return self._make_prop(int, "locationUpdateOrder")

    @property
    def acc_enable(self):
        return self._make_prop(bool, "accelerometerEnable")

    @property
    def acc_duration(self):
        return self._make_prop(int, "accelerometerMovementDuration")

    @property
    def acc_threshold(self):
        return self._make_prop(int, "accelerometerThreshold")

    @property
    def cache_enable(self):
        return self._make_prop(int, "cachedMessagesEnable")

    @property
    def cache_length(self):
        return self._make_prop(int, "noSymMessagesCached")

    @property
    def gps_power_mode(self):
        return self._make_prop(str, "gpsPowerMode")

    @property
    def gps_timeout(self):
        return self._make_prop(int, "gpsTimeout")

    @property
    def network_lost_timeout(self):
        return self._make_prop(int, "networkLostTimeout")

    @property
    def network_lost_max_count(self):
        return self._make_prop(int, "networkLostMaxCount")

    @property
    def lb_lost_max_count(self):
        return self._make_prop(int, "lbLostMaxCount")

    @property
    def ref_lost_timeout(self):
        return self._make_prop(int, "refLostTimeout")

    @property
    def network_scan_int(self):
        return self._make_prop(int, "networkScanInterval")

    @property
    def max_symble_retries(self):
        return self._make_prop(int, "symRetries")

    @property
    def network_token(self):
        token = self._md.get("networkToken")
        # return int(token, 16) if token else None
        return hex(int(token, 16))[2:] if token else None

    @property
    def battery_capacity(self):
        val = self._make_prop(int, "batteryCapacity_mAh")
        return val * 1000 if val else None

    @property
    def start_up_power(self):
        val = self._make_prop(int, "pwr-Boot_mAh")
        return val * 1000 if val else None

    @property
    def alive_time_power(self):
        val = self._make_prop(int, "avg_pwr-Alive_mAh")
        return val * 1000 if val else None

    @property
    def location_update_power(self):
        val = self._make_prop(int, "pwr-LocationScan_mAh")
        return val * 1000 if val else None

    @property
    def network_scan_power(self):
        val = self._make_prop(int, "pwr-NetworkScan_mAh")
        return val * 1000 if val else None

    @property
    def ble_connection_power(self):
        val = self._make_prop(int, "pwr-BleConnection_mAh")
        return val * 1000 if val else None

    @property
    def lte_success_power(self):
        val = self._make_prop(int, "pwr-LTEmSuccess_mAh")
        return val * 1000 if val else None

    # @property
    # def lte_registration_power(self):
    #     val = self._make_prop(int, "")

    @property
    def lte_failed_power(self):
        val = self._make_prop(int, "pwr-LTEmFailure_mAh")
        return val * 1000 if val else None

    @property
    def gps_avg_power(self):
        val = self._make_prop(int, "avg_pwr-ScanningGPS_mA")
        return val * 1000 if val else None

    @property
    def wifi_avg_power(self):
        val = self._make_prop(int, "avg_pwr-ScanningWIFI_mA")
        return val * 1000 if val else None

    @property
    def temp_read_power(self):
        val = self._make_prop(int, "pwr-TempReading_mAh")
        return val * 1000 if val else None

    @property
    def battery_read_power(self):
        val = self._make_prop(int, "pwr-BattReading_mAh")
        return val * 1000 if val else None

    @property
    def led_power(self):
        val = self._make_prop(int, "avg_pwr-LedOn_mA")
        return val * 1000 if val else None

    @property
    def ftp_power(self):
        val = self._make_prop(int, "pwr-LTEmFOTA_mAh")
        return val * 1000 if val else None

    @classmethod
    def _get_spec(cls, vers):
        if vers.major == 1:
            return SercommDownlinkMessageSpecV2_0()
        elif vers.major == 2:
            return SercommDownlinkMessageSpecV2_2()
        elif vers.major == 3:
            if vers.minor < 3:
                return SercommDownlinkMessageSpecV3_0()
            elif vers.minor == 3:
                return SercommDownlinkMessageSpecV3_3()
        elif vers.major == 4:
            if vers.minor == 0:
                return SercommDownlinkMessageSpecV4_0()
            elif vers.minor == 1:
                return SercommDownlinkMessageSpecV4_1()
        else:
            raise Exception("No Supported Message Specification.")

    def set_batt_window(self, time_to_live_s=60.0, access_point=None, **kwargs):
        """ TODO """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("BattConsumptionWindow", **kwargs)
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_set_batt_window(cls, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None, **kwargs):
        """ TODO """
        pld = cls._get_spec(vers).build_message("BattConsumptionWindow", **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, access_point, ap_vers, gws)

    def set_diag_mode(self, en, time_to_live_s=60.0, access_point=None):
        """ TODO """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("SetDiagnosticMode", enable=en)
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_set_diag_mode(cls, en, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None):
        """ TODO """
        pld = cls._get_spec(vers).build_message("SetDiagnosticMode", enable=en)
        return cls._send_multicast_message(pld, time_to_live_s, access_point, ap_vers, gws)

    def req_batt_consumption(self, time_to_live_s=60.0, access_point=None):
        """ TODO: docs
        kwargs:
            'batt_cap', 'start_up_power', 'alive_time_power',
            'loc_upd_power', 'net_scan_power', 'ble_conn_power',
            'lte_success_power', 'lte_failed_power', 'gps_avg_power',
            'wifi_avg_power', 'temp_read_power', 'batt_read_power',
            'led_power', 'ftp_power'
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("ConsumptionRequest")
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_req_batt_consumption(cls, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None):
        """ TODO """
        pld = cls._get_spec(vers).build_message("ConsumptionRequest")
        return cls._send_multicast_message(pld, time_to_live_s, access_point, ap_vers, gws)

    def set_throttling(self, time_to_live_s=60.0, access_point=None,
                       ap_vers=None, **kwargs):
        """ TODO: docs
        kwargs:
            'enable', 'mode', 'win_len', 'min_batt',
            'win_limit', 'batt_cap'
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("SetThrottling", **kwargs)
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_set_throttling(cls, vers, gws, time_to_live_s=60.0,
                                 access_point=None, ap_vers=None, **kwargs):
        """ TODO  """
        pld = cls._get_spec(vers).build_message("SetThrottling", **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, access_point, ap_vers, gws)

    def ftp_notify(self, time_to_live_s=60.0, access_point=None, **kwargs):
        """ TODO: docs
        kwargs:
            'app_vers_major', 'app_vers_minor', 'app_vers_tag',
            'modem_vers_major', 'modem_vers_minor',
            'modem_vers_tag'
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("FtpAvailable", **kwargs)
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_ftp_notify(cls, vers, gws, time_to_live_s=60.0,
                             access_point=None, ap_vers=None, **kwargs):
        """ TODO """
        pld = cls._get_spec(vers).build_message("FtpAvailable", **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, access_point, ap_vers, gws)

    def ack(self, time_to_live_s=60.0, access_point=None):
        """ TODO """
        raise NotImplementedError

    @classmethod
    def multicast_ack(cls, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None):
        """ TODO """
        raise NotImplementedError

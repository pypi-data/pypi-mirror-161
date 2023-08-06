""" Methods for the Secure Sensor Filter. """
from conductor.airfinder.devices.node import Node
from conductor.airfinder.messages import DownlinkMessageSpec
from conductor.util import Version


class SSFDownlinkMessageSpecV1(DownlinkMessageSpec):
    """ Message Spec for Secure Sensor Filter v1.0.

    Caution:
        Internal Object
    """

    header = {
        'def': ['msg_type', 'msg_spec_vers'],
        'struct': '>BB',
        'defaults': [0x00, 0x01]
    }

    msg_types = {
        'Configuration': {
            'def': ['max_retries', 'scan_per_fix', 'sensor_data_interval', 'heartbeat'],
            'struct': '>BBII',
            'defaults': [0x05, 0x03, 0x00005000, 0x00000090]
        },
        'Reset': {
            'def': ['reset_code'],
            'struct': '>I',
            'defaults': [0xd5837ed6]
        },
        'Control': {
            'def': ['ctrl_cmd', 'data'],
            'struct': '>B{}s',
        }
    }

    control_types = {
        'ADD_FILTERS': {
            'type': 0x01,
            'def': ['filter_id', 'filter_priority', 'event_rate', 'min_adv_rssi',
                    'adv_length', 'num_sub_filters', 'sub_filter1_len', 'data1', 'sub_filter2_len', 'data2',
                    'sub_filter3_len', 'data3', 'sub_filter4_len', 'data4'],
            'struct': '>BBBBBBB{}sB{}sB{}sB{}s',
            'defaults': [0x00, 0x01, 0x05, 0x30, 0x05, 0x0, 0x01, b'\xff', 0x01, b'\xff', 0x01, b'\xff', 0x01, b'\xff']
        },
        'MODIFY_FILTERS': {
            'type': 0x02,
            'def': ['filter_id', 'filter_priority', 'event_rate', 'min_adv_rssi',
                    'adv_length', 'num_sub_filters', 'sub_filter1_len', 'data1', 'sub_filter2_len', 'data2',
                    'sub_filter3_len', 'data3', 'sub_filter4_len', 'data4'],
            'struct': '>BBBBBBB{}sB{}sB{}sB{}s',
            'defaults': [0x00, 0x01, 0x05, 0x30, 0x05, 0x0, 0x01, b'\xff', 0x01, b'\xff', 0x01, b'\xff', 0x01, b'\xff']
        },
        'DELETE_FILTERS': {
            'type': 0x03
        },
        'FILTER_STATUS': {
            'type': 0x04
        }
    }


class SecureSensorFilter(Node):
    """ """
    application = "597b0f9e3e799165f5d5"

    @property
    def symble_version(self):
        pass

    @property
    def msg_spec_version(self):
        return Version(1, 0, 0)

    @property
    def filter_id(self):
        return self._make_prop(int, 'filter_id')

    @property
    def filter_priority(self):
        return self._make_prop(int, 'filter_priority')

    @property
    def event_rate(self):
        return self._make_prop(int, 'event_rate')

    @property
    def min_adv_rssi(self):
        return self._make_prop(int, 'min_adv_rssi')

    @property
    def adv_length(self):
        return self._make_prop(int, 'adv_length')

    @property
    def num_sub_filters(self):
        return self._make_prop(int, 'num_sub_filters')

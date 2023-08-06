""" Represents an Alert Tag """
import logging

from datetime import datetime

from conductor.airfinder.messages import DownlinkMessageSpec
from conductor.airfinder.devices.tag import Tag

LOG = logging.getLogger(__name__)


class AlertTagDownlinkMessageSpecV1(DownlinkMessageSpec):
    """ Message Spec for the Alert Tag v1.0. """

    header = {
        'def': ['msg_type', 'msg_spec_version'],
        'struct': '>BB',
        'defaults': [0x00, 0x01]
    }

    msg_types = {
            'Configuration': {
                'def': ['mask', 'heartbeat', 'alert_heartbeat',
                        'alert_loc_upd', 'net_lost_scan_count',
                        'net_lost_scan_int', 'max_symble_retries',
                        'button_hold_len', 'audible_alarm_en'],
                'struct': '>BHBBBHBBB',
                'defaults': [0x00, 0x0258, 0x1e, 0x0f, 0x03,
                             0x012c, 0x03, 0x03, 0x01]
            },
            'Ack': {'type': 6},
            'Close': {'type': 7}
    }


class AlertTagDownlinkMessageSpecV2(AlertTagDownlinkMessageSpecV1):
    """ Message Spec for the Alert Tag v2.0. """

    def __init__(self):
        super().__init__()
        # Update Message Spec Version.
        self.header.update({'defaults': [0x00, 0x02]})

        # Update Configuration Message.
        #   - Add U Lite Flags Field.
        #   - Increase Change Mask from uint8 -> uint16.
        self.msg_types["Configuration"].update({
            'def': ['mask', 'heartbeat', 'alert_heartbeat',
                    'alert_loc_upd', 'net_lost_scan_count',
                    'net_lost_scan_int', 'max_symble_retries',
                    'button_hold_len', 'audible_alarm_en', 'ulite_flags'],
            'struct': '>HHBBBHBBBB',
            'defaults': [0x00, 0x0258, 0x1e, 0x0f, 0x03,
                         0x012c, 0x03, 0x03, 0x01, 0b01000000]
        })


class AlertTag(Tag):
    """ Hotel Alert Tag Application. """
    application = 'e66eedc473c53911dbc6'

    @classmethod
    def _get_spec(cls, vers):
        """ Determines the correct message specification of the device. """
        if vers.major == 1:
            return AlertTagDownlinkMessageSpecV1()
        elif vers.major == 2:
            return AlertTagDownlinkMessageSpecV2()
        else:
            raise Exception("Unsupported Message Specification")

    ###########################################################################
    # Core Methods.
    ###########################################################################

    def send_ack(self, time_to_live_s=60, access_point=None):
        """ Sends an Acknowledge message to the Alert Tag.

        Args:
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                receive the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("Ack")
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_ack(cls, vers, gws, time_to_live_s=60, access_point=None,
                      ap_vers=None):
        """ Sends an Acknowledge message to all Alert Tags connected through
        the targetted Access Points.

        Args:
            gws (list): a list of :class:`.gateway` objects that should
                recieve the multicast message. only required when not sending
                through a particular access point.
            vers (:class:`.Version`): The Message Spec version for the
                constructed message.
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                receive the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        pld = cls._get_spec(vers).build_message("Ack")
        return cls._send_multicast_message(pld, time_to_live_s, access_point,
                                           ap_vers, gws)

    def send_close(self, time_to_live_s=60, access_point=None):
        """ Sends a Close message to the Alert Tag.

        Args:
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                receive the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("Close")
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_close(cls, vers, gws, time_to_live_s=60, access_point=None,
                        ap_vers=None):
        """ Sends a Close message to all Alert Tags connected through the
        targetted Access Points.

        Args:
            gws (list): a list of :class:`.gateway` objects that should
                recieve the multicast message. only required when not sending
                through a particular access point.
            vers (:class:`.Version`): The Message Spec version for the
                constructed message.
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                receive the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        pld = cls._get_spec(vers).build_message("Close")
        return cls._send_multicast_message(pld, time_to_live_s, access_point,
                                           ap_vers, gws)

    ###########################################################################
    # Alert Tag Properties.
    ###########################################################################

    @property
    def alertModeFlags(self):
        return self._md.get('alertModeFlags')

    @property
    def alertModeHeartbeatInterval(self):
        return self._md.get('alertModeHeartbeatInterval')

    @property
    def alertModeLength(self):
        return self._md.get('alertModeLength')

    @property
    def alertModeLocationUpdateRate(self):
        return self._md.get('alertModeLocationUpdateRate')

    @property
    def audibleAlarmEnabled(self):
        return bool(self._md.get('audibleAlarmEnabled'))

    @property
    def averageRssi(self):
        return self._md.get('averageRssi')

    @property
    def batteryVoltage(self):
        return self._md.get('batteryVoltage')

    @property
    def buttonHoldLength(self):
        return self._md.get('buttonHoldLength')

    @property
    def diagnosticInfo(self):
        return self._md.get('diagnosticInfo')

    @property
    def firmwareVersion(self):
        return self._md.get('firmwareVersion')

    @property
    def hardwareId(self):
        return self._md.get('hardwareId')

    @property
    def uptime(self):
        val = self._md.get('uptime')
        return datetime.TimeDelta(seconds=int(val)) if val else None

    ###########################################################################
    # Configuration Methods.
    ###########################################################################

    def configure(self, time_to_live_s=60, access_point=None, **kwargs):
        """ Configure the settings of an Alert Tag. Only the values specified
        will be modified.

        Args:
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                recieve the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.
            heartbeat (int): The heartbeat interval of the tag. How often the
                tag will send it's configuration to validate that it is still
                operational.
            alert_heartbeat (int): The maximum amount of time that the Alert
                Tag will wait before requiring to send a new message whilst
                in Alert Mode.
            alert_loc_upd (int): The Alert Location Update Interval. How often
                the Alert Tag will attempt to determine its location whilst in
                Alert Mode.
            net_lost_scan_count (int): Network Lost Scan Count. How many times
                the Alert Tag will scan for a SymBLE Network before it
                determines it has lost the SymBLE Network and goes to sleep.
            net_lost_scan_int (int): Network Lost Scan Interval. How long the
                tag will sleep in-between scans when determining when it has
                lost the SymBLE Network.
            max_symble_retries (int): Maximum SymBLE Retries. How many times
                the Alert Tag will attempt to resend a failed uplink message.
            button_hold_len (int): Button Hold Length. How long the user needs
                to hold the two buttons of the Alert Tag down, before
                activating the alert mode on the tag.
            audible_alarm_en (bool): Enable Audible Alarm. Whether the Alert
                Tag should emit an audible alarm when the Alert Mode has been
                activated, or not.
            ulite_enable (bool): [v2 Only] Ultrasound Lite Enable. Whether to
                attempt an ultrasound based location service when in Alert Mode
            ulite_high_gain (bool): [v2 Only] Ultrasound Lite High Gain.
                Whether to enable the High Gain setting on the Alert Tag when
                performing an ultrasound location update in Alert Mode.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message('Configuration', **kwargs)
        return self._send_message(pld, time_to_live_s, access_point)

    @classmethod
    def multicast_configure(cls, vers, gws, time_to_live_s=60,
                            access_point=None, ap_vers=None, **kwargs):
        """ Configure the settings all Alert Tags connected through the
        targetted Access Points. Only the values specified configuration
        values will be modified.

        Args:
            gws (list): a list of :class:`.gateway` objects that should
                recieve the multicast message. only required when not sending
                through a particular access point.
            vers (:class:`.Version`): The Message Spec version for the
                constructed message.
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                recieve the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.
            heartbeat (int): The heartbeat interval of the tag. How often the
                tag will send it's configuration to validate that it is still
                operational.
            alert_heartbeat (int): The maximum amount of time that the Alert
                Tag will wait before requiring to send a new message whilst
                in Alert Mode.
            alert_loc_upd (int): The Alert Location Update Interval. How often
                the Alert Tag will attempt to determine its location whilst in
                Alert Mode.
            net_lost_scan_count (int): Network Lost Scan Count. How many times
                the Alert Tag will scan for a SymBLE Network before it
                determines it has lost the SymBLE Network and goes to sleep.
            net_lost_scan_int (int): Network Lost Scan Interval. How long the
                tag will sleep in-between scans when determining when it has
                lost the SymBLE Network.
            max_symble_retries (int): Maximum SymBLE Retries. How many times
                the Alert Tag will attempt to resend a failed uplink message.
            button_hold_len (int): Button Hold Length. How long the user needs
                to hold the two buttons of the Alert Tag down, before
                activating the alert mode on the tag.
            audible_alarm_en (bool): Enable Audible Alarm. Whether the Alert
                Tag should emit an audible alarm when the Alert Mode has been
                activated, or not.
            ulite_enable (bool): [v2 Only] Ultrasound Lite Enable. Whether to
                attempt an ultrasound based location service when in Alert Mode
            ulite_high_gain (bool): [v2 Only] Ultrasound Lite High Gain.
                Whether to enable the High Gain setting on the Alert Tag when
                performing an ultrasound location update in Alert Mode.

        Returns:
            :class:`.DownlinkMessage`.
        """
        pld = cls._get_spec(vers).build_message('Configuration', **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, access_point,
                                           ap_vers, gws)

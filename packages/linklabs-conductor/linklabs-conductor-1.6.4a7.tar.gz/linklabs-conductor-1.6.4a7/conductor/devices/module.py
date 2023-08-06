import logging

from collections import namedtuple
from enum import IntEnum

# from conductor.asset_group import AssetGroup
from conductor.event_count import EventCount
from conductor.devices.gateway import Gateway
from conductor.subject import UplinkSubject, DownlinkSubject, UplinkMessage
from conductor.tokens import AppToken
from conductor.util import Version, parse_time

LOG = logging.getLogger(__name__)


# TODO: Format documenation.

class ModuleUplinkMessage(UplinkMessage):

    SignalData = namedtuple('SignalData', ['spreading_factor', 'snr', 'rssi',
                                           'frequency', 'channel'])

    @property
    def signal_data(self):
        vals = self._data.get('value').get('avgSignalMetadata')
        return self.SignalData(int(vals.get('sf')),
                               int(vals.get('snr')),
                               int(vals.get('rssi')),
                               int(vals.get('frequency')),
                               int(vals.get('channelNumber')))

    @property
    def port(self):
        vals = self._data.get('value')
        return int(vals.get('port'))

    @property
    def module(self):
        vals = self._data.get('value')
        return Module(self.session, vals.get('module'), self.instance)

    @property
    def gateway(self):
        vals = self._data.get('value')
        return Gateway(self.session, vals.get('gateway'), self.instance)


class Module(UplinkSubject, DownlinkSubject, EventCount):
    """ Represents a single Module (end node). """
    subject_name = 'node'
    msgObj = ModuleUplinkMessage

    ALLOWED_PORT_RANGE = range(0, 129)

    class DownlinkMode(IntEnum):
        OFF = 0,
        ALWAYS = 1
        MAILBOX = 2

    def send_message(self, payload, gateway_addr=None, acked=True, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a downlink message to a node. If the `gateway_addr` is specified,
        then the message will be sent through that gateway. Otherwise,
        Conductor will route the message automatically.

        `payload` should be a bytearray or bytes object.

        Returns a `DownlinkMessage` object, which can be used to poll for the
        message's status or cancel the message.
        """
        if port not in self.ALLOWED_PORT_RANGE:
            raise ValueError("Port must be within [0, 127]")

        body = {}
        if gateway_addr:
            body['commandRoutes'] = {'linkAddresses': [self.subject_id + '!101!' + str(gateway_addr)]}
        else:
            body['commandTargets'] = {'targetNodeAddresses': [self.subject_id]}

        return self._send_message_with_body(body, payload, acked, time_to_live_s, port, priority)

    def get_routes(self):
        """ Gets the routes for the subject """
        url = '{}/module/{}/routes'.format(self.client_edge_url, self.subject_id)
        return self._get(url)

#    def get_asset_groups(self):
#        """ Returns all the AssetGroups the module is a part of. """
#        url = '{}/assetGroup/node/{}'.format(self.network_asset_url,
#                                             self.subject_id)
#        return [AssetGroup(self.session, x['id'], _data=x)
#                for x in self._get(url)]

    @property
    def downlink_mode(self):
        """ Returns the downlink mode of the module. """
        val = self._md.get('downlinkMode')
        return self.DownlinkMode(int(val)) if val else None

    @property
    def module_firmware_version(self):
        """ Returns the Symphony Link Module Version. """
        val = self._md.get('firmware_version')
        return Version(val[:1], val[2:3], val[4:]) if val else None

    @property
    def last_modified_time(self):
        """ Returns the last time the Access Point was modified. """
        val = self._md.get('lastModified')
        return parse_time(val) if val else None

    @property
    def last_mailbox_request_time(self):
        """ Returns the last time the module requested it's mailbox. """
        val = self._md.get('mailboxRequestTime')
        return parse_time(val) if val else None

    @property
    def initial_detection_time(self):
        """ Returns the last time the Access Point was modified. """
        val = self._data.get('initialDetectionTime')
        return parse_time(val) if val else None

    @property
    def registration_time(self):
        """ Returns the last time the Access Point was modified. """
        val = self._data.get('registrationTime')
        return parse_time(val) if val else None

    @property
    def application_token(self):
        """ Returns the Application Token the module is registered to. """
        val = self._data.get('registrationToken')
        return AppToken(self.session, val, self.instance) if val else None

    @property
    def gateway(self):
        """ Returns the Gateway that registered the AccessPoint. """
        val = self._md.get("registeredByGateway")
        if val is None:
            return None
        try:
            return Gateway(self.session, val, self.instance)
        except Exception as e:
            LOG.exception(e)
            return None

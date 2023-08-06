""" A base for airfinder classes. """
import logging

from collections import namedtuple
from datetime import datetime, timedelta

from conductor.event_count import EventCount
from conductor.devices.gateway import Gateway
from conductor.devices.lte_module import LTEmModuleUplinkMessage
from conductor.devices.module import ModuleUplinkMessage
from conductor.tokens import AppToken, NetToken
from conductor.util import get_device_type, DeviceType
from conductor.subject import UplinkSubject, DownlinkSubject, UplinkMessage

LOG = logging.getLogger(__name__)


class AirfinderUplinkMessage(UplinkMessage):
    """ An intuitive wrapper to the metadata properties
    expected for Airfinder Uplink Messages."""

    SignalData = namedtuple('SignalData', ['rssi'])

    @property
    def _md(self):
        """ Full metadata for the uplink message. """
        return self._data.get('metadata').get('props')

    @property
    def signal_data(self):
        vals = self._data.get('value').get('avgSignalMetadata')
        if vals and 'rssi' in vals:
            return self.SignalData(int(vals.get('rssi')))
        return None

    @property
    def source_message(self):
        uuid = self._md.get('sourceMessageId')
        time = self._md.get('sourceMessageTimestamp')
        url = '{}/data/uplinkPayload/event/{}/{}'.format(self.client_edge_url,
                                                         uuid, time)
        data = self._get(url)
        node_type = get_device_type(self._data.get('value').get('module'))
        if node_type == DeviceType.Module:
            return ModuleUplinkMessage(self.session, data.get('uuid'),
                                       self.instance, data)
        elif node_type == DeviceType.LTEmModule:
            return LTEmModuleUplinkMessage(self.session, data.get('uuid'),
                                           self.instance, data)
        else:
            return TypeError(node_type)

    @property
    def gateway(self):
        vals = self._data.get('value')
        return Gateway(self.session, vals.get('gateway'), self.instance)

    @property
    def application_token(self):
        return AppToken(self.session, self._md.get('app_tok'),
                        self.instance)

    @property
    def network_token(self):
        return NetToken(self.session, self._md.get('net_tok'), self.instance)


class AirfinderUplinkSubject(UplinkSubject):
    """ Airfinder Uplink Subject with built-in multicast capabilities. """

    @classmethod
    def get_all_messages_time_range(self, start, stop=None):
        """ """
        pass

    @classmethod
    def get_all_recent_messages(self, mins_back):
        """ Gets the messages received in the last `mins_back` minutes. """
        now = datetime.utcnow()
        td_mb = timedelta(minutes=mins_back)
        return self.get_all_messages_time_range(now - td_mb)

    @classmethod
    def get_all_last_messages(self, count=1):
        """ Gets the last message the :class:`.ConductorSubject` uplinked, up
        to the count number of messages.

        Args:
            count (int): How many messages to receive.

        Returns:
            List of the last uplink messages for the
            :class:`.ConductorSubject`.
        """
        base_url = '{}/data/{}/ctionnode/{}/mostRecentEvents'.format(self.client_edge_url, self.uplink_type,
                                                                     self.subject_id)
        params = {"maxResults": count}
        messages = [self._get_msg_obj(self.session, m.get('uuid'), self.instance, m)
                    for m in self._get(base_url, params=params)['results']]
        return sorted(messages, key=lambda m: m.receive_time)

    @classmethod
    def _app_addr(self):
        """ Returns:
            Converts the 'application' property of the AirfinderSubject to a
            Conductor-Friendly format to issue commands.
        """
        if not self.application:
            return None
        return '$401${}-{}-{}-{:0>9}'.format(self.application[:8], self.application[8:16], 0, self.application[16:])


class AirfinderSubject(AirfinderUplinkSubject, DownlinkSubject, EventCount):
    """ Base class for Airfinder objects, not intended to be used directly. """
    msgObj = AirfinderUplinkMessage
    application = ""
    af_subject_name = ""

    @property
    def _af_network_asset_url(self):
        """ Returns:
            Instance-based, Client Edge URL for Airfinder.
        """
        return ''.join([self.network_asset_url, '/airfinder'])

    @property
    def _af_client_edge_url(self):
        """ Returns:
            Instance-based, Client Edge URL for Airfinder.
        """
        return ''.join([self.client_edge_url, '/airfinder'])

    @property
    def name(self):
        """ Returns:
            The user issued name of the Subject.
        """
        return self._data.get('value')

    @property
    def subject_type(self):
        """ Returns:
            The type of subject.
        """
        val = self._data.get('type')
        return val

    @property
    def version(self):
        """ Returns the version of the device. """
        raise NotImplementedError()

    def __repr__(self):
        name = "{}: {}".format(self.name, self) if self.name else str(self)
        return '{}({})'.format(self.__class__.__name__, name)

    def _get_registered_af_asset(self, subject_name, subject_id):
        """ Base function for getting a registered asset from the Airfinder
        Network Asset API.

        Args:
            subject_name (str): The corresponding name of the asset class.
            subject_id (str): The asset ID.

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            A list of registered asset from the Airfinder Network Asset API.
        """
        return self._get('{}/{}/{}'.format(self._af_network_asset_url, subject_name, subject_id))

    def _get_registered_af_assets(self, subject_name, account_id=None):
        """ Base function for getting list of registered assets from the
        Airfinder Network Asset API.

        Args:
            subject_name (str): The corresponding name of the asset class.

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            A list of registered assets (json) from the Airfinder Network
            Asset API.
        """
        url = '{}/{}'.format(self._af_network_asset_url, subject_name)
        params = {'accountId': account_id, 'lifecycle': 'registered'}
        return self._get(url, params)

    def update_data(self):
        """ Updates the _data field and resultantly all other properties of the
        object by calling the latest version GET.
        """
        href = self._data["self"]["href"]
        if self.subject_id not in href:
            href += "/{}/{}".format(self.af_subject_name, self.subject_id)
        self._data = self._get(href)

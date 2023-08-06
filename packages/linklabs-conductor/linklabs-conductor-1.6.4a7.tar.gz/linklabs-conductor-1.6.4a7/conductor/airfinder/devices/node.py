""" A base class for SymBLE Nodes. """
import logging
from collections import namedtuple
from uuid import uuid4

from conductor.airfinder.base import AirfinderUplinkMessage, AirfinderSubject
from conductor.airfinder.devices.access_point import AccessPoint
from conductor.airfinder.devices.nordic_access_point import NordicAccessPoint
from conductor.devices.gateway import Gateway
from conductor.devices.lte_module import LTEmModule
from conductor.subject import DownlinkMessage
from conductor.tokens import AppToken, NetToken
from conductor.util import addr_to_mac, find_cls, Version, parse_time

LOG = logging.getLogger(__name__)


class NodeUplinkMessage(AirfinderUplinkMessage):
    """ Uplink Messages for SymBLE EndNodes. """

    SignalData = namedtuple('SignalData', ['ble_rssi'])

    @property
    def msg_type(self):
        return int(self._md.get('msgType'))

    @property
    def msg_counter(self):
        return int(self._md.get('msgCounter'))

    @property
    def access_point(self):
        return AccessPoint(session=self.session, instance=self.instance, subject_id=self._md("symbleAccessPoint"))

    def __repr__(self):
        return "{}({}): Type: {}, {}".format(self.__class__.__name__, self, self.msg_type, self.signal_data)


class NodeDownlinkMessage(DownlinkMessage):
    """ Represents a SymBLE Downlink Message. """

    time_issued = None

    @property
    def target(self):
        """ The recpient SymBLE Endnode. """
        return self._data.get('subjectId')

    @property
    def issuance_time(self):
        """ The timestamp of the issued command. """
        if not self.time_issued:
            self.time_issued = self.issued_commands[0].issuance_time
        return self.time_issued

    @property
    def acknowledged(self):
        """ Whether the downlink messge was acknowledged. """
        return self._data.get('acknowledged')

    @property
    def issued_commands(self):
        """ The Issued Commands from Conductor. """
        return [DownlinkMessage(self.session, x, self.instance,
                                self._get("{}/issuedCommand/{}".format(self.client_edge_url, x)))
                for x in self._data.get('issuedCommandIds')]

    @property
    def route_status(self):
        """ The status of each route. """
        return self._data.get('routeStatus')

    def get_status(self):
        """ Gets the status of the SymBLE Downlink Message. """
        self._data = self._get(''.join([self._af_client_edge_url, '/symbleDownlinkStatus', '/', self.target, '/',
                                       self.subject_id]))
        return self._data


class Node(AirfinderSubject):
    """ Base class for SymBLE Endnodes. """
    subject_name = 'node'
    application = None
    uplink_type = "airfinderLocation"

    @property
    def name(self):
        """ The user issued name of the Subject. """
        return self._data.get('nodeName')

    @property
    def version(self):
        """ The firmware version of the SymBLE Endnode. """
        return None
        # raise NotImplementedError()

    @property
    def symble_version(self):
        """ The version the SymBLE Core on the EndNode is running. """
        raise NotImplementedError()

    @property
    def msg_spec_version(self):
        """ The message spec version of the SymBLE EndNode. """
        return Version(int(self._md.get('messageSpecVersion')))

    @property
    def mac_address(self):
        """ The mac address of the device from its metadata. """
        mac = self._md.get('macAddress')
        return mac if mac else addr_to_mac(self.subject_id)

    @property
    def device_type(self):
        """ Represents the human-readable Application Token that identifies
        which data parser the device is using. """
        return self._md.get('deviceType')

    @property
    def app_token(self):
        """ The Application Token of the Device Type of the Node. """
        val = self._md.get('app_tok')
        return AppToken(self.session, val, self.instance) if val else None

    @property
    def last_access_point(self):
        """ The last access point the node has communicated through. """
        addr = self._md.get('symbleAccessPoint')
        x = self._get_registered_af_asset('accesspoint', addr)
        obj = find_cls(AccessPoint, x['registrationToken'])
        if obj:
            return obj(self.session, addr, self.instance, x)
        dev = x['assetInfo']['metadata']['props'].get('deviceType')
        LOG.error("No device conversion for {}".format(dev))
        return AccessPoint(session=self.session, subject_id=addr, instance=self.instance, _data=x)

    @property
    def gateway(self):
        """ The last gateway that the node's AP communicated through. """
        val = self._md.get('gateway')
        return Gateway(self.session, val, self.instance) if val else None

    @property
    def acknowledged(self):
        """ Whether the last downlink messages was acknowledged. """
        return bool(self._md.get('acknowledged'))

    @property
    def initial_detection_time(self):
        return parse_time(self._data.get('initialDetectionTime'))

    @property
    def registration_detection_time(self):
        return parse_time(self._data.get('registrationTime'))

    @property
    def last_provisioned_time(self):
        return parse_time(self._md.get('lastProvisionedTime'))

    @property
    def initial_provisioned_time(self):
        return parse_time(self._md.get('initialProvisionedTime'))

    @property
    def heartbeat(self):
        val = self._md.get('heartbeatInterval')
        return int(val) if val else None

    @property
    def uptime(self):
        val = self._md.get('uptimeSeconds')
        return int(val) if val else None

    @property
    def avg_rssi(self):
        val = self._md.get('averageRssi')
        return float(val) if val else None

    @property
    def access_point(self):
        val = self._md.get('symbleAccessPoint')
        if not val:
            return None
        x = self._get_registered_af_asset('accesspoint', val)
        obj = find_cls(AccessPoint, x['registrationToken'])
        return obj(session=self.session, subject_id=x['nodeAddress'], instance=self.instance, _data=x)

    @property
    def network(self):
        for key in ['net_tok', 'networkToken']:
            val = self._md.get(key)
            if val:
                x = self._get_registered_af_asset('networkToken', val)
                return NetToken(self.session, val, self.instance, x)
        return None

    @property
    def site_id(self):
        return self._md.get('siteId')

    @classmethod
    def _get_spec(cls, vers):
        """ Should return the correct message specification for the message specification. """
        pass

    @staticmethod
    def _get_msg_obj(*args):
        """ Should return the correct uplink message object for the message specification. """
        return NodeUplinkMessage(*args)

    def _send_message(self, payload, time_to_live_s, access_point=None):
        """ Sends a SymBLE Unicast message. Defaults to sending to all
        Access Points within a Site. This requires the SymBLE endnode
        and all Access Points to be registered to a common site. To send a
        downlink to an individual Access Point, just specify the access_point
        parameter. This does not require a registration of a site.

        Args:
            payload (bytearray):
                The data to be received by the SymBLE Node.
            time_to_live_s (float):
                The time the SymBLE Endnode has to request its Mailbox to
                receive the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        if access_point:
            if isinstance(access_point, LTEmModule):
                self.last_downlink = access_point.send_message(payload, time_to_live_s=time_to_live_s)
            else:
                self.last_downlink = access_point.send_unicast_message(self, payload, time_to_live_s)
        else:
            url = "{}/multicastCommand/{}".format(
                    self._af_client_edge_url, self.subject_id)
            params = {
                'payload': payload.hex(),
                'ttlMsecs': int(time_to_live_s * 1e3)
            }
            data = self._post(url, params=params)
            self.last_downlink = NodeDownlinkMessage(self.session, data.get('symbleMessageId'), self.instance, _data=data)
        return self.last_downlink

    @classmethod
    def _send_multicast_message(cls, payload, time_to_live_s, ap, ap_vers=None, gws=None):
        """ Sends a SymBLE Multicast message.

        To send a Symphony Unicast message (to one Access Point), the
        access_point argument must be set to an instantiated AP.

        To send a Symphony Multicast message (to all Access Points), the
        access_point must be set to an un-instantiated AP class: either
        :class:`.AccessPoint` or :class:`.NordicAccessPoint`; the
        gateway list must be defined to :class:`.Gateway` objects, and
        the ap_vers must be a :class:`.Version` set to the message spec
        version to target the mutlicast message towards.

        Args:
            payload (bytearray): The data to be received by the SymBLE Node.
            time_to_live_s (float): The time the SymBLE Endnode has to request
                its Mailbox to receive the Downlink Message.
            ap (:class:`.AccessPoint`): Can be the Class Object or an
                instantiated Access Point. When instantiated, the message will
                be sent Unicast to that module, otherwise, the ap_vers and gw
                list will be required to multicast.parent
            gws (list): a list of :class:`.gateway` objects that should
                receive the multicast message. only required when not sending
                through a particular access point.
            ap_vers (:class:`.Version`): Required when an Access Point is not
                specified. Will define the message spec of the Access Point
                when constructing the multicast message.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        if not cls.application:
            raise ValueError("Class has no application attribute!")

        # Symphony Unicast.
        if isinstance(ap, AccessPoint) or isinstance(ap, NordicAccessPoint):  # SymBLE Access Point.
            return ap.send_multicast_message(cls.application, payload, time_to_live_s, bytearray.fromhex(uuid4().hex))
        elif isinstance(ap, LTEmModule):  # Supertag Virtual Access Point.
            return ap.send_message(payload, time_to_live_s=time_to_live_s)
        # Symphony Multicast
        else:
            # Validate Arguments.
            if not gws:
                raise ValueError("Must specify gateway to multicast to!")
            if not ap_vers:
                raise ValueError("AP Version is required to multicast!")
            gw = gws[0]
            if not isinstance(gw, Gateway):
                raise ValueError("Gateway must be an instantiated Gateway Object!")
            if not isinstance(ap_vers, Version):
                raise ValueError("AP Version must be a Version object!")

            # Note: Class Method does not have any member variables so we
            # need an instantiated object's session and instance.
            app_tok = AppToken(gw.session, ap.application, gw.instance)

            # Build the Access Point wrapper.
            spec = ap._get_spec(ap_vers)
            pld = spec.build_message('Multicast',
                                     app_tok=bytearray.fromhex(cls.application),
                                     time_to_live_s=time_to_live_s,
                                     uuid=uuid4().fields[0],
                                     data=payload)

            return app_tok.send_message(pld, gws, False, time_to_live_s)

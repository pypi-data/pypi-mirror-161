import logging
import sys

from datetime import datetime, timedelta
from operator import itemgetter
from json.decoder import JSONDecodeError
from requests import HTTPError
from time import sleep

import conductor
from conductor.util import format_time, parse_time, hexlify
from conductor.subscriptions import ZeroMQSubscription, WebsocketSubscription, PollingSubscription

LOG = logging.getLogger(__name__)
CLIENT_EDGE_POLL_PERIOD_S = 1.0


class FailedAPICallException(Exception):
    """ Raised when an API call fails. """
    pass


class DownlinkMessageError(Exception):
    """
    Exception thrown when checking the success of a DownlinkMessage if it is
    neither successful nor pending.
    """
    pass


class ConductorSubject(object):
    """
    Base class for subclasses that are Conductor subjects.

    All subjects need a subject name (unique to the class),
    subject ID (unique to the object), and an authenticated session.
    """
    subject_name = None

    def __init__(self, session, subject_id, instance=conductor.PRODUCTION, _data=None):
        """ Constructs a ConductorSubject.

        Args:
            session(requests.Session): The HTTP session to the conductor
                backend.
            subject_id(str): The Conductor Address of the Conductor Subject.
            instance(str): The Conductor instance to make API calls with.
            _data(json): The json data structure of the Conductor Subject.

        Returns:
            ConductorSubject
        """
        self.session = session
        self.instance = instance
        self.subject_id = subject_id
        self._data = _data
        self._uat = False

    def _validate_http_rsp(self, resp):
        """ Wrapper for the requests HTTPException, to include Conductor's
        Error Messages and potential tracebacks.

        Parameters
        ----------
        resp: requests.Response
            The request made.

        Raises
        ------
        FailedAPICallException
            Will contain the error message of the the returned call!

        Returns the json return of the function.
        """
        exception = False
        try:
            resp.raise_for_status()
        except HTTPError:
            # Prevents the original exception from being logged additionally.
            exception = True
            LOG.error("Call to {} FAILED!".format(resp.url))
            msg = None
            try:
                json = resp.json()
                msg = "HTTP {} | {}: {}".format(resp.status_code,
                                                json.get('description'),
                                                json.get('message'))
            except Exception:
                txt = resp.text
                msg = txt[txt.find("<body><h1>")+len("<body><h1>"):txt.find("</h1>")]
            LOG.error(msg)
            LOG.error("")
            LOG.error("check issues: https://bitbucket.org/link-labs_engineering/conductor-py/issues")
        if exception:
            raise FailedAPICallException(msg)

    def _get(self, url, params=None, json=None):
        """ Calls a GET through the Subject's session given the URL.

        Parameters
        ----------
        url: str
            The URL to execute the GET on.

        params: dict
            [Optional] Parameters to the GET call.

        json: dict
            [Optional] Body to the GET call.

        Raises
        ------
        FailedAPICallException
            Will contain the error message of the the returned call!

        Returns the json return of the function.
        """
        resp = self.session.get(url, params=params, json=json)
        if params:
            LOG.debug("Parameters: {}".format(params))
        if json:
            LOG.debug("Body: {}".format(json))
        self._validate_http_rsp(resp)
        return resp.json()

    def _post(self, url, params=None, json=None):
        """ Calls a POST through the Subject's session given the URL.

        Parameters
        ----------
        url: str
            The URL to execute the POST on.

        params: dict
            [Optional] Parameters to the POST call.

        json: dict
            [Optional] The body of the POST.

        Raises
        ------
        FailedAPICallException
            Will contain the error message of the the returned call!

        Returns the json return of the function.
        """
        resp = self.session.post(url, params=params, json=json)
        if params:
            LOG.debug("Parameters: {}".format(params))
        if json:
            LOG.debug("Body: {}".format(json))
        self._validate_http_rsp(resp)
        try:
            return resp.json()
        except JSONDecodeError:
            return None

    def _delete(self, url, params=None, json=None):
        """ Calls a DELETE through the Subject's session given the URL.

        Parameters
        ----------
        url: str
            The URL to execute the DELETE on.

        json: dict
            [Optional] The body of the DELETE.

        params: dict
            [Optional] Parameters to the DELETE call.

        Raises
        ------
        FailedAPICallException
            Will contain the error message of the the returned call!

        Returns the json return of the function.
        """
        resp = self.session.delete(url, params=params, json=json)
        if params:
            LOG.debug("Paramaters: {}".format(params))
        if json:
            LOG.debug("Body: {}".format(json))
        self._validate_http_rsp(resp)
        try:
            return resp.json()
        except JSONDecodeError:
            return None

    def _patch(self, url, params=None, json=None):
        """ Calls a PATCH through the Subject's session given the URL.

        Parameters
        ----------
        url: str
            The URL to execute the PATCH on.

        json: dict
            [Optional] The body of the PATCH.

        params: dict
            [Optional] Parameters to the GET call.

        Raises
        ------
        FailedAPICallException
            Will contain the error message of the the returned call!

        Returns the json return of the function.
        """
        resp = self.session.patch(url, params=params, json=json)
        if params:
            LOG.debug("Paramaters: {}".format(params))
        if json:
            LOG.debug("Body: {}".format(json))
        self._validate_http_rsp(resp)
        return resp.json()

    def _put(self, url, params=None, json=None):
        """ Calls a PUT through the Subject's session given the URL.

        Parameters
        ----------
        url: str
            The URL to execute the PUT on.

        json: dict
            [Optional] The body of the PUT.

        params: dict
            [Optional] Parameters to the PUT call.

        Raises
        ------
        FailedAPICallException
            Will contain the error message of the the returned call!

        Returns the json return of the function.
        """
        resp = self.session.put(url, params=params, json=json)
        if params:
            LOG.debug("Paramaters: {}".format(params))
        if json:
            LOG.debug("Body: {}".format(json))
        self._validate_http_rsp(resp)
        try:
            return resp.json()
        except JSONDecodeError:
            return None

    def update_data(self):
        """ Updates the _data field and resultantly all other properties of the
        object by calling the latest version GET.
        """
        href = self._data["self"]["href"]
        if self.subject_id not in href:
            href += "/{}/{}".format(self.subject_name, self.subject_id)
        self._data = self._get(href)

    @property
    def network_asset_url(self):
        return 'https://networkasset-{}.com/networkAsset'.format(self.instance)

    @property
    def client_edge_url(self):
        if self._uat:
            if self.instance == conductor.HOSPITALITY:
                return "https://clientedge-hospitality-uat.airfinder.com/clientEdge"
            else:
                return "https://clientedge-conductor-uat.link-labs.com/clientEdge"
        else:
            return 'https://clientedge-{}.com/clientEdge'.format(self.instance)

    @property
    def access_url(self):
        return 'https://access-{}.com/access'.format(self.instance)

    def __str__(self):
        return str(self.subject_id)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.subject_id == other.subject_id
        return NotImplemented

    def __neq__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash((self.subject_name, self.subject_id))

    @property
    def _md(self):
        """ Returns the raw json metadata returned by the object. """
        return self._data.get('assetInfo').get('metadata').get('props')

    def _make_prop(self, datatype, key):
        """ Used to quickly return property values. """
        val = self._md.get(key)
        return datatype(val) if val else None

    @property
    def _href(self):
        return self._data.get('self').get('href')


class UplinkMessage(ConductorSubject):
    """ Base Uplink Message for Containing Uplink Information. """

    @property
    def _md(self):
        return self._data.get('metadata').get('props')

    def __repr__(self):
        return "{}({}), {}".format(
                self.__class__.__name__,
                self, self.signal_data)

    @property
    def module(self):
        return self._data["value"]["module"]

    @property
    def signal_data(self):
        return None

    @property
    def payload_hex(self):
        vals = self._data.get('value')
        return vals.get('pld')

    @property
    def gateway(self):
        vals = self._data.get('value')
        return vals.get("gateway")

    @property
    def receive_time(self):
        return parse_time(self._data.get('time'))

    @property
    def uuid(self):
        return self._data.get('uuid')


class UplinkSubject(ConductorSubject):
    """
    Base class for things that can be queried against for uplink payloads.
    This should not be used directly.
    """
    uplink_type = 'uplinkPayload'
    msgObj = UplinkMessage

    def _build_msg(self, *args):
        """ Should return the correct uplink message object for the msg spec.
        And update any equivalent metadata in the object. """
        if len(args) == 4:
            md = args[3].get("metadata").get("props")
            for k, v in md.items():
                if self._data and k in self._data:
                    self._data[k] = v
        return self.msgObj(*args)

    # TODO: create more generic get message method.

    def get_messages_time_range(self, start, stop=None):
        """ Retrieves all messages within a start and stop time.

        Args:
            start (:class:`.datetime.datetime`): Start Time.
            stop (:class:`datetime.datetime`): [Optional] Stop Time, will
                default to the current time of when the method is called.

        Returns:
            A list of :obj:`UplinkMessage` objects.
        """
        stop = stop or datetime.utcnow()
        base_url = '{}/data/{}/{}/{}/events/{}/{}'.format(self.client_edge_url,
                                                          self.uplink_type,
                                                          self.subject_name,
                                                          self.subject_id,
                                                          format_time(stop),
                                                          format_time(start))
        paged_url_ext = ''

        messages = []
        more_results = True
        while more_results:
            resp_data = self._get(base_url + paged_url_ext)

            messages.extend([self._build_msg(self.session, m.get('uuid'), self.instance, m)
                             for m in resp_data['results']])
            if resp_data['moreRecordsExist']:
                paged_url_ext = '?pageId={}'.format(resp_data['nextPageId'])
            else:
                more_results = False

        messages = sorted(messages, key=lambda m: m.receive_time)
        return messages

    def get_recent_messages(self, mins_back):
        """ Gets the messages received in the last `mins_back` minutes. """
        now = datetime.utcnow()
        return self.get_messages_time_range(now - timedelta(minutes=mins_back))

    def get_last_messages(self, count=1):
        """ Gets the last message the :class:`.ConductorSubject` uplinked, up
        to the count number of messages.

        Args:
            count (int): How many messages to receive.

        Returns:
            List of the last uplink messages for the :class:`.ConductorSubject`
        """
        base_url = '{}/data/{}/{}/{}/mostRecentEvents?maxResults={}'.format(
                self.client_edge_url, self.uplink_type, self.subject_name, self.subject_id, count)
        messages = [self._build_msg(self.session, m.get('uuid'), self.instance, m)
                    for m in self._get(base_url)['results']]
        return sorted(messages, key=lambda m: m.receive_time)

    def get_subscriptions(self):
        """ """
        pass

    def build_polling_sub(self, polling_int_s=5, callback=None):
        """
        """
        return PollingSubscription(self, polling_int_s, callback)

    def build_zmq_sub(self, port, callback=None):
        """
        """
        return ZeroMQSubscription(self, port, callback)

    def build_ws_sub(self, callback=None):
        """
        """
        return WebsocketSubscription(self, callback)


class DownlinkMessage(ConductorSubject):
    """ This class represents a downlink message that has already been posted.
    """

    @property
    def issuance_id(self):
        """ The issuance ID of the DownlinkMessage. """
        return self.subject_id

    @property
    def issuance_time(self):
        """ The timestamp of the issued command. """
        return parse_time(self._data.get('issuanceTime'))

    def get_status(self):
        """ Gets the status of the DownlinkMessage.

        Returns:
            The current status of the DownlinkMessage.
        """
        url = '{}/issuedCommand/{}/status'.format(self.client_edge_url,
                                                  self.issuance_id)
        return self._get(url)['status']

    def get_routes(self):
        """ Gets all routes that a DownlinkMessage took to get to an end-node.

        Returns:
            The routes that Conductor used for this message. """
        url = '{}/issuedCommand/{}'.format(self.client_edge_url,
                                           self.issuance_id)
        return [r['assignedLink'] for r in self._get(url)['routeAssignments']]

    def get_events(self, route=None):
        """ Gets the events on the message and their timestamps.

        Args:
            route (str): The route of interest, can be found with
            :meth:`get_routes`.

        Example:
            Sending a :class:`.DownlinkMessage` to a module with two routes.
            The message was sent and never received in the first route and
            was never received by the :class:`.Gateway` in the second ::

                msg.get_events()
                {
                    '$301$0-0-0-030001665!101!$101$0-0-0-db935317c': [
                        ('Issued', datetime.datetime(2016, 6, 9, 21, 45, 56, 585000)),
                        ('Submitting', datetime.datetime(2016, 6, 9, 21, 45, 57, 158000)),
                        ('Submitted', datetime.datetime(2016, 6, 9, 21, 45, 57, 349000)),
                        ('Sending', datetime.datetime(2016, 6, 9, 21, 45, 57, 403000)),
                        ('Sent', datetime.datetime(2016, 6, 9, 21, 45, 57, 945000)),
                        ('Expired', datetime.datetime(2016, 6, 9, 21, 47, 36, 531000))
                    ],
                    '$301$0-0-0-030001665!101!$101$0-0-0-db9360dc0': [
                        ('Issued', datetime.datetime(2016, 6, 9, 21, 45, 56, 585000)),
                        ('Expired', datetime.datetime(2016, 6, 9, 21, 47, 36, 531000))
                    ]
                }

        Returns:
            A dictionary mapping routes to a list of (state, datetime) pairs.
            If `route` is specified, only the events for the specified route
            will be retrieved (the return type will be the same).
        """
        routes = [route] if route is not None else self.get_routes()
        route_urls = ['{}/issuedCommand/{}/statusDetail/{}'
                      .format(self.client_edge_url, self.issuance_id, rte)
                      for rte in routes]

        results = {}
        for url in route_urls:
            resp_json = self._get(url)
            route = resp_json['routeAssignment']['assignedLink']
            events = [(event['state'], parse_time(event['stateTime']))
                      for event in resp_json['downlinkEvents']]
            events.sort(key=itemgetter(1))
            results[route] = events

        return results

    def cancel(self):
        """ Cancels a pending downlink message. """
        if not self.is_complete():
            LOG.debug("Deleting downlink message %s", self.issuance_id)
            url = '{}/command/{}'.format(self.client_edge_url, self.issuance_id)
            self._delete(url)
            return True
        return False

    def is_complete(self):
        """ Tells if a DownlinkMessage is complete or not.

        Raises:
            DownlinkMessageError: If the message was unsuccessful.

        Returns:
            True if the message was successful and False if it is pending
        """
        status = self.get_status()
        if 'Pending' in status:
            return False
        elif 'Success' in status or 'Acknowledged' in status:
            return True
        else:
            raise DownlinkMessageError(self, status)

    def wait_for_success(self):
        """ Polls the status of the message and returns once it is successful.

        Raises:
            RuntimeError: if the message is unsuccessful.
        """
        while not self.is_complete():
            sleep(CLIENT_EDGE_POLL_PERIOD_S)


class DownlinkSubject(ConductorSubject):
    """ A class for sending downlink messages. """
    last_downlink = None

    def _send_message_with_body(self, body, payload, acked=True, time_to_live_s=60.0, port=0, priority=10):
        url = '{}/issueCommand'.format(self.client_edge_url)

        # We're only looking for one link to respond
        ack_ratio = sys.float_info.epsilon if acked else 0

        body['commandProperties'] = {
            "payloadHex": hexlify(payload),
            "commReqs": {
                "requiredAckRatio": ack_ratio,
                "requiredSuccessfulAckRatio": ack_ratio,
                "priority": int(priority),
                "ttlMSecs": int(time_to_live_s * 1000),
                "portNumber": port,
            }
        }
        data = self._post(url, json=body)
        issuance_id = data['issuanceId']
        self.last_downlink = DownlinkMessage(self.session, issuance_id, self.instance, data)
        return self.last_downlink

    def query_downlink(self, start, stop=None):
        """ Queries Conductor for all downlink sent to this subject. """
        stop = stop or datetime.utcnow()
        url = '{}/commands/{}/{}/{}/{}'.format(self.client_edge_url,
                                               self.subject_name,
                                               self.subject_id,
                                               format_time(stop),
                                               format_time(start))
        return [DownlinkMessage(self.session, result['issuanceId'],
                                self.instance, _data=result)
                for result in self._get(url)]

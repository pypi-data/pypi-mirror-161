import logging
import json

from datetime import datetime
from queue import Queue, Empty
from time import sleep
from threading import Thread, Event

import requests

USE_WEBSOCKETS = True
USE_ZEROMQ = True

try:
    import websockets
except ImportError:
    USE_WEBSOCKETS = False
try:
    import zmq
except ImportError:
    USE_ZEROMQ = False

LOG = logging.getLogger(__name__)


class SubscriptionError(Exception):
    """
    Exception thrown when a subscription reaches a fatal state.
    """
    pass


class SubscriptionBase(Thread):
    """ Uplink Subscription for Conductor Subjects. """

    def __init__(self, uplink_subject, callback=None):
        """ Constructs a Conductor Subscription Thread.

        Args:
            uplink_subject(:class:`.UplinkSubject`): The Conductor Subject to
                subscribe the uplink messages for.
            callback(func): A function that will get called when messages are
                received. Takes the uplink message object as the only argument.

        Note:
            Will pass messages through the supplied callback when supplied.
            Otherwise, will be required to utilize the iterator,  or access
            the ul_queue attribute directly.

        Returns:
            Subscription Thread.
        """
        Thread.__init__(self)
        self.stop_event = Event()
        self.subject = uplink_subject
        self.name = "{}-uplink_subscription".format(self.subject.subject_id)
        self.ul_queue = Queue()
        self.callback = callback

    def _pass_msg(self, msg):
        self.callback(msg) if self.callback else self.ul_queue.put(msg)

    def run(self):
        """ The Subscription Thread.

        Note:
            Not Implemented in base class.
        """
        raise SubscriptionError("Use a derived subscription class ({})!".format(self.__subclasses__()))

    def iter(self):
        """ Provides an iterator function to handle the live subscription in a
        blocking fashion.

        Yeilds:
            UplinkMessage
        """
        while not self.stop_event.is_set():
            try:
                yield self.ul_queue.get_nowait()
            except Empty:
                continue

    def stop(self):
        """ Kill the Subscription Thread. """
        self.stop_event.set()


class ZeroMQSubscription(SubscriptionBase):
    """ ZeroMQ 2 Implementation for uplink events given an UplinkSubject.

    Note:
        Requires port-forwarding to the server running the subscription.
    """

    def __init__(self, uplink_subject, port=11101, callback=None):
        if not USE_ZEROMQ:
            raise Exception("pip install pyzmq")

        super(ZeroMQSubscription, self).__init__(uplink_subject, callback)
        self.event_count = 0
        self.published_event_count = 0
        self.subscription_id = None
        self.port = port

        # Instantiate ZMQ Objects.
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.ip = requests.get("https://api.ipify.org").text

        # Initialize the ZMQ Socket.
        LOG.info("Binding endpoint {}...".format(self.endpoint))
        try:
            self.socket.bind("tcp://*:{}".format(self.port))
        except Exception as e:
            raise SubscriptionError("Could not bind port! {}".format(str(e)))

        # Issue Subscription Request
        self._request_sub()

    def _request_sub(self):
        self.url = "{}/data/{}/{}/{}/subscriptions".format(
            self.subject.client_edge_url, self.subject.uplink_type,
            self.subject.subject_name, self.subject.subject_id)
        data = {
            "channelRequest": {
                "type": "ZeroMQ2",
                "endpoint": self.endpoint,
            },
            "subscriptionProperties": {
                "filterProperties": []
            }
        }

        self.subscription_id = self.subject._post(self.url, json=data)["id"]
        LOG.info("Created New Subscription: {}".format(self.subscription_id))
        self.sub_url = "{}/data/{}/{}/{}/subscription/{}".format(
            self.subject.client_edge_url, self.subject.uplink_type,
            self.subject.subject_name, self.subject.subject_id,
            self.subscription_id)

    def run(self):
        LOG.info("Start subscription...")
        last_evt = None
        while not self.stop_event.is_set():
            if self.socket.closed:
                raise SubscriptionError("Socket Closed!")

            # Retrieve Message
            msg_json = None
            try:
                msg_json = self.socket.recv_json()
            except zmq.error.ZMQError:
                continue
            # LOG.info("Recieved {} message!".format(msg_type))
            # LOG.debug("RXed message: {}".format(msg))

            # Validate recieved data.
            if "event" not in msg_json or not msg_json["event"]:
                LOG.warning("Received invalid event: {}".format(msg_json))
                continue

            # Always respond to server.
            msg_type = msg_json["messageType"]
            evt = msg_json["event"]
            uuid = evt["uuid"]
            self._send_response(uuid)

            # Handle non-message events.
            if msg_type == "remove" or msg_type == "Error":
                LOG.error("Subscription was closed! {}".format(
                    msg_json["headers"]["ClosedReason"]))
                try:
                    self.subject._get(self.sub_url)
                    LOG.info("Subscription is still alive!")
                except Exception:
                    # Build a new subscription.
                    self._request_sub()
                continue  # No message evt to handle.

            # Handle message events.
            self.event_count += 1
            msg = self.subject._build_msg(self.subject.session,
                                          uuid,
                                          self.subject.instance,
                                          evt)

            if last_evt == msg.uuid:
                LOG.warning("Received duplicate event from ZMQ ({})."
                            .format(msg.module))
                # LOG.debug("dupe message: {}".format(msg_json))
                continue  # Do not forward dupe message.
            last_evt = msg.uuid

            # Forward Message to User.
            self._pass_msg(msg)

    def _send_response(self, uuid):
        """ Sends an acknowledgement response.

        Args:
            uuid(int): The UUID of the recieved message.
        """
        attempt = 0
        response = {
            "requestId": uuid,
            "responseStatus": {"OK": None},
            "service": "Subscription",
            "method": "Subscription",
            "responseData": None
        }
        while attempt < 5:
            try:
                attempt += 1
                self.socket.send_json(response)
                self.published_event_count += 1
                return
            except zmq.error.ZMQError:
                LOG.error("Could not send response!")
                continue

    def _close_subscription(self, err=None):
        """ Sends a close notification to Conductor.

        Args:
            err(str): An error message will failing.
        """
        response = {
            "subscriptionId": self.subscription_id,
            "messageType": "UnsubscribeRequest" if not err else "Error",
            "headers": {
                "matchedEventCount": self.event_count,
                "ClosedReason": "Requested by user" if not err else err,
                "publishedEventCount": self.published_event_count,
            },
            "event": None
        }
        return self.socket.send_json(response)

    def stop(self):
        self.stop_event.set()
        self._close_subscription()
        self.subject._delete(self.sub_url)

        LOG.info("Waiting for sever confirmation...")
        start_time = datetime.now()

        # NOTE: This will prevent the next zmq socket initialized on the same
        # port from retrieving the close message and messing with the socket.
        while (datetime.now() - start_time).seconds <= 15:
            msg = None  # Retrieve Message
            try:
                msg = self.socket.recv_json()
            except zmq.error.ZMQError:
                continue
            msg_type = msg["messageType"]
            # LOG.info("Recieved {} message!".format(msg_type))
            LOG.debug("RXed message: {}".format(msg))

            if msg_type == "remove" or msg_type == "Error":
                LOG.info("Subscription was closed successfully! {}".format(
                    msg["headers"]["ClosedReason"]))
                return
        LOG.warning("Never recieved server confirmation of close!")

    @property
    def endpoint(self):
        """ The Endpoint is the protocol/address/port of the zmq server. """
        return "tcp://{}:{}".format(self.ip, self.port)


class WebsocketSubscription(SubscriptionBase):
    """ Websocket Implementation for uplink events given an UplinkSubject.

    Note:
        Conductor Proxies will break websocket implementation.
    """

    def __init__(self, uplink_subject, callback=None):
        """

        """
        if not USE_WEBSOCKETS:
            raise Exception("pip install websockets")
        super(WebsocketSubscription, self).__init__(uplink_subject, callback)

        # Issue Subscription Request
        self.url = "{}/data/{}/{}/{}/subscriptions".format(
            self.subject.client_edge_url, self.subject.uplink_type,
            self.subject.subject_name, self.subject.subject_id)
        data = {
            "channelRequest": {
                "type": "Websocket",
            },
            "subscriptionProperties": {
                "filterProperties": []
            }
        }

        # Manually post to acquire HTTPS Headers.
        resp = self.session.post(self.url, json=data)
        resp.raise_for_status()
        rep = resp.json()

        self.subscription_id = rep["id"]
        self.ws_url = rep["websocketUrl"]["href"]
        LOG.info("Created subscription: {}".format(self.subscription_id))

        # Initialize Websocket Connection
        self.websocket = None
        try:
            hdrs = resp.request.headers.items()
            self.websocket = websockets.connect(self.ws_url,
                                                ping_interval=None,
                                                ping_timeout=50.0,
                                                extra_headers=hdrs)
        except Exception as e:
            raise SubscriptionError("Could not connect to websocket! {}"
                                    .format(str(e)))

    def run(self):
        while not self.stop_event.is_set():
            if self.terminated:
                raise SubscriptionError("Websocket terminated!")

            msg = json.loads(str(self.websocket.recv()))
            obj = self.subject._build_msg(self.subject.session,
                                          msg.uuid,
                                          self.subject.instance,
                                          msg)
            self._pass_msg(obj)

    @property
    def terminated(self):
        if self.websocket:
            return not self.websocket.open
        return True


class PollingSubscription(SubscriptionBase):
    """ Polls for messages at the given polling interval. """

    def __init__(self, uplink_subject, polling_int_s=5, callback=None):
        super(PollingSubscription, self).__init__(uplink_subject, callback)
        self.polling_int_s = polling_int_s

    def run(self):
        last_msg_time = datetime.utcnow()  # Initial value for query time.
        last_msg_ids = []  # Messages forwarded last iteration.
        while not self.stop_event.is_set():
            try:
                msgs = self.subject.get_messages_time_range(last_msg_time)  # Get new messages.
                last_msg_time = datetime.utcnow()  # Save time received.
            except Exception as ex:
                # except FailedAPICallException as ex:
                LOG.error(f"Could not retrieve messages from subscription: {ex}")
            for msg in msgs:  # Forward Messages
                if msg.uuid not in last_msg_ids:  # Message is not duplicate.
                    self._pass_msg(msg)  # Pass message to application
            last_msg_ids = []  # Clear old messages.
            for msg in msgs:  # Add new messages.
                last_msg_ids.append(msg.uuid)
            sleep(self.polling_int_s)  # Wait for next polling interval.

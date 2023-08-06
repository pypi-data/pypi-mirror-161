#
# Messaging module.
#

from typing import Dict, List
import json
import zmq

from .msg_types import MsgType
from .proxy import get_msg_proxy_info
from typhoon.utilities.task import Task
from typhoon.utilities.abstract import Identifiable


KwargsDict = Dict[str, object]
Msg = List[bytes]


class IMsgPublisher:
    """ Message publishing interface. """

    def publish_msg(self, msg_type: MsgType, msg: str, **kwargs: KwargsDict) \
            -> None:
        """
        Publish message of ``msg_type`` type with accompanying keywords
        arguments collected in ``kwargs`` dictionary.

        Args:
            msg_type(MsgType): Message type enumeration constant.
            msg(str): Actual message string.
            kwargs(dict): Collected keyword arguments.

        Returns:
            None
        """
        raise NotImplementedError()


class MinimalMsgPublisher(IMsgPublisher, Identifiable):
    """
    Minimal implementation of IMsgPublisher interface.
    It contains only functional zmq underlying sockets to be able to send
    messages. Actual method for publishing messages are abstract.
    """
    def __init__(self, proxy_info) -> None:
        """
        Initialize an object.

        Args:
           proxy_info(dict): Message proxy information in dict form.
        """
        super().__init__()

        self._pub_ctx: zmq.Context = None
        self._pub_sock: zmq.Socket = None

        self._setup_zmq(pub_port=proxy_info["outbound_port"])
        self._sync_to_proxy(sync_port=proxy_info["sync_port"])

    def _setup_zmq(self, pub_port: int) -> None:
        """
        Setup zmq parts like context and socket.

        Args:
            pub_port(int): Number for outbound proxy port.

        Returns:
            None
        """
        self._pub_ctx = zmq.Context()
        self._pub_sock = self._pub_ctx.socket(zmq.PUB)
        self._pub_sock.setsockopt(zmq.LINGER, 1000)
        self._pub_sock.connect("tcp://localhost:{0}".format(pub_port))

    def _sync_to_proxy(self, sync_port: int) -> None:
        """
        Sync this publisher to messaging proxy.

        Args:
            sync_port(int): Proxy sync port number.

        Returns:
            None
        """
        self._req_sock = self._pub_ctx.socket(zmq.REQ)
        self._req_sock.connect("tcp://localhost:{}".format(sync_port))

        self._req_sock.send(b"Hello")
        # noinspection PyUnusedLocal
        __ = self._req_sock.recv()

    def __del__(self):
        """ Close resources (first close zmq sockets then context). """
        self._req_sock.close()
        self._pub_sock.close()
        self._pub_ctx.destroy()


class CommonMsgPublisher(MinimalMsgPublisher):
    """
    Implementation of message publisher.
    """
    def __init__(self, proxy_info) -> None:
        """
        Initialize an object.

        Args:
           proxy_info(dict): Message proxy information in dict form.
        """
        super().__init__(proxy_info=proxy_info)

    def publish_msg(self, msg_type: MsgType, msg: str, **kwargs: dict) -> None:
        """
        See IMsgPublisher.publish_msg docstring.
        Construct message as composed from several parts and sends it
        through socket as multipart message.

        Message format:
             ------------------------------------------------------
            |MsgType enum as str | msg | kwargs json representation|
             ------------------------------------------------------
        """
        msg = (msg_type.value.encode("utf-8"),
               msg.encode("utf-8"),
               json.dumps(kwargs if kwargs else {}).encode("utf-8"))

        self._pub_sock.send_multipart(msg)


class IMsgSubscriber:
    """
    Models a message subscriber.
    Subscriber subscribes to specific message patterns and handle messages
    it receives through.
    """
    def subscribe(self, msg_pattern: str) -> None:
        """
        Subscribes subscriber to message pattern.
        Pattern is a string which will be converted to bytes.

        Args:
            msg_pattern(str): Message pattern.

        Returns:
             None
        """
        raise NotImplementedError()

    def unsubscribe(self, msg_pattern: object) -> None:
        """
        Unsubscribe subscriber from provided message pattern.

        Pattern can be arbitrary object, but it will be converted to string
        and then encoded to bytes, and that will be used as matching pattern.

        Args:
            msg_pattern(object): Message pattern.
        """
        raise NotImplementedError()

    def handle_msg(self, msg: Msg) -> None:
        """
        Message handler which was routed to this subscriber.

        Args:
            msg(list): List of bytes, as multipart message.

        Returns:
            None
        """
        raise NotImplementedError()


class MinimalMsgSubscriber(IMsgSubscriber, Task):
    """
    Minimal implementation for IMsgSubscriber.
    Only zmq setup is performed, subclass needs to define how messages will
    be handled in ``handle_msg`` and subscribe it to some message patterns using
    ``subscribe_to``.
    """
    def __init__(self, name, proxy_port: int) -> None:
        """
        Initialize an object.

        Args:
            name(str): Name of subscriber.
            proxy_port(int): Port number on proxy to connect it.
        """
        super().__init__(name=name)

        self._proxy_port = proxy_port

        self._sub_ctx: zmq.Context = None
        self._sub_sock: zmq.Socket = None

        # Keep on what this subscriber is subscribed.
        self._subscribed_to: Dict[object, bytes] = {}

        self._setup_zmq(proxy_port)

    def _setup_zmq(self, proxy_port: int) -> None:
        """ Initialize zmq parts. """
        self._sub_ctx = zmq.Context()
        self._sub_sock = self._sub_ctx.socket(zmq.SUB)
        self._sub_sock.connect("tcp://localhost:{}".format(proxy_port))

    def __del__(self):
        """ Close resources (first close zmq sockets then context). """
        print("Destroying {}".format(self))
        self._sub_sock.close()
        self._sub_ctx.destroy()

    def subscribe(self, msg_pattern: str) -> None:
        """ Inherited from IMsgSubscriber. """
        try:
            msg_pattern_bytes = msg_pattern.encode("utf-8")
        except Exception as ex:
            err_msg = "Subscriber '{0}' can't subscribe to '{1}' due to '{2}'".\
                format(self.name, str(msg_pattern), str(ex))
            print(err_msg)
            raise

        self._sub_sock.setsockopt(zmq.SUBSCRIBE, msg_pattern_bytes)
        self._subscribed_to[msg_pattern] = msg_pattern_bytes

    def unsubscribe(self, msg_pattern: object) -> None:
        """ Inherited from IMsgSubscriber. """
        try:
            msg_pattern_bytes = str(msg_pattern).encode("utf-8")
        except Exception as ex:
            err_msg = "Subscriber '{0}' can't unsubscribe '{1}' due to '{2}'". \
                format(self.name, str(msg_pattern), str(ex))
            print(err_msg)
            raise

        self._sub_sock.setsockopt(zmq.UNSUBSCRIBE, msg_pattern_bytes)
        del self._subscribed_to[msg_pattern]

    def execute(self) -> None:
        """
        Starts subscriber task.
        """
        print("Starting subscriber '{0}' <{1}>".format(self.name,
                                                       self.get_id()))

        while True:
            recv = self._sub_sock.recv_multipart()
            self.handle_msg(recv)

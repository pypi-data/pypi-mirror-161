from asyncio_mqtt import Client


class Mqtt:
    """Class for modules IPC with mqtt message broker"""

    _DEFAULT_HOSTNAME = "localhost"
    _DEFAULT_PORT = 1883

    def __init__(
        self,
        hostname=_DEFAULT_HOSTNAME,
        port=_DEFAULT_PORT,
        username=None,
        password=None,
    ):

        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password

        self._client = Client(hostname, port, username=username, password=password)

    async def __aenter__(self):
        self._client = await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)

    def _get_client(self):
        return self._client

    async def publish(self, topic: str, message: str):
        """Publish a messege into a MQTT topic

        :param topic: MQTT topic
        :param message: message to write
        """

        await self._client.publish(topic, payload=message.encode())

    async def subscribe(self, topic: str or list):
        """Read messeges of a topic from an async iterator

        :param topic: MQTT topic, can be a list of topic
        """

        if isinstance(topic, str):
            await self._client.subscribe(f"{topic}/#")
            return self._client.unfiltered_messages()
        else:
            for t in topic:
                await self._client.subscribe(f"{t}/#")
            return self._client.unfiltered_messages()

    async def sensor_publish(
        self,
        sensor: str,
        data: str or int or float = None,
    ):
        """Publish a messege into a sensor topic

        :param data: data to write to the topic
        :param sensor: specific sensor of the module, can be of the format <module>/<sensor>
        """

        if not isinstance(data, str):
            data = str(data)

        await self.publish(f"sensors/{sensor}", data)

    async def sensor_subscribe(self, sensor: str or list = None):
        """Read messeges of a sensor topic

        :param sensor: specific sensor of the module, can be of the format <module>/<sensor>
        """

        if not sensor:
            # subscribe to all sensors

            return await self.subscribe("sensors")
        elif isinstance(sensor, list):
            # substcibe to a subset of sensors

            sensors = [f"sensors/{s}" for s in sensor]
            return await self.subscribe(sensors)
        else:
            # subscrive to only one sensor

            return await self.subscribe(f"sensors/{sensor}")


class Message:
    """Decoder class for client messages"""

    def __init__(self, msg):
        self._raw_message = msg
        self._topic = msg.topic
        self._value = msg.payload.decode()

    @property
    def sensor(self):
        return "/".join(self._topic.split("/")[1:])

    @property
    def module(self):
        fields = self._topic.split("/")

        if len(fields) > 2:
            return fields[1]

        return None

    @property
    def value(self):
        # transform into int
        if self._value.isdigit():
            return int(self._value)

        # transform into float
        try:
            return float(self._value)
        except:
            pass

        # return the string
        return self._value

import logging

import confluent_kafka

from autoreduce_utils.clients.kafka_utils import kafka_config_from_env

log = logging.getLogger(__name__)


class Publisher():
    """Wrapper around asynchronous Kafka Producer"""

    def __init__(self):
        super().__init__()
        config = kafka_config_from_env()
        self.producer = confluent_kafka.Producer(config)

    @staticmethod
    def delivery_report(err, msg):
        """
        Callback called once for each produced message to indicate the final
        delivery result. Triggered by poll() or flush().

        :param confluent_kafka.KafkaError err: Information about any error
        that occurred whilst producing the message.
        :param confluent_kafka.Message msg: Information about the message
        produced.
        :returns: None
        :raises confluent_kafka.KafkaException
        """

        if err is None:
            log.debug('Message delivered to %s [%s]: %s', msg.topic(), msg.partition(), msg.value())
        else:
            log.exception('Message delivery failed: %s', (err))
            raise confluent_kafka.KafkaException(err)

    def publish(self, topic, messages, key=None, timeout=2):
        """
        Publish messages to the topic.

        :param str topic: Topic to produce messages to.
        :param list(str) messages:  List of message payloads.
        :param str key: Message key.
        :param float timeout: Maximum time to block in seconds.
        :returns: Number of messages still in queue.
        :rtype int
        """

        if not isinstance(messages, list):
            messages = [messages]

        try:
            for message in messages:
                record_value = message.json()
                self.producer.produce(topic, record_value, key, callback=Publisher.delivery_report)
                self.producer.poll(0)

            return self.producer.flush(timeout)

        except (BufferError, confluent_kafka.KafkaException, NotImplementedError):
            log.exception('Error publishing to %s topic.', (topic))
            raise

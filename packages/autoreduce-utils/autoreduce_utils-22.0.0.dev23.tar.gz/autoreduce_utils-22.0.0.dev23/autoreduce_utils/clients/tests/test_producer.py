import os
from unittest import TestCase, mock
import confluent_kafka
from autoreduce_utils.clients.producer import Publisher
from autoreduce_utils.message.message import Message

FAKE_KAFKA_TOPIC = 'topic'
FAKE_KAFKA_URL = 'FAKE_KAFKA_URL'


class TestConfluentKafkaProducer(TestCase):

    @mock.patch.dict(os.environ, {"KAFKA_BROKER_URL": FAKE_KAFKA_URL}, clear=True)
    def setUp(self):
        """ Set up the test case. """
        super().setUp()
        self.patcher = mock.patch('confluent_kafka.Producer')
        self.mock_confluent_producer = self.patcher.start()
        self.prod = Publisher()

    def tearDown(self):
        """ Tear down the test case. """
        self.prod.producer.stop()
        self.patcher.stop()

    def test_kafka_producer_init(self):
        """ Test if the producer is initialized correctly. """
        expected_config = {'bootstrap.servers': FAKE_KAFKA_URL}

        self.mock_confluent_producer.assert_called_once_with(expected_config)
        self.assertEqual(self.mock_confluent_producer.return_value, self.prod.producer)

    def test_kafka_producer_publish(self):
        """ Test if the producer publishes correctly. """
        topic = FAKE_KAFKA_TOPIC
        test_message = Message()
        messages = [test_message]
        expected_message = test_message.json()

        self.prod.publish(topic, messages)

        produce_callback = Publisher.delivery_report
        self.prod.producer.produce.assert_called_once_with(topic, expected_message, None, callback=produce_callback)
        self.prod.producer.flush.assert_called_once()

    def test_kafka_producer_publish_one_message_with_key(self):
        """ Test if the producer publishes correctly with a key. """
        topic = FAKE_KAFKA_TOPIC
        one_message = Message()
        key = '1000'
        expected_message = one_message.json()

        self.prod.publish(topic, one_message, key)

        produce_callback = Publisher.delivery_report
        self.prod.producer.produce.assert_called_once_with(topic, expected_message, key, callback=produce_callback)
        self.prod.producer.flush.assert_called_once()

    def test_kafka_producer_publish_exception(self):
        """ Test if the producer raises an exception when publishing. """
        topic = FAKE_KAFKA_TOPIC
        test_message = Message()
        messages = [test_message]
        self.prod.producer.produce.side_effect = \
            confluent_kafka.KafkaException

        self.assertRaises(confluent_kafka.KafkaException, self.prod.publish, topic, messages)

    @mock.patch('autoreduce_utils.clients.producer.log')
    @mock.patch('confluent_kafka.Message')
    def test_delivery_report_exception(self, mock_message, mock_logger):
        """ Test if the delivery report raises an exception. """
        self.assertRaises(confluent_kafka.KafkaException, self.prod.delivery_report, confluent_kafka.KafkaError,
                          mock_message)
        mock_logger.exception.assert_called_once()

    @mock.patch('autoreduce_utils.clients.producer.log')
    @mock.patch('confluent_kafka.Message')
    def test_delivery_report(self, mock_message, mock_logger):
        """ Test if the delivery report publishes correctly. """
        self.prod.delivery_report(None, mock_message)
        mock_logger.debug.assert_called_once()

    @mock.patch('autoreduce_utils.clients.producer.log')
    @mock.patch('confluent_kafka.Message')
    def test_delivery_report_with_unicode(self, mock_message, mock_logger):
        """ Test if the delivery report publishes correctly with unicode. """
        mock_message.topic.return_value = 'test_topic'
        mock_message.partition.return_value = '1'
        mock_message.value.return_value = 'gęś'
        self.prod.delivery_report(None, mock_message)
        mock_logger.debug.assert_called_once_with('Message delivered to %s [%s]: %s', 'test_topic', '1', 'gęś')

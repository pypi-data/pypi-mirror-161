from comram import ramshare
from comram import procon
import unittest
import time


class Test_procon(unittest.TestCase):
    def test_init_read_write(self):
        producer = procon.Produce("test_time_name2", data_type="time_structure", ip="127.0.0.1", port=9980,
                                  send_interval=0.01, debug=False)
        producer.start_produce()
        test_write = ramshare.RamShare("test_time_name2")
        test_write.write_to_tag("tag_3", 9999.9999)

        consumer = procon.Consume("test_time_name_3", "test_consumer", data_type="time_structure", ip="127.0.0.1",
                                  port=9980, debug=False)
        consumer.start_consume()
        test_read = ramshare.RamShare("test_time_name_3")

        time.sleep(0.1)
        tag_3_value = test_read.read_tag("tag_3")

        self.assertEqual(tag_3_value, 9999.9999)

        test_write.close()
        test_read.close()

        producer.stop_produce()
        producer.unlink()
        consumer.stop_consume()
        consumer.unlink()

    def test_consume_reconnect(self):
        consumer = procon.Consume("test_time_name_4", "test_consumer", data_type="time_structure", ip="127.0.0.1",
                                  port=9981)
        consumer.start_consume()
        test_read = ramshare.RamShare("test_time_name_4")

        time.sleep(3)

        producer = procon.Produce("test_time_name5", data_type="time_structure", ip="127.0.0.1", port=9981,
                                  send_interval=0.01)
        producer.start_produce()

        test_write = ramshare.RamShare("test_time_name5")
        test_write.write_to_tag("tag_3", 9999.9999)

        time.sleep(2)
        tag_3_value = test_read.read_tag("tag_3")

        self.assertEqual(tag_3_value, 9999.9999)

        test_write.close()
        test_read.close()

        producer.stop_produce()
        producer.unlink()
        consumer.stop_consume()
        consumer.unlink()

    def test_connection_timeout(self):
        producer = procon.Produce("test_time_name2", data_type="time_structure", ip="127.0.0.1", port=9980,
                                  send_interval=0.01, debug=False)
        producer.start_produce()
        test_write = ramshare.RamShare("test_time_name2")
        test_write.write_to_tag("tag_3", 9999.9999)

        consumer = procon.Consume("test_time_name_3", "test_consumer", data_type="time_structure", ip="127.0.0.1",
                                  port=9980, debug=False)
        consumer.start_consume()
        test_read = ramshare.RamShare("test_time_name_3")

        time.sleep(0.1)
        tag_3_value = test_read.read_tag("tag_3")

        self.assertEqual(tag_3_value, 9999.9999)

        test_write.close()
        producer.stop_produce()
        producer.unlink()

        time.sleep(2)

        connection_status = test_read.read_tag("connection_status")
        connection_status = connection_status.strip(" ")
        self.assertEqual(connection_status, "connection_timeout")

        test_read.close()
        consumer.stop_consume()
        consumer.unlink()


if __name__ == '__main__':
    unittest.main()

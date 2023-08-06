import socket
import threading
import select
import time

from comram import ramshare


def producer_get_connection(self, producer_socket):
    timeout_in_seconds = 0.1
    connection_dict = {}
    while self.signal:
        ready = select.select([producer_socket], [], [], timeout_in_seconds)
        if ready[0]:
            msg, client_address = producer_socket.recvfrom(1024)

            consumer_name = msg[0:20].decode('utf-8').strip(" ")
            consumer_request = msg[20:30].decode('utf-8').strip(" ")

            if consumer_request == "connect":
                consumer_checksum = msg[30:62].decode('utf-8').strip(" ")
                checksum = self.share_memory.data_dict_checksum
                if consumer_checksum == checksum:
                    if self.debug:
                        print("checksum match")

                    if consumer_name in connection_dict:
                        old_client_address = connection_dict[consumer_name]
                        client_found = False
                        i = 0
                        while i < len(self.producer_client_list) and not client_found:
                            if self.producer_client_list[i] == old_client_address:
                                client_found = True
                                del self.producer_client_list[i]
                                print("deleted old address from consumer")
                            i += 1

                    self.producer_client_list.append(client_address)

                    respond_msg = "connection_success"
                    respond_msg = f"{respond_msg:<{20}}".encode('utf-8')
                    update_time = str(self.send_interval)
                    update_time = f"{update_time:<{10}}".encode('utf-8')
                    combine_msg = respond_msg + update_time
                    producer_socket.sendto(combine_msg, client_address)

                    connection_dict[consumer_name] = client_address
                    if self.debug:
                        consumer_name = msg.decode('utf-8')
                        print(f"{consumer_name} connection established")
                else:
                    respond_msg = "checksum_mismatch"
                    respond_msg = f"{respond_msg:<{20}}".encode('utf-8')
                    producer_socket.sendto(respond_msg, client_address)
                    print("checksum mismatch, do something more")

            if consumer_request == "disconnect":
                client_found = False
                i = 0
                while i < len(self.producer_client_list) and not client_found:
                    if self.producer_client_list[i] == client_address:
                        client_found = True
                        del self.producer_client_list[i]
                        print("disconnected consumer")
                    i += 1
                connection_dict.pop(consumer_name)


def producer_message_transmitter(self):
    producer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    producer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
    socket_address = (self.ip, self.port)
    producer_socket.bind(socket_address)

    t_transmitter = threading.Thread(target=producer_get_connection, args=(self, producer_socket,))
    t_transmitter.daemon = True
    t_transmitter.start()

    while self.signal:
        if len(self.producer_client_list):
            msg = self.share_memory.read_all_bytes()

            for i in range(len(self.producer_client_list)):
                producer_socket.sendto(msg, self.producer_client_list[i])
                if self.debug:
                    print("sending message to: ", self.producer_client_list[i])
        time.sleep(self.send_interval)


def consume_message_receiver(self):
    timeout_in_seconds = 0.5
    consumer_name = f"{self.name:<{20}}".encode('utf-8')
    con_dis = "connect"
    connect = f"{con_dis:<{10}}".encode('utf-8')

    checksum = self.share_memory.data_dict_checksum.encode('utf-8')
    message = consumer_name + connect + checksum
    while self.signal:
        consume_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        consume_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
        consume_socket.sendto(message, (self.ip, self.port))
        ready = select.select([consume_socket], [], [], timeout_in_seconds)
        if ready[0]:
            msg, _ = consume_socket.recvfrom(65535)
            connection_status = msg[0:20].decode('utf-8').strip(" ")
            update_time = float(msg[20:30].decode('utf-8').strip(" "))
            timeout_in_seconds = update_time * 100
            self.connection = True
            if connection_status == "connection_success":
                if self.debug:
                    print("successfully connected to producer")
            else:
                raise ValueError(connection_status)
        else:
            consume_socket.close()

        while self.signal and self.connection:
            ready = select.select([consume_socket], [], [], timeout_in_seconds)
            if ready[0]:
                msg, _ = consume_socket.recvfrom(65535)
                self.share_memory.consume_write_all(msg)
                if self.debug:
                    print(msg)
            else:
                self.share_memory.write_to_tag("connection_status", 2)
                if self.reconnect:
                    self.connection = False
                    consume_socket.close()
                else:
                    raise ConnectionError("Connection to producer timeout")

    if self.connection:
        con_dis = "disconnect"
        connect = f"{con_dis:<{10}}".encode('utf-8')
        disconnect_msg = consumer_name + connect
        consume_socket.sendto(disconnect_msg, (self.ip, self.port))
        consume_socket.close()


class Produce(threading.Thread):
    def __init__(self, share_name, ip=None, port=None, send_interval=0.01, data_type=None, debug=False):
        threading.Thread.__init__(self)
        self.signal = True
        self.ip = ip
        self.port = port
        self.data_type = data_type
        self.producer_client_list = []
        self.send_interval = send_interval
        self.share_name = share_name
        self.share_memory = ramshare.RamShare(self.share_name, self.data_type)
        self.debug = debug

    def start_produce(self):
        self.signal = True
        if self.port and self.ip and self.share_name:
            t1 = threading.Thread(target=producer_message_transmitter, args=(self,))
            t1.daemon = True
            t1.start()

        else:
            if not self.port:
                print("port required")
                raise ValueError

            if not self.ip:
                print("ip address required")
                raise ValueError

    def stop_produce(self):
        self.signal = False

    def unlink(self):
        self.share_memory.unlink()


class Consume(threading.Thread):

    def __init__(self, share_name, conname, ip=None, port=None, data_type=None, debug=False, reconnect=True):
        threading.Thread.__init__(self)
        self.signal = True
        self.ip = ip
        self.port = port
        self.data_type = data_type
        self.share_name = share_name
        self.share_memory = ramshare.RamShare(self.share_name, self.data_type)
        self.name = conname
        self.debug = debug
        self.connection = False
        self.reconnect = reconnect

    def start_consume(self):
        self.signal = True
        if self.port and self.ip:
            t1 = threading.Thread(target=consume_message_receiver, args=(self,))
            t1.daemon = True
            t1.start()

        else:
            if not self.port:
                raise ValueError("port required")

            if not self.ip:
                raise ValueError("ip address required")

            if not self.data_type:
                raise ValueError("data type required")

    def stop_consume(self):
        self.signal = False

    def unlink(self):
        self.share_memory.unlink()

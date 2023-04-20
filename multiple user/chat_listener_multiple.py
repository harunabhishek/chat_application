#!/usr/bin/env python3

import socket
import json
import threading
import time
import queue

class Chat_listener:
    def __init__(self, address):
        # Creates the socket with IPV4 and TCP for communicaton
        self.SERVER_ADDRESS_PORT = address
        self.CLIENTS = []
        self.CLIENTS_CONNECTION = {}
        self.MESSAGES_QUEUE = queue.Queue()

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      #to reconnect if connection breaks (we can reuse sockets),1 to enable this
        self.listener.bind(self.SERVER_ADDRESS_PORT)

    def reliable_send(self, connection, data):
        # Sends data error free
        json_data = json.dumps(data)
        connection.send(json_data.encode())

    def reliable_receive(self, connection, bufsize=1024):
        # Receives data error free
        json_data = b""
        while True:
            try:
                json_data = json_data + connection.recv(bufsize)
                return json.loads(json_data)
            except ValueError:
                continue

    def broadcast(self, message):
        # Send the message to all the clients
        for client in self.CLIENTS:
            if client != message[0]:
                self.reliable_send(self.CLIENTS_CONNECTION[client], message)

    def queue_received_messages(self, message):
        # Stores the received messages in a queue
        self.MESSAGES_QUEUE.put(message)
        self.MESSAGES_QUEUE.join()

    def receive_client_messages(self, connection):
        # Continously RECEIVES clients messages
        while True:
            try:
                message_received = self.reliable_receive(connection)
                action = message_received[2]
            except Exception:
                action = "DISCONNECT"

            if action == "DISCONNECT":                        # Stores the Broadcast message of the disconnected client and exit it's thread
                self.queue_received_messages([message_received[0],"ALL","INACTIVE"])
                self.CLIENTS.remove(message_received[0])
                del self.CLIENTS_CONNECTION[message_received[0]]
                connection.close()
                print(message_received[0], "DISCONNECTED")
                exit() 
            elif action == "FILE":
                self.queue_received_messages(message_received)
            elif action == "MESSAGE":                         # stores  the message in queue to redirect it to the RECEIVER
                self.queue_received_messages(message_received)

    def send_client_messages(self):
        # Process and Sends (or REDIRECT) the messages from queue to the receiver 
        print("Queue is ready to send messages")
        while True:
            message = self.MESSAGES_QUEUE.get()
            sender_id = message[1]
            if sender_id == "ALL":
                self.broadcast(message)
            else:
                self.reliable_send(self.CLIENTS_CONNECTION[sender_id], message)

            self.MESSAGES_QUEUE.task_done()

    def handle_client(self, connection):
        # Provides a Unique User Id to a new connection 
        while True:
            client_id = self.reliable_receive(connection)
            if client_id in self.CLIENTS:
                self.reliable_send(connection, "USER NACK")
            else:
                self.reliable_send(connection, "USER ACK")
                break

        self.reliable_send(connection, self.CLIENTS)         # send the Clients list to the new user
        self.CLIENTS.append(client_id)
        self.CLIENTS_CONNECTION[client_id] = connection

        self.queue_received_messages([client_id,"ALL","ACTIVE"])   # sends broadcast message for new user
        self.receive_client_messages(connection)

    def start_thread(self, call_target, arguements=()): 
        threader = threading.Thread(target=call_target, args=arguements)
        threader.daemon = True
        threader.start(  )

    def run(self):
        # Continously listens and accept the new connections
        self.start_thread(self.send_client_messages)
        self.listener.listen(0)
        while True:
            print(" [+] Waiting for connection.....")
            connection, address = self.listener.accept()
            print(" [+] Connection accepted from ", address)

            # start a THREAD for a each new  client
            self.start_thread(self.handle_client, (connection,))

def reliable_connection():
    try:
        ha_chat_listener = Chat_listener((address, port))
        ha_chat_listener.run()
    except Exception as e:
        # print("[+] Error occured...Exiting")
        print(str(e))
        time.sleep(1)
        exit()
       
# address = socket.gethostbyname_ex(socket.gethostname()) [-1][-1]
address = ""                                                                    # ip address of the server
port = 5555                                                                     # port for the chat server to listening
reliable_connection()

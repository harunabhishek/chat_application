#!/usr/bin/env python3

import socket
import json
import threading
# import base64
import sys
import os
import platform
import time


class Chat_listener:
            # listen for connectinons as the object is created
    def __init__(self):
        self.flag_client_exit = 0
        port_ip_list = self.ip_port_manager()
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      #to reconnect if connection breaks (we can reuse sockets),1 to enable this
        # ip = socket.gethostname()
        self.listener.bind((port_ip_list[0], int(port_ip_list[1])))

        self.listener.listen(0)                                       #0 backlocks ,number of connection to be made


        self.accepting_connection()

    def accepting_connection(self):
        print(" [+] Waiting for connection.....")
        self.connection, address = self.listener.accept()             #returns two values /objects , first is socket object to send and receive data (its like connection object in reverse_backdoor prograam) & second is address of the connection
        print(" [+] Connection received from " + str(address))
        self.reliable_send("[+] CONNECTED ")

                                                                 # Serialising data to make it well defined and also to use data structures/objects by converting to json format
    def clear_console(self):
    	system = platform.system() 
    	if system == 'Windows':
    		command = "cls" 
    	# elif system == "Linux":
    	# 	command = "clear"
    	else: 
    		command = "clear"
    	os.system(command)  

    def ip_port_manager(self):
        file_name = "chat_listener.conf"
        if not os.path.exists(file_name):
            ip = input("enter the ip ")
            port = input("enter the port ")
            with open(file_name, "w") as config_file:
                config_file.write(ip + "/" + port)

        with open(file_name, "r") as config_file:
            port_ip = config_file.read()
            port_ip_list = port_ip.split("/")
            return port_ip_list


    def exit_chat(self):
        print("[+] Exiting the chat successfully.")
        self.connection.close()
        sys.exit()

    def handle_client_exit(self):
        print("\033[31mWarning\033[00m : Client already exit the chat.....Unable to send message.")
        decision_made = input("\033[93mDo you want to Exit or Reconnect,\033[00mpress [e/r]")
        if decision_made == "e":
            self.exit_chat()
        elif decision_made == "r":
            # self.__init__("192.168.43.70", 3456)
            self.connection.close()
            self.accepting_connection()
            self.threading_receiving()
            # self.run()    
            return
        else:
            print("Invalid Option.....Exiting")
            self.exit_chat()

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def consistent_receive_print(self):
        while True:
            message_received = self.reliable_receive()
            if "chat exit" in message_received:
                self.flag_client_exit = 1
                print("\033[31m[-] Client exit the chat \033[00m")
                sys.exit()
            else:
                print("\033[34m" + message_received + "\033[00m")

    def consistent_sending(self):
        while True:
            message_sent = input("")

            if message_sent:
                if self.flag_client_exit == 0:
                    self.reliable_send(message_sent)

                    if "chat exit" in message_sent:
                        self.exit_chat()

                else:
                    if "chat exit" in message_sent:
                        self.exit_chat()
                    else:
                        self.handle_client_exit()

    def threading_receiving(self):
        threader = threading.Thread(target = self.consistent_receive_print)
        threader.daemon = True 
        threader.start()
        self.flag_client_exit = 0

    def run(self):
        self.clear_console()
        self.threading_receiving()
        self.consistent_sending()

def reliable_connection():
    try:
        ha_chat_listener = Chat_listener()
        ha_chat_listener.run()
    except Exception:
        print("[+] Error occured...Exiting")
        time.sleep(1)
        sys.exit()
       
# reliable_connection()
ha_chat_listener = Chat_listener()
ha_chat_listener.run()

#!/usr/bin/env python3

# Note:using listener like netcat face problem to execute some commands on the target,,so creating our custom listener


import socket
import json
import threading
import time
import os
import sys
import platform


class Chat_client:
	def __init__(self):
			#connection.send("\n [+] Connection has been established.\n")
		self.flag_client_exit = 0
		port_ip_list = self.ip_port_manager()

		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         #it has two brackets since it takes tuple

		self.trying_connecting(port_ip_list)

	def trying_connecting(self, port_ip_list):
		print("[+] Requesting for the Connection.....")
		while True:
			try:
				self.connection.connect((port_ip_list[0], int(port_ip_list[1])))
				break
			except Exception:
				time.sleep(1)
				continue
		self.reliable_send("[+] CONNECTED ")

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
		file_name = "chat_client.conf"
		if not os.path.exists(file_name):
			ip = input("Enter the ip ")
			port = input("Enter the port ")
			with open(file_name, "w") as config_file:
				config_file.write(ip + "/" + port)

		with open(file_name, "r") as config_file:
			port_ip = config_file.read()
			port_ip_list = port_ip.split("/")
			return port_ip_list
			
	def exit_chat(self):
		print("[+] Exiting the chat successfuly.")
		self.connection.close()
		sys.exit()

	def handle_client_exit(self):
		print("\033[31mWARNING\033[00m : Client already exit the chat.....Unable to send message.")
		decision_made = input("\033[93mDo you want to Exit or Reconnect,\033[00mpress [e/r]")
		while True:
			if decision_made == "e":
				self.exit_chat()
			elif decision_made == "r":
				self.connection.close()
				self.__init__()
				self.threading_receiving()
				return
			else:
				print("Invalid Option.....Try agian..")
				# self.exit_chat()
		
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

	def run(self):
		self.clear_console()
		self.threading_receiving()
		self.consistent_sending()
		
def reliable_connection():
	try:
		ha_chat_client = Chat_client()
		ha_chat_client.run()
	except Exception:
		print("[-] Error occured...Exiting")
		time.sleep(1)
		sys.exit()
	
# reliable_connection()		

ha_chat_client = Chat_client()
ha_chat_client.run()
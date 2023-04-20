#!/usr/bin/env python3

import socket
import json
import threading
import time
import base64


class Chat_client:
	def __init__(self, address):
		# Creates the socket with IPV4 and TCP for communication
		self.SENDER_USER_ID = input("Enter Username ")
		self.RECEIVER_USER_ID = "NONE"
		self.RECEIVER_STATUS = "ACTIVE"
		self.SERVER_ADDRESS_PORT = address
		self.USERS = []

		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	def exit_chat(self):
		print("[+] Exiting the chat successfully.")
		self.connection.close()
		exit()

	def reliable_send(self, data):
		# Sends data error free
		json_data = json.dumps(data)
		self.connection.send(json_data.encode())

	def reliable_receive(self,bufsize=1024):
		# Receives data error free 
		json_data = b""
		while True:
			try:
				json_data = json_data + self.connection.recv(bufsize)
				return json.loads(json_data)
			except ValueError:
				continue

	def write_file(self, path, content):
		with open(path, "wb") as file:
			file.write(base64.b64decode(content))
			return "[+] Received a file " + path

	def read_file(self, path):
		with open(path, "rb") as file:
			return base64.b64encode(file.read()).decode()

	def receive_messages(self):
		# Continuously RECEIVE messages from other USERS
		while True:
			received_message = self.reliable_receive()
			action = received_message[2]
			temp_message = ""
			
			# decides what action to take on message
			if action == "ACTIVE":								# add new active user to list
				self.USERS.append(received_message[0])
				temp_message = received_message[0] + ": is ONLINE"
			elif action == "INACTIVE":							# removes inactive user from list
				self.USERS.remove(received_message[0])
				temp_message = received_message[0] + ": is OFFLINE"
				if received_message[0] == self.RECEIVER_USER_ID:
					self.RECEIVER_STATUS = "INACTIVE"			# marks the selected user as inactive, if disconnected
			elif action == "FILE":
				print("received a file")
				temp_message = self.write_file(received_message[3], received_message[4])
			elif action == "MESSAGE":
				if received_message[1] == "ALL":
					temp_message = received_message[0] + "(" + "ALL" + ") : " + received_message[3]
				else:	
					temp_message = received_message[0]+ " : " + received_message[3]

			print(temp_message)

	# checks wheter the user is connected before sending the messages to the user
	def send_on_active(self, message):
		if self.RECEIVER_USER_ID != "NONE":
			if self.RECEIVER_STATUS == "ACTIVE":
				if self.RECEIVER_USER_ID == "ALL":
					if not self.USERS:
						print("[-] NO USER is ONLINE")
						return

				self.reliable_send(message)
			else:
				print("[-] User DISCONNECTED, select ANOTHER")
		else:
			print("[-] Please SELECT at least ONE user")

	def send_messages(self):
		# Continuously takes INPUT to SEND messages
		while True:
			message = input("")
			if message:
				# Separates commands from messages and performs actions on them accordingly
				if "#" in message:
					action = message.replace("#", "")
					if action == "users":						# list users
						print(self.USERS)
					elif action == "close":						# closes the chat
						message = [self.SENDER_USER_ID, "SERVER","DISCONNECT"]
						self.reliable_send(message)
						self.exit_chat()
					elif action == "all":						# send to all users
						self.RECEIVER_USER_ID = "ALL"
						self.RECEIVER_STATUS = "ACTIVE"
					elif "send" in action:
						file_name = action.split(" ") [1]			# seprates filename
						try:
							file_content = self.read_file(file_name)
						except Exception as e:
							print(str(e))
							continue
						message = [self.SENDER_USER_ID, self.RECEIVER_USER_ID, "FILE", file_name, file_content]
						self.send_on_active(message)
						print("[+] File sent successfully.")
					else:
						if self.USERS:							# select a user to send pesonally
							if action in self.USERS:
								self.RECEIVER_USER_ID = action
								self.RECEIVER_STATUS = "ACTIVE"
							else:
								print("[-] User NOT FOUND, select ANOTHER")
						else:
							print("[-] NO USER is ONLINE")
				# sends messages to the server according to user preferences
				else:
					message = [self.SENDER_USER_ID, self.RECEIVER_USER_ID, "MESSAGE", message]
					self.send_on_active(message)

	def start_thread(self, call_target, arguements=()): 
		threader = threading.Thread(target=call_target, args=arguements)
		threader.daemon = True
		threader.start()

	def run(self):
		# try to connect to server
		print("[+] Connecting .....")
		while True:
			try:
				self.connection.connect(self.SERVER_ADDRESS_PORT)
				break
			except Exception as e:
				print(str(e))
				time.sleep(1)
				continue

		# create and verify USER ID with server from already connected CLIENTS
		while True:
			self.reliable_send(self.SENDER_USER_ID)
			user_flag = self.reliable_receive()
			if user_flag == "USER NACK":
				print("[-] Username already taken, Choose another")
				self.SENDER_USER_ID = input("Enter new username >> ")
			elif user_flag == "USER ACK":
				print("[+] YOU are now connected as", self.SENDER_USER_ID)
				break

		# List CONNECTED USERS
		self.USERS = self.reliable_receive()
		print("CONNECTED USERS:")
		print(self.USERS)

		# Start a THREAD to continuously receive messages
		self.start_thread(self.receive_messages)
		self.send_messages()
		
def reliable_connection():
	try:
		ha_chat_client = Chat_client((address, port))
		ha_chat_client.run()
	except Exception as e:
		# print("[-] Error occured...Exiting")
		print(str(e))
		time.sleep(1)
		exit()

# address = socket.gethostbyname_ex(socket.gethostname()) [-1][-1]
address = ""																# ip address of the server
port = 5555																	# port for the chat server to listening
reliable_connection()		

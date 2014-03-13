
import socket
import sys
import re
import client



class Server: 

	SENSOR_PORT = 1079
	CLIENT_PORT = 1080
	HOST = '' #localhost? 127.0.0.1
	CLIENT_SOCKET = None
	SENSOR_SOCKET = None
	
	clients = []## list of clients		## need to add clients
	
	def start_listening_sensor(self):
		try:
			self.SENSOR_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.SENSOR_SOCKET.bind((self.HOST,self.SENSOR_PORT))
		except socket.error, (errno,message):
			if self.SENSOR_SOCKET:
				self.SENSOR_SOCKET.close()
			print "Failed to open socket " + errno + " " + message
			sys.exit() #or do we want to exist, or just ignore it?
		while 1:
			data,addr = self.SENSOR_SOCKET.recvfrom(2000)
			#
			sensorID = re.search("'dev_id':'(.*)','sensor_data'",data).group(1)
			
			for c in self.clients:
				c.received_packet_from_sensor(sensorID, data)
	
				
	def start_listening_client(self):
		try:
			self.CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.CLIENT_SOCKET.bind((self.HOST,self.SENSOR_PORT))
		except socket.error, (errno,message):
			if self.CLIENT_SOCKET:
				self.CLIENT.SOCKET.close()
			print "Failed to open socket " + errno + " " + message
			sys.exit() #or do we want to exist, or just ignore it?
		while 1:
			data,addr = self.CLIENT.SOCKET.recvfrom(2000)
			
			for c in self.clients:
				if c.client_addr == addr:
					c.received_packet_from_client(data)
					break
				elif self.clients[-1] == c:
					self.clients.append(client(addr))
					self.clients[-1].received_packet_from_client(data)
			
			
			
			
			
			
					
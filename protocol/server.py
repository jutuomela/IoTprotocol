
import socket
import sys
import re




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
			
			for client in self.clients:
				client.received_packet_from_sensor(client, sensorID, data)
	
				
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
			#
			
					
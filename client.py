import socket
import packet
import packet_settings, packet_unpacker

	server_port = 6006
	server_addr = None
	server_socket = None






	def __init__(self,address,port):
		try: 
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.server_port = port
			self.server_addr = address
		except socket.error, (errno,message):
			if self.server_socket:
				self.server_socket.close()
			print "Failed to open socket " + message
			sys.exit() #or do we want to exit, or just ignore it?

	

	def send_packet(self, packet):
		self.server_socket.sendto(message, (self.server_addr,self.server_port))


	def receive_data(self):
		data, server = self.server_socket.recvfrom(2048)
		self.received_data_from_server(data)





	#possible chunk types: HB,DATA, ACK, NACK, (v2 AGR)
	def received_data_from_server(self, packet):
		

import socket
import packet
import packet_settings, packet_unpacker
import struct 

	server_port = 6006
	server_addr = None
	server_socket = None
	packet_seq_num = 0


#TODO mechanism for NACK
class Client_ui(): 

	def __init__(self,address,port):
		self.packet_seq_num = os.urandom(4) % packet_settings.MAX_SEQ_NUM
		self.packet_seq_num = struct.unpack(">L", packet_seq_num)
		self.server_port = port
		self.server_addr = address

		try: 
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			
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
		print("Client received data from server: " + str(data)) #used for testing




	#possible chunk types: HB,DATA, ACK, , (v2 AGR, NACK)
	def received_data_from_server(self, packet):
		unpacker = packet_unpacker.Packet_unpacker() 
		packet = unpacker_unpack(packet)
		position = 3
		while(position < len(packet)):
			if(packet[position] == packet_setting.TYPE_ACK):
				##subscription was succesfull, datafield contains list of sensors should we retry sensors which are not listed? 
	
			if(packet[position] == packet_setting.TYPE_HB):
				#respond with ACK, now 
				self.sendACK("")

			if(packet[position] == packet_setting.TYPE_DC):
				result = re.search("'dev_id': '(.*)', 'sensor_data'",packet[position+3])
				
				if result != None:
					sensorID = result.group(1)

					#write received data to log
					file = open("client_"+ sensorID +".log", "a")
					file.write(str(time.time()))
					file.write("\t")
					file.write(packet[position+3])
					file.write("\n")
					file.close()





	def sendACK(self,data):
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addACK(data)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM

	def sendNACK(self):	
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addNACK("")
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM
	
	def sendSUB(self,data,option): #data: sensors, option: initial/or not
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addSub(data,option)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM	
	
	def sendUNSUB(self):
		current_packet = packet.Packet(self.packet_seq_num) 
		current_packet.addUnSub(data,option)
		self.send_packet(current_packet)
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM	
			
	








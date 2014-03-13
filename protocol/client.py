

import socket, os
import sets
import struct
import packet_settings, packet_unpacker
import packet


class Client():

	packet_seq_num = 0
	sensor_list = sets.Set([])
	current_packet = 0
	client_addr = 0
	client_socket = 0
	server = 0
	
	def __init__(self, server, client_addr):
		self.server = server
		self.client_addr = client_addr
		self.client_socket = socket(socket.AF_INET6, socket.SOCK_DGRAM)
		
		packet_seq_num = os.urandom(4) % packet_settings.MAX_SEQ_NUM
		self.packet_seq_num = struct.unpack(">L", packet_seq_num)
		
	##sends the packet that has been forming to the client
	def send_packet(self):
		num_sent=self.client_socket.sendto(self.current_packet.get_packet(), self.client_addr)
		if num_sent != len(self.current_packet.get_packet()):
			print("Error: only part of packet sent")
		self.packet_seq_num = (self.packet_seq_num +1)%packet_settings.MAX_SEQ_NUM
		self.current_packet = packet.Packet() #TODO: header info needs to be added to packet
		
		
	## called when we received a packet from a client
	def received_packet_from_client(self, packet):
		unpacker = packet_unpacker.Packet_unpacker() #unpack the packet
		packet = unpacker.unpack(packet)
		position = 3
		self.heartbeats_sent = 0
		while position < len(packet):
			if(packet[position] == packet_settings.TYPE_ACK):
				# Dont think we need to implement anything here since ack only sent in response to heartbeat
				#and we already reset self.heartbeats_sent to zero
				print("received ack from client") 
				
			if(packet[position] == packet_settings.TYPE_NACK):
				# put congestion control here
				print("Received nack from client")
				
				
			if(packet[position] == packet_settings.TYPE_SUB):
				# add new sensors to clients sensor list
				print("Received sub from client")
				
			if(packet[position] == packet_settings.TYPE_UNSUB):
				# remove sensors from clients sensor list
				# remember to check options bit for remove all sensors bit
				# if no more sensors then delete client from server list
				print("Received unsub from client")
					
			if(packet[position] == packet_settings.TYPE_REQ):
				# return the list of all sensors
				print("Received req from client")
			
			#increment our position in the list by four to get to the next chunk 
			position+=4

	## called when the server class the owns this client class has a packet from a sensor
	def received_packet_from_sensor(self, sensor, data):
		if sensor in self.sensor_list:	# check if the sensor is in the sensor list
			self.add_data(data) #add the data to the current packet. 
			return
	
		
	## sends a heartbeat to the client
	def send_heartbeat(self):
		status=self.current_packet.addHeartBeat("")
		
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.send_packet()
			self.send_heartbeat()
			
		elif(status==packet_settings.DATA_TOO_LONG):
			print("ERROR: adding heartbeat to packet resulted in DATA_TOO_LONG status code")
			
		elif(status==packet_settings.OKAY):
			self.send_packet() #heartbeats are sent immediatly
			self.heartbeats_sent+=1		
		else:
			print("ERROR: unknown status code returned by add_heartbeat()")
			
	

	def add_data(self, data):
		status = self.current_packet.addData(data)
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.send_packet()
			self.add_data(data)
			
		elif(status==packet_settings.DATA_TOO_LONG):
			print("ERROR: adding data to packet resulted in DATA_TOO_LONG status code")
			
		elif(status==packet_settings.OKAY):
			#if status okay do nothing
			continue
		
		else:
			print("ERROR: unknown status code returned by add_data(self, data)")








	

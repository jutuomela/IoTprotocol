

import socket, sys, os
import sets
import random
import struct


class Client():

	packet_seq_num
	sensors = Set([])
	current_packet
	client_addr
	client_socket
	
	def __init__(self, client_addr):
		self.client_addr = client_addr
		self.client_socket = socket(AF_INET6, SOCK_DGRAM)
		
		packet_seq_num = os.urandom(4)
		self.packet_seq_num = struct.unpack("<L", packet_seq_num)
		

	def send_packet():
		num_sent=self.client_socket.sendto(self.current_packet.get_packet(), clientaddr)
		if num_sent != len(self.current_packet.get_packet()):
			print("Error: only part of packet sent")
		self.current_packet = Packet() #TODO: header info needs to be added to packet
		
		
	def send_heartbeat():
		status=self.current_packet.addHeartBeat("")
		
		if(status==packet_settings.NOT_ENOUGH_SPACE):
			self.send_packet()
			self.send_heartbeat()
			
		elif(status==packet_settings.DATA_TOO_LONG):
			print("ERROR: adding heartbeat to packet resulted in DATA_TOO_LONG status code")
			
		elif(status==packet_settings.OKAY):
			self.send_packet()
		
		else:
			print("ERROR: unknown status code returned by add_heartbeat()")
			
	










	

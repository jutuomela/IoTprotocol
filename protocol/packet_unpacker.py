import packet_settings
import math
import struct

class packet_unpacker():
	
	packet = 0
	unpacked_packet = []
	position = 0; 
		
	def unpack(self, packet):
		self.packet = packet
		unpacked_packet = []
		
	#unpacks the header
	def unpack_header(self):
		header = self.packet[:4]
		header = int(struct.unpack("<L", header)[0])
		self.position = 4
		version = header >> packet_settings.VERSION_SHIFT
		options = self.get_bits(header, packet_settings.OPTIONS_SHIFT, packet_settings.OPTIONS_LENGTH)
		
	def get_bits(self, value, position, length):
		answer = value & (int((math.pow(2, length)-1)) << position)
		answer = answer >> position
		return answer
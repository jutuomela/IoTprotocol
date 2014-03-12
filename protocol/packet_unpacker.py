import packet_settings
import math
import struct

class Packet_unpacker():
	
	packet = 0
	unpacked_packet = []
	position = 0; 
		
	def unpack(self, packet):
		self.packet = packet
		self.unpacked_packet = []
		self.unpack_header()
		
	#unpacks the header
	def unpack_header(self):
		header = self.packet[:4]
		header = struct.unpack("<L", header)[0]
		self.position = 4
		version = self.get_bits(header, packet_settings.VERSION_SHIFT, packet_settings.VERSION_LENGTH)
		options = self.get_bits(header, packet_settings.OPTIONS_SHIFT, packet_settings.OPTIONS_LENGTH)
		seq_num = self.get_bits(header, packet_settings.SEQ_NUM_SHIFT, packet_settings.SEQ_NUM_LENGTH)
		self.unpacked_packet.append(version)
		self.unpacked_packet.append(options)
		self.unpacked_packet.append(seq_num)
		
	def unpack_chunks(self):
		
		#loop through the chunks
		while len(self.packet)<self.position:
			
			#unpack chunk header 
			header = self.packet[self.position:self.position+4]
			header = struct.unpack("<L", header)
			self.position += 4
			type = self.get_bits(header, packet_settings.CHUNK_TYPE_SHIFT, packet_settings.CHUNK_TYPE_LENGTH)
			options = self.get_bits(header, packet_settings.CHUNK_OPTIONS_SHIFT, packet_settings.CHUNK_OPTIONS_LENGTH)
			chunk_length = self.get_bits(header, packet_settings.CHUNK_LEN_SHIFT, packet_settings.CHUNK_LENGTH_FIELD_LENGTH)
			self.unpacked_packet.append(type)
			self.unpacked_packet.append(options)
			self.unpacked_packet.append(chunk_length)
			
			#unpack data if chunk length greater than 0
			self.unpacked_packet.append(self.packet[self.position:self.position+self.chunk_length])
			self.position+=chunk_length
		
	def get_bits(self, value, position, length):
		answer = value & (int((math.pow(2, length)-1)) << position)
		answer = answer >> position
		return answer
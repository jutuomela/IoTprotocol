import struct

class packet():
	global packet_content = b""
	global version = 1
	
	def get_packet():
		
	
	def addHeader():
		a = 0
		a = a | (version<<packet_settings.version_shift)
		a = a | (0<<packet_settings.options_shift) #a = a || (options<<24)	
		a = a | (seq_num<<packet_settings.seq_num_shift) #remember to check sequence number before
		packet_content += struct.pack(">L",a)
		
	def addSub(data):
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_SUB<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)
			packet_content += data

	def addUnSub(data):
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_UNSUB<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)
			packet_content += data

	def addHeartBeat(data):
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_HB<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)
			packet_content += data

	def addData(data):
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_DC<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)

	def addACK():
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_ACK<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)
			packet_content += data

	def addNACK(data):
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_NACK<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)
			packet_content += data

	def addREQ(data):
		if(len(data) > pow(2,packet_setting.chunk_length_field_length+1)-1):
			#ERROR
		else:
			a = 0
			a = a | (packet_settings.type_REQ<<packet_settings.type_shift)
			a = a | (0<<packet_settings.options_shift #no options
			a = a | (len(data)<<packet_settings.chunk_len_shift) 
			packet_content += struct.pack(">L",a)
			packet_content += data
		


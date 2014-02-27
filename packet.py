import struct

class packet():
	global packet_content = b""
	global version = 1
	
	def get_packet():
		return struct.pack("4B4B", )
	
	def addHeader():
		a = 0
		a = a | (version<<28)
		a = a | (0<<24) #a = a || (options<<24)	
		a = a | (seq_num) #remember to check sequence number before
		packet_content += struct.pack(">L",a)
		
	def addSub(data):
		#TODO
		type = 0
		options = 0
		chunk_len =
		chunk_data = data 

		struct.pack( ) 


	def addUnSub():
		#TODO

	def addHeartBeat():
		#TODO

	def addData():

	def addACK():

	def addNACK():

	def addREQ():

		


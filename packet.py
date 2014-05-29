import struct
import packet_settings 

class Packet():
	packet_content = b""
	VERSION = 1
	data_added = False


	def __init__(self,seq_num):
		self.addHeader(seq_num)

	def get_packet(self):
		return self.packet_content



	def addHeader(self,seq_num):
		a = 0
		a = a | (self.VERSION<<packet_settings.VERSION_SHIFT)
		a = a | (0<<packet_settings.OPTIONS_SHIFT)	
		a = a | (seq_num<<packet_settings.SEQ_NUM_SHIFT) #remember to check sequence number before
		self.packet_content += struct.pack(">L",a)

	def addSub(self,data,option):

		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a | (packet_settings.TYPE_SUB<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a | (option<<packet_settings.CHUNK_OPTIONS_SHIFT) #option: initial subscription = 1, additional subscription = 0
		a = a | (len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addUnSub(self,data,option):

		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a | (packet_settings.TYPE_UNSUB<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a | (option<<packet_settings.CHUNK_OPTIONS_SHIFT) #option: unSub one sensor = 0, unSub all=1
		a = a | (len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addHeartBeat(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a|(packet_settings.TYPE_HB<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(0<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addData(self,data):
		print("PACKET: adding data")
		status = self.check_data(data)
		print("PACKET: status: " + str(status))
		print("PACKET: data length" +str(len(data)))
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a|(packet_settings.TYPE_DC<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		print("PACKET: header " + str(a))
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addACK(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a|(packet_settings.TYPE_ACK<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addNACK(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)
		a = 0
		a = a|(packet_settings.TYPE_NACK<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addREQ(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)
		a = 0
		a = a|(packet_settings.TYPE_REQ<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addAGG(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a|(packet_settings.TYPE_AGG<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;


	def addAGR(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)

		a = 0
		a = a|(packet_settings.TYPE_AGR<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;

	def addERR(self,data):
		status = self.check_data(data)
		if status != packet_settings.OKAY:
			return(status)
		
		a = 0
		a = a|(packet_settings.TYPE_ERR<<packet_settings.CHUNK_TYPE_SHIFT)
		a = a|(0<<packet_settings.CHUNK_OPTIONS_SHIFT) #no options
		a = a|(len(data)<<packet_settings.CHUNK_LEN_SHIFT) 
		self.packet_content += struct.pack(">L",a)
		self.packet_content += data
		data_added = True;



	#checks that the data isnt too long and that the packet has
	#enough room to add it along with the header
	def check_data(self, data):
		#check that data isnt too long
		if(len(data) > int(pow(2,packet_settings.CHUNK_LENGTH_FIELD_LENGTH)-1)):
			return packet_settings.DATA_TOO_LONG

		#check that packet has enough space
		if(len(data) + len(self.packet_content) + 1 > packet_settings.MAX_PACKET_LENGTH):  # the +1 is the header length
			return packet_settings.NOT_ENOUGH_SPACE

		return packet_settings.OKAY

	def isDataAdded(self):
                return data_added


class packet_settings():

	MAX_PACKET_LENGTH = 1012

	#packet header
	VERSION= 1
	VERSION_LENGTH = 4
	OPTIONS_LENGTH = 4
	SEQ_NUM_LENGTH = 24
	
	VERSION_SHIFT = 28
	TYPE_SHIFT = 28
	OPTIONS_SHIFT = 24
	SEQ_NUM_SHIFT = 0
	CHUNK_LEN_SHIFT = 0

	#chunks
	TYPE_LENGTH = 4
	PACKET_OPTIONS_LENGTH = 4
	CHUNK_LENGTH_FIELD_LENGTH = 24
	
	TYPE_SUB = 0
	TYPE_UNSUB = 1
	TYPE_HB = 2
	TYPE_DC = 3
	TYPE_ACK = 4
	TYPE_NACK = 5
	TYPE_REQ = 6

	#Status ints
	OKAY = 0
	DATA_TOO_LONG = 1
	NOT_ENOUGH_SPACE = 2

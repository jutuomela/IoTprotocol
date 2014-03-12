
class packet_settings():

	MAX_PACKET_LENGTH = 1012

	#packet headder
	global	VERSION= 1
	global VERSION_LENGTH = 4
	global OPTIONS_LENGTH = 4
	global SEQ_NUM_LENGTH = 24
	
	global VERSION_SHIFT = 28
	global TYPE_SHIFT = 28
	global OPTIONS_SHIFT = 24
	global SEQ_NUM_SHIFT = 0
	global CHUNK_LEN_SHIFT = 0

	#chunks
	global TYPE_LENGTH = 4
	global PACKET_OPTIONS_LENGTH = 4
	global CHUNK_LENGTH_FIELD_LENGTH = 24
	
	global TYPE_SUB = 0
	global TYPE_UNSUB = 1
	global TYPE_HB = 2
	global TYPE_DC = 3
	global TYPE_ACK = 4
	global TYPE_NACK = 5
	global TYPE_REQ = 6

	#Status ints
	OKAY = 0
	DATA_TOO_LONG = 1
	NOT_ENOUGH_SPACE = 2

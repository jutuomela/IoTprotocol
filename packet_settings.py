
class packet_settings():

	#packet headder
	global version = 1
	global version_length = 4
	global options_length = 4
	global seq_num_lenght = 24
	
	#chunks
	global type_length = 4
	global options_length = 4
	global chunk_length_field_length = 28
	
	global type_SUB = 0
	global type_UNSUB = 1
	global type_HB = 2
	global type_DC = 3
	global type_ACK = 4
	global type_NACK = 5
	global type_REQ = 6

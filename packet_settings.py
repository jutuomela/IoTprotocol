
class packet_settings():

	#packet headder
	global version = 1
	global version_length = 4
	global options_length = 4
	global seq_num_lenght = 24
	
	global version_shift = 28
	global type_shift = 28
	global options_shift = 24
	global seq_num_shift = 0
	global chunk_len_shift = 0

	#chunks
	global type_length = 4
	global options_length = 4
	global chunk_length_field_length = 24
	
	global type_SUB = 0
	global type_UNSUB = 1
	global type_HB = 2
	global type_DC = 3
	global type_ACK = 4
	global type_NACK = 5
	global type_REQ = 6

	

import hashlib
import base64
import json
import re
# import logging
import copy

def get_message_service():
	q = Q()
	return q

class Message:
	def __init__(self):
		self.message = dict()
		self.hash = None
		self._hash = None
		self.queue = 3
		self.sequence = None
		self.part_number = None
		self.int_value = None
		self.nested_object = None

	# def __repr__(self):
	# 	return "message: {0}, hash: {1}, sequence: {2}, part_number: {3}".format(self.message, self.hash, self.sequence, self.part_number)

	def get(self):
		if self.hash is not None:
			self.message['hash'] = self.hash
		if self._hash is not None:
			self.message['_hash'] = self._hash
		if self.int_value is not None:
			self.message['int_value'] = self.int_value
		if self.sequence is not None:
			self.message['_sequence'] = self.sequence
			self.message['_part'] = self.part_number

		return self

	def to_string(self):
		return json.dumps(self.message)

class Q:
	def __init__(self):
		self.queue_0 = []
		self.queue_1 = []
		self.queue_2 = []
		self.queue_3 = []
		self.queue_4 = []

	def enqueue(self, message):
		decoded_message = json.loads(message)

		self.apply_transformation_and_dispatch(decoded_message)
		
		return self	

	def apply_transformation_and_dispatch(self, decoded_message):
		new_message = Message()

		def _apply_transformation_and_dispatch(decoded_message, new_message):

			for key, value in decoded_message.items():
				if isinstance(value, str):
					self.set_str_value_transformation(key, value, new_message, decoded_message)

				elif isinstance(value, dict):
					recursed_message = _apply_transformation_and_dispatch(value, Message())
					new_message.message[key] = recursed_message.get().message

					if recursed_message.queue < new_message.queue:
						new_message.queue = recursed_message.queue
				else: # key has a int value
					self.set_int_value_transformation(key, value, new_message, decoded_message)
			return new_message

		v = _apply_transformation_and_dispatch(decoded_message, new_message)
		print(new_message.queue)
		self.dispatch(new_message)

		return v

	def set_str_value_transformation(self, key, value, new_message, decoded_message):
		if key == '_special':
			new_message.queue = 0
	
		# If a message has a field "_hash", it's going to have a field "hash"
		elif key == '_hash':
			base64_encoded = self.encode(decoded_message[value])
			new_message.hash = base64_encoded
			new_message._hash = value

			if new_message.queue  > 1:
				new_message.queue = 1

		elif key == '_sequence' or key == "_part":
			new_message.sequence = decoded_message["_sequence"]
			new_message.part_number = decoded_message["_part"]
		else:
			new_message.message[key] = value

	def set_int_value_transformation(self, key, value, new_message, decoded_message):
		if key not in ('_sequence', '_part'):
			if isinstance(value, dict):
				value = ~value["int_value"]
			else:	
				value = ~value

			new_message.int_value = value

			if new_message.queue  > 2:
				new_message.queue = 2


		return new_message
		
	@classmethod
	def encode(self, value):
		utf_8_encoded = value.encode("utf-8") # Get the Unicode (UTF-8) value of the field specified in "_hash"
		hash_object = hashlib.sha256(utf_8_encoded) # Hash it according to SHA-256
		hex_dig = hash_object.digest() # Get a byte-like object
		base64_encoded = base64.b64encode(hex_dig) # Base 64 Encode

		return str(base64_encoded)

	def dispatch(self, message):
		if message.queue == 0:
			self.queue_0.append(message.get().to_string())
		elif message.queue == 1:
			self.queue_1.append(message.get().to_string())
		elif message.queue == 2:
			self.queue_2.append(message.get().to_string())
		else:
			self.queue_3.append(message.get().to_string())


	def next(self, queue_number):
		if queue_number == 0:	
			message = self.queue_0.pop(0)
		elif queue_number == 1:
			message = self.queue_1.pop(0)
		elif queue_number == 2:
			message = self.queue_2.pop(0)
		else:
			message = self.queue_3.pop(0)

		return message





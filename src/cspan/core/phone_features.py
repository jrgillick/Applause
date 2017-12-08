import numpy as np

class PhoneFeatures:
	def __init__(self, word_list):
		self.word_list = word_list
		self.phone_lengths = self.get_all_phone_lengths()

	def get_all_phone_lengths(self):
		all_phone_lengths = []
		for w in self.word_list:
			all_phone_lengths += [p['duration'] for p in w['phones']]
		return all_phone_lengths

	def get_max_phone_length(self):
		return np.max(self.phone_lengths)

	def get_min_phone_length(self):
		return np.min(self.phone_lengths)

	def get_mean_phone_length(self):
		return np.mean(self.phone_lengths)

	def get_all_features(self):
		return {'max_phone_length': self.get_max_phone_length(), 'min_phone_length': self.get_min_phone_length(), 'mean_phone_length': self.get_mean_phone_length()}

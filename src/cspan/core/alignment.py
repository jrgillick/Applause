import json
import numpy as np

class Alignment:
	def __init__(self,file_path):
		self.alignment_file = file_path
		self.alignments = self.get_alignments()
		self.words = self.get_words()
		self.start_times = self.get_start_times()
		self.end_times = self.get_end_times()
		self.transcript = self.get_transcript()
				
	def get_alignments(self):
		return json.loads(open(self.alignment_file).read())
		
	def get_words(self):
		return self.get_alignments()['words']

	def get_transcript(self):
		return self.get_alignments()['transcript']
		
	def get_start_times(self):
		words = self.get_words()
		return([w['start'] if 'start' in w.keys() else None for w in words])

	def get_end_times(self):
		words = self.get_words()
		return([w['end'] if 'end' in w.keys() else None for w in words])
		
	# Gets the index of the last word that STARTS before the given time t
	def get_last_index_before_time(self, t):
		start_times = self.start_times
		for i in range(len(start_times)):
			if start_times[i] > t:
				return i-1

	def get_preceding_word_indices(self, t, n_words):
		last_index = self.get_last_index_before_time(t)
		count = 1
		pointer = last_index - 1
		word_indices = [last_index]
		while pointer >= 0 and count <= n_words:
			word = self.words[pointer]
			if word['case'] == 'success':
				word_indices.append(pointer)
				count += 1
			pointer -= 1
		word_indices.reverse()
		return word_indices

	# Given start and end times in seconds, get the indices of all words in that span
	def get_indices_within_time_range(self, start_time, end_time):
		last_index = self.get_last_index_before_time(end_time)
		pointer = last_index
		word_indices = []
		current_time = end_time
		while pointer >= 0 and current_time > start_time:
			word = self.words[pointer]	
			if word['case'] == 'success':
				current_time = word['start']
				if current_time > start_time:
					word_indices.append(pointer)
			pointer -= 1
		word_indices.reverse()
		return word_indices

	# Given a list of word indices in the alignment sequence, get the words
	def get_word_list_from_indices(self, indices):
		wlist = list(np.array(self.words)[indices])
		return [w['alignedWord'] for w in wlist]

	# Given a list of word indices in the alignment, get the corresponding characters from the raw transcript
	# This recovers punctuation, capitalization, etc. that was thrown away by forced alignment
	def get_chars_from_indices(self, indices):
		return(self.transcript[self.words[indices[0]]['startOffset']:self.words[indices[-1]]['endOffset']])

	# Given a list of word indices, get the audio start and end times
	# Use this to get the audio for a sequence of words preceding applause
	def get_start_end_times_from_indices(self, indices):
		start = self.words[indices[0]]['start']
		end = self.words[indices[-1]]['end']
		return (start,end)

	def get_preceding_60_word_indices_within_20_seconds(self, start_time):
		indices = self.get_preceding_word_indices(start_time, 60)
		return [i for i in indices if self.words[i]['start'] > start_time - 25]

	def get_preceding_chars(self, start_time):
		indices = self.get_preceding_60_word_indices_within_20_seconds(start_time)
		return self.get_chars_from_indices(indices)


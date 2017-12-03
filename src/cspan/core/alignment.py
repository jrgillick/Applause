import json, numpy as np, spacy, re
import sentence
nlp = spacy.load('en')

class Alignment:
	def __init__(self,file_path):
		self.alignment_file = file_path
		self.alignments = self.get_alignments()
		if self.alignments is None: return
		self.words = self.get_words()
		self.clean_words = self.get_clean_words()
		self.start_times = self.get_start_times()
		self.end_times = self.get_end_times()
		self.transcript = self.get_transcript()
		#self.sentence_list = self.get_sentence_list()
		self.phrase_list = self.get_aligned_phrases(self.clean_words)

	def get_alignments(self):
		try:
			return json.loads(open(self.alignment_file).read())
		except:
			return None
		
	def get_words(self):
		return self.get_alignments()['words']

	def spans_overlap(self,start1, end1, start2, end2):
		if end1 < start2 or end2 < start1: return False
		else: return True

	def no_overlapping_spans(self,span, spans):
		for s in spans:
			if self.spans_overlap(span[0],span[1],s[0],s[1]):
				return False
		return True

	def get_clean_words(self):
		transcript = self.get_alignments()['transcript']
		exp = re.compile("[\[\(][a-zA-Z0-9_ \,\.]*[\]\)]")
		spans = [m.span() for m in exp.finditer(transcript)]
		words = self.get_alignments()['words']
		return [w for w in words if self.no_overlapping_spans((w['startOffset'],w['endOffset']),spans)]

	def get_transcript(self):
		transcript = self.get_alignments()['transcript']
		#exps = [re.compile(exp) for exp in  ["[\[\(][a-zA-Z0-9_ \,\.]*[\]\)]","\.\.\.","\n"]]
		#for exp in exps:
		#	transcript = re.sub(exp, '', transcript)
		return transcript
		
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
		count = 0
		pointer = last_index
		word_indices = []
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
		if len(indices) == 0:
			return ''
		else:
			return(self.transcript[self.words[indices[0]]['startOffset']:self.words[indices[-1]]['endOffset']])

	# an attempt. don't use right now
	def get_aligned_chars_from_indices(self, indices):
		if len(indices) == 0:
			return ''
		else:
			start_index = self.words[indices[0]]['startOffset']
			end_index = self.words[indices[-1]]['endOffset']
			cut_list = [(self.words[i]['startOffset'], self.words[i]['endOffset']) for i in indices if not 'start' in self.words[i]]
			if len(cut_list) > 0:
				print "using"
				for c in cut_list:
					print self.transcript[c[0]:c[1]]
				s = self.transcript[start_index:cut_list[0][0]]
				for index, start_end in enumerate(cut_list[0:-1]):
					start = start_end[0]; end = start_end[1]
					s += self.transcript[end:cut_list[index+1][0]]
				s += self.transcript[cut_list[-1][1]:end_index]
			else:
				s = self.transcript[self.words[indices[0]]['startOffset']:self.words[indices[-1]]['endOffset']]
			return s				
			#return " ".join([self.transcript[self.words[i]['startOffset']:self.words[i]['endOffset']] for i in indices if 'start' in self.words[i]])

	# Given a list of word indices, get the audio start and end times
	# Use this to get the audio for a sequence of words preceding applause
	def get_start_end_times_from_indices(self, indices):
		if len(indices) == 0: return (0.0,0.0)
		i = indices[0]
		start = None; end = None
		for i in indices:
			if 'start' in self.words[i]:
				if start is None:
					start = self.words[i]['start']
		for i in reversed(indices):
			if 'end' in self.words[i]:
				if end is None:
					end = self.words[i]['end']
		return (start,end)

	def get_preceding_chars(self, start_time,max_words=60, max_time=25):
		indices = self.get_preceding_word_indices(start_time, max_words)
		indices = [i for i in indices if self.words[i]['start'] > start_time - max_time]
		return self.get_chars_from_indices(indices)

	def get_preceding_aligned_words(self, start_time,max_words=60, max_time=25):
		indices = self.get_preceding_word_indices(start_time, max_words)
		indices = [i for i in indices if self.words[i]['start'] > start_time - max_time]
		return self.get_word_list_from_indices(indices)

	def get_sentence_list(self):
		sentences = [sent for sent in nlp(self.transcript).sents]
		return [sentence.Sentence(self, s.start_char,s.end_char) for s in sentences]

	def get_indices_from_char_span(self, start_char, end_char):
		i = 0
		start_index = None; end_index = None
		while i < len(self.words) and end_index is None:
			if 'start' in self.words[i]:
				if start_index is None:
					if self.words[i]['startOffset'] >= start_char:
						start_index = i
				if end_index is None:
					if self.words[i]['startOffset'] >= end_char:
						end_index = i
			i += 1
		indices = list(range(start_index,end_index))
		return [i for i in indices if 'start' in self.words[i]]

	def get_aligned_phrases(self,words,min_pause_time=0.7):
		i = 0
		phrase_list = []
		current_phrase = []
		last_end = 0
		while i < len(words):	
			if 'start' in words[i]: # Skip unaligned words
				if len(current_phrase) > 0 and words[i]['start'] > (last_end + min_pause_time):
					phrase_list.append(current_phrase)
					current_phrase = []
				else:
					current_phrase.append(i)
					last_end = words[i]['end']
			i += 1
		return phrase_list

	def get_phrase_times(self):
		words = self.clean_words
		return [(words[phrase[0]]['start'], words[phrase[-1]]['end']) for phrase in self.phrase_list]

	def get_phrase_text(self):
		words = self.clean_words
		return [' '.join([words[i]['word'] for i in p]) for p in self.phrase_list]

	def get_phrase_text_and_times(self):
		words = self.clean_words
		return [[' '.join([words[i]['word'] for i in p]),words[p[0]]['start'],words[p[-1]]['end']] for p in self.phrase_list]

	def get_phrase_text_times_and_mean_applause_volume(self,applause_time=3):
		phrase_text_and_times = self.get_phrase_text_and_times()
		volumes = [np.mean(self.speech.get_rmse_at_times(p[2],p[2] + applause_time)) for p in phrase_text_and_times]
		return [phrase_text_and_times[i] + [volumes[i]] for i in range(len(volumes))]

	def get_phrase_lengths(self,phrase_text):
		return [len(p.split(' ')) for p in phrase_text]

	def get_preceding_phrases(self, start_time, max_time=25):
		phrases = self.get_phrase_text_and_times()
		return [p for p in phrases if p[2] < start_time and p[1] > start_time - max_time]
		

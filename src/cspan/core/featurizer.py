import librosa, numpy as np, pickle, pandas as pd, file_loader
import alignment, applause_list, speech, text_features, vector_features, phone_features
from scipy.spatial.distance import cosine as cosine_distance
from scipy import sparse

with open('/data/corpora/cspan/top_unigrams.pkl') as f:
	top_unigrams = pickle.load(f)

with open('/data/corpora/cspan/top_bigrams.pkl') as f:
	top_bigrams = pickle.load(f)

with open('/data/corpora/cspan/top_trigrams.pkl') as f:
	top_trigrams = pickle.load(f)


def hash_to_list(h):
	keys = h.keys(); keys.sort()
	l = [h[k] for k in keys]
	return l

class Featurizer:
	def __init__(self, s):
		self.s = s

	# assumes order is rst, audio,euphony,liu,phone,substring,word_overlap,cosine
	def get_combined_feature_names(self):
		return np.hstack([self.get_rst_feature_names(),
											self.get_audio_feature_names(),
											self.get_euphony_feature_names(),
											self.get_liu_feature_names(),
											self.get_phone_feature_names(),
											self.get_substring_feature_names(),
											self.get_word_overlap_feature_names(),
											self.get_cosine_feature_names()])

	def get_substring_feature_names(self):
		return ['substring']

	def get_word_overlap_feature_names(self):
		return ['word_overlap']

	def get_cosine_feature_names(self):
		return ['cosine']

	def get_audio_feature_names(self):
		h = self.s.phrase_audio_features[0]
		keys = h.keys(); keys.sort()
		return keys

	def get_euphony_feature_names(self):
		text = self.s.alignment.get_phrase_text()
		tfs = text_features.TextFeatures(text[0]).get_euphony_features()
		keys = tfs.keys(); keys.sort()
		return keys

	def get_rst_feature_names(self):
		return open('/data/corpora/cspan/rst_feature_names.txt').read().split('\n')
	
	def get_liu_feature_names(self):
		text = self.s.alignment.get_phrase_text()
		tfs = text_features.TextFeatures(text[0]).get_liu_features()
		keys = tfs.keys(); keys.sort()
		return keys

	def get_name_feature_names(self):
		text = self.s.alignment.get_phrase_text()
		tfs = text_features.TextFeatures(text[0]).get_name_features()
		keys = tfs.keys(); keys.sort()
		return keys

	def get_phone_feature_names(self):
		phrase_list = self.s.alignment.phrase_list
		phone_feats = phone_features.PhoneFeatures(list(np.array(self.s.alignment.clean_words)[phrase_list[0]]))
		keys = phone_feats.get_all_features().keys(); keys.sort()
		return keys

	def get_text_and_labels(self):
		tta = self.s.alignment.get_phrase_text_times_and_mean_applause_volume()
		text = [t[0] for t in tta]
		times = [t[1:3] for t in tta]
		volumes = [t[3] for t in tta]
		binary_labels = [int(self.s.alignment.applause_follows(t[1])) for t in times]
		return text, volumes, binary_labels

	def get_euphony_features(self):
		text = self.s.alignment.get_phrase_text()
		tfs = [text_features.TextFeatures(t) for t in text]
		feats = [hash_to_list(tf.get_euphony_features()) for tf in tfs]
		return feats

	def get_liu_features(self):
		text = self.s.alignment.get_phrase_text()
		tfs = [text_features.TextFeatures(t) for t in text]
		feats = [hash_to_list(tf.get_liu_features()) for tf in tfs]
		return feats

	def get_name_features(self):
		text = [t.lower() for t in self.s.alignment.get_phrase_text()]		
		tfs = [text_features.TextFeatures(t) for t in text]
		feats = [hash_to_list(tf.get_name_features()) for tf in tfs]
		return feats

	def get_rst_features(self):
		rst_feature_names = open('/data/corpora/cspan/rst_feature_names.txt').read().split('\n')
		#rst_file_path = '/data/dbamman/cspan/phrase_list_lower/' + self.s.file_path.split('/')[1] + '.txt.combined.rst_features'
		rst_file_path = '/data/dbamman/cspan/new_phrase_list/' + self.s.file_path.split('/')[1] + '.txt.combined.rst_features'
		rst_lines = open(rst_file_path).read().split('\n')[0:-1]
		split_lines = [l.split(' ') for l in rst_lines]
		feature_name_lists = [[l.split(':')[0] for l in line] for line in split_lines]
		feats = []
		if len(rst_lines) != len(self.s.alignment.get_phrase_text()):
			print "RST failed for " + self.s.file_path
			return
		for line in feature_name_lists:
			h = {}
			for n in rst_feature_names:
				h[n] = 0
			for feature in line:
				h[feature] = 1
			feats.append(hash_to_list(h))
		return feats

	def get_binary_labels(self):
		times = self.s.alignment.get_phrase_times()
		return [int(self.s.alignment.applause_follows(t[1])) for t in times]

	def get_skip_thought_features(self):
		text = self.s.alignment.get_phrase_text()
		return vector_features.VectorFeatures(text).skip_thought_vectors

	def get_phone_features(self):
		phrase_list = self.s.alignment.phrase_list
		phone_feats = [phone_features.PhoneFeatures(list(np.array(self.s.alignment.clean_words)[word_list])) for word_list in phrase_list]
		feats = [hash_to_list(p.get_all_features()) for p in phone_feats]
		return feats

	def get_vector_cosine_distances(self):
		vectors = self.get_skip_thought_features()
		sims = [cosine_distance(vectors[0],vectors[1])] #no i-1 for first timestep
		for i in range(1,len(vectors)):
			sims.append(cosine_distance(vectors[i], vectors[i-1]))
		return sims

	def longest_common_substring(self, s1, s2):
		m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
		longest, x_longest = 0, 0
		for x in xrange(1, 1 + len(s1)):
			for y in xrange(1, 1 + len(s2)):
				if s1[x - 1] == s2[y - 1]:
					m[x][y] = m[x - 1][y - 1] + 1
					if m[x][y] > longest:
						longest = m[x][y]
						x_longest = x
				else:
					m[x][y] = 0
		return len(s1[x_longest - longest: x_longest])

	def get_common_substring_features(self):
		text = [t.lower() for t in self.s.alignment.get_phrase_text()]
		feats = [0] # no i-1 for first timestep
		for i in range (1,len(text)):
			feats.append(self.longest_common_substring(text[i],text[i-1]))
		return feats

	def get_n_common_words(self):
		text = [t.lower() for t in self.s.alignment.get_phrase_text()]
		feats = [0] # no i-1 for first timestep
		for i in range (1,len(text)):
			feats.append(len(set(text[i].split(' ')) & set(text[i-1].split())))
		return feats

	def get_unigram_features(self):
		with open('/data/corpora/cspan/top_unigrams.pkl','rb') as f:
			unigrams = pickle.load(f)
		word_lists = [t.lower().split(' ') for t in self.s.alignment.get_phrase_text()]
		feats = []
		for word_list in word_lists:
			h = {}
			keys = [u[0] for u in unigrams]
			for k in keys:
				h[k] = 0
			for word in word_list:
				if word in keys: 
					h[word] = 1
			feats.append(hash_to_list(h))
		return np.array(feats)

	def get_bigram_features(self):
		with open('/data/corpora/cspan/top_bigrams.pkl','rb') as f:
			bigrams = pickle.load(f)
		phrases = [t.lower() for t in self.s.alignment.get_phrase_text()]
		feats = []
		keys = [u[0] for u in bigrams]
		for phrase in phrases:
			h = {}
			#keys = [u[0] for u in bigrams]
			for k in keys:
				h[k] = 0
			grams = text_features.TextFeatures(phrase).get_n_grams(2)
			for gram in grams:
				if gram in keys: 
					h[gram] = 1
			feats.append(hash_to_list(h))
		return np.array(feats)

	def get_trigram_features(self):
		with open('/data/corpora/cspan/top_trigrams.pkl','rb') as f:
			trigrams = pickle.load(f)
		phrases = [t.lower() for t in self.s.alignment.get_phrase_text()]
		feats = []
		keys = [u[0] for u in trigrams]
		for phrase in phrases:
			h = {}
			#keys = [u[0] for u in trigrams]
			for k in keys:
				h[k] = 0
			grams = text_features.TextFeatures(phrase).get_n_grams(3)
			for gram in grams:
				if gram in keys: 
					h[gram] = 1
			feats.append(hash_to_list(h))
		return np.array(feats)

	def get_mean_vector_features(self):
		text = self.s.alignment.get_phrase_text()
		return [text_features.TextFeatures(unicode(text)).get_mean_vector(t) for t in text]

	#def get_all_features(self):
	#	return np.hstack([self.get_audio_features(),self.get_euphony_features(),self.get_liu_features()])

	# TODO fix hack for missing data
	def get_audio_features(self):
		l = []
		for f in self.s.phrase_audio_features:
			if f is not None:
				l.append(hash_to_list(f))
				last_not_none = hash_to_list(f)
			else:
				l.append(last_not_none)
		return l
		#return [hash_to_list(f) for f in self.s.phrase_audio_features]

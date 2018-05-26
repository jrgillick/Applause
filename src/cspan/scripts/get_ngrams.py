import sys, os, pickle
from tqdm import tqdm

sys.path.insert(0, '../core')

import speech, text_features

with open('/data/jrgillick/speeches.pkl') as f:
	bigram_vocab = {}
	bigram_counts = {}
	trigram_vocab = {}
	trigram_counts = {}
	speeches = pickle.load(f)
	bigram_index = 0
	trigram_index = 0
	for s in tqdm(speeches):
		phrases = s.alignment.get_phrase_text()
		for phrase in phrases:
				tf = text_features.TextFeatures(phrase)
				bigrams = tf.get_n_grams(2)
				trigrams = tf.get_n_grams(3)

				for bigram in bigrams:
					if bigram not in bigram_vocab:
						bigram_vocab[bigram] = bigram_index
						bigram_counts[bigram] = 1
						bigram_index += 1
					else:
						bigram_counts[bigram] += 1

				for trigram in trigrams:
					if trigram not in trigram_vocab:
						trigram_vocab[trigram] = trigram_index
						trigram_counts[trigram] = 1
						trigram_index += 1
					else:
						trigram_counts[trigram] += 1

	with open('/data/corpora/cspan/bigram_vocab.pkl','wb') as f:
		pickle.dump(bigrams, f)
	with open('/data/corpora/cspan/bigram_counts.pkl','wb') as f:
		pickle.dump(bigram_counts, f)
	with open('/data/corpora/cspan/trigram_vocab.pkl','wb') as f:
		pickle.dump(trigrams, f)
	with open('/data/corpora/cspan/trigram_counts.pkl','wb') as f:
		pickle.dump(trigram_counts, f)

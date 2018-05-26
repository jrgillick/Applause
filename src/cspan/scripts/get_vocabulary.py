import sys, os, pickle
from tqdm import tqdm

sys.path.insert(0, '../core')

import speech

with open('/data/jrgillick/speeches.pkl') as f:
	vocab = {}
	counts = {}
	speeches = pickle.load(f)
	index = 0
	for s in tqdm(speeches):
		speech_words = " ".join(s.alignment.get_phrase_text()).split(" ")
		for word in speech_words:
			word = word.lower()
			if word not in vocab:
				vocab[word] = index
				counts[word] = 1
				index += 1
			else:
				counts[word] += 1
	with open('/data/corpora/cspan/vocabulary.pkl','wb') as f:
		pickle.dump(vocab, f)
	with open('/data/corpora/cspan/vocabulary_counts.pkl','wb') as f:
		pickle.dump(counts, f)

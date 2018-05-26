import speech, featurizer
from sklearn.utils import shuffle
import numpy as np
from tqdm import tqdm

def get_vector_cosine_distance_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feats.append(f.get_vector_cosine_distances())
	return feats
	
def get_mean_vector_data(speeches):
	feats = []
	labs = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feats.append(f.get_mean_vector_features())
		labs.append(f.get_binary_labels())
	return feats, labs

def get_skip_thought_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feats.append(f.get_skip_thought_features())
	return feats

def get_rst_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feats.append(f.get_rst_features())
	return feats

def get_liu_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_liu_features()
		feats.append(np.array(feat))
	return feats

def get_name_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_name_features()
		feats.append(np.array(feat))
	return feats

def get_unigram_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_unigram_features()
		feats.append(np.array(feat))
	return feats

def get_bigram_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_bigram_features()
		feats.append(np.array(feat))
	return feats

def get_trigram_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_trigram_features()
		feats.append(np.array(feat))
	return feats

def get_euphony_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_euphony_features()
		feats.append(np.array(feat))
	return feats

def get_audio_data(speeches):
	feats = []
	for s in tqdm(speeches):
		s.phrase_audio_features = s.get_phrase_audio_features()
		f = featurizer.Featurizer(s)
		feat = f.get_audio_features()
		feats.append(np.array(feat))
	return feats

def get_phone_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_phone_features()
		feats.append(np.array(feat))
	return feats

def get_substring_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = f.get_common_substring_features()
		feats.append(np.array(feat))
	return feats

def get_word_overlap_data(speeches):
	feats = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		feat = [f.get_n_common_words()]
		feats.append(np.array(feat))
	return feats

def get_binary_labels(speeches):
	labs = []
	for s in tqdm(speeches):
		f = featurizer.Featurizer(s)
		labs.append(f.get_binary_labels())
	return labs


# Throw away extra negative examples until you have balanced data
def balance(X,y):
	X,y = shuffle(X,y)
	positive_indices = [i for i,lab in enumerate(y) if lab == 1]
	negative_indices = [i for i,lab in enumerate(y) if lab == 0]
	negative_indices = negative_indices[0:len(positive_indices)]
	X = [x for i,x in enumerate(X) if i in positive_indices or i in negative_indices]
	y = [x for i,x in enumerate(y) if i in positive_indices or i in negative_indices]
	return (X,y)

def get_mean_phrase_time(s):
	return np.mean([t[1]-t[0] for t in s.alignment.get_phrase_times()])

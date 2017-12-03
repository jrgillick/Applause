import numpy as np, re, spacy
nlp = spacy.load('en')
import pronouncing

#### Useful methods that don't need to be in the Class

# combine list of lists
flatten = lambda l: [item for sublist in l for item in sublist]

# get all flat LIWC categories for a word
def getLIWC(word):
	vals=[]
	if word in liwc:
		vals.extend(liwc[word])
	if len(word) > 1:
		pref=word[0:2]
		if pref in regex_liwc:
			cands=regex_liwc[pref]
			for cand in cands:
				if re.match(cand, word) != None:
					vals.extend(regex_liwc[pref][cand])
	return vals

def readLIWC(filename):
	liwc_vocab={}
	regex_liwc={}
	liwc={}
	
	# Liu et al. excludes "affective or emotional processes"
	invalid={}
	invalid["31"]=1
	invalid["32"]=1
	invalid["33"]=1
	invalid["34"]=1
	invalid["35"]=1

	file=open(filename)
	for i in range(75):
		line=file.readline()
		cols=re.split("\s+", line.rstrip())
		if line.rstrip() != "%":
			idd="%s" % cols[0]
			label=cols[1]
			liwc_vocab[idd]=label
	for line in file:
		cols=line.rstrip().split("\t")
		term=cols[0]
		valid=[]
		for x in cols[1:]:
			if x not in invalid:
				valid.append(x)
		cats=["LIWC_%s" % liwc_vocab[x] for x in valid]

		if term.endswith("*"):
			pref=term[0:2]
			if pref not in regex_liwc:
				regex_liwc[pref]={}
			regex_liwc[pref][term]=cats
		else:
			liwc[term]=cats
			
	return (liwc_vocab, regex_liwc, liwc)

liwc_path = '/data/corpora/LIWC/LIWC.txt'
liwc_vocab, regex_liwc, liwc = readLIWC(liwc_path)

def get_counts(l):
	h = {}
	for item in l:
		if item in h:
			h[item] += 1
		else:
			h[item] = 1
	return h

# given a single pair of lists, count the number of entries that match continuously from the start
def count_matching_prefix_length(l1,l2):
	c = 0
	for i in range(min(len(l1),len(l2))):
		if l1[i] == l2[i]:
			c += 1
	else:
		return c
	return c

# For a list of lists, count the prefixes that match between any 2 pairs
def count_matching_prefixes(l):
	total_count = 0
	for i,p in enumerate(l):
		for j,p2 in enumerate(l):
			if i < j:
				total_count += count_matching_prefix_length(p,p2)
	return total_count

# For a list of lists, count the suffixes that match between any 2 pairs
def count_matching_suffixes(l):
	total_count = 0
	for i,p in enumerate(l):
		for j,p2 in enumerate(l):
			if i < j:
				total_count += count_matching_suffix_length(p,p2)
	return total_count

def count_matching_suffix_length(l1,l2):
	return count_matching_prefix_length(list(reversed(l1)),list(reversed(l2)))

plosive_list = ['P','T','K','B','D','G']


########

class TextFeatures:
	def __init__(self, raw_text):
		self.raw_text = raw_text
		self.doc = self.get_doc()
		self.words = self.raw_text.split(' ')
		#self.sentences = self.get_sentences()

		self.phone_list = self.get_phone_list()
		self.split_phone_list = [p.split(' ') for p in self.phone_list]
		self.phone_count = self.get_phone_count()

	

	#### Methods for Euphony Features
	def get_phone_list(self):
		return [pronouncing.phones_for_word(w.lower())[0] for w in self.words]

	def get_phone_count(self):
		return sum([len(p) for p in self.split_phone_list])

	def get_all_phones(self):
		all_phones = []
		for p in self.split_phone_list:
			all_phones += p
		return all_phones

	def get_distinct_phone_count(self):
		return len(get_counts(self.get_all_phones()).keys())

	#def get_syllable_count(self):
	#	return sum([pronouncing.syllable_count(p) for p in self.phone_list])

	def get_rhyme_feature(self):
		repeated_suffixes = count_matching_suffixes(self.split_phone_list)
		return float(repeated_suffixes) / self.phone_count

	def get_homogeneity_feature(self):
		return 1 - (float(self.get_distinct_phone_count()) / self.phone_count)

	def get_alliteration_feature(self):
		repeated_prefixes = count_matching_prefixes(self.split_phone_list)
		return float(repeated_prefixes) / self.phone_count

	def get_plosive_feature(self):
		return float(len([p for p in self.get_all_phones() if p in plosive_list])) / self.phone_count

	def get_euphony_features(self):
		return {
			'rhyme' : self.get_rhyme_feature(), 
			'alliteration': self.get_alliteration_feature(),
			'homogeneity': self.get_homogeneity_feature(),
			'plosive': self.get_plosive_feature()
		}

	#########

	#### Methods for the Liu TED features

	def get_applause_feature(self):
		text = self.raw_text.lower() 
		exp = re.compile("applau*")
		return 1 if len(re.findall(exp,text)) > 0 else 0

	def get_thank_you_feature(self):
		text = self.raw_text.lower() 
		exp = re.compile("grateful*|thank*|gratitud*|appreciate*|bless*")
		return 1 if len(re.findall(exp,text)) > 0 else 0

	def get_liwc_features(self):
		all_keys = ["LIWC_" + v for v in liwc_vocab.values()]
		keys = list(set(flatten([getLIWC(w.lower()) for w in self.words])))
		h = {}
		for k in all_keys:
			h[k] = 1 if k in keys else 0
		return h

	##########


	##### Methods for word vector features

	def get_skip_thought_vector(self):
		return

	def get_mean_vector(self, sentence_list):
		if len(sentence_list) == 0:
			return np.zeros(300)
		else:
			return np.mean(np.array([nlp(sent).vector for sent in sentence_list]),axis=0)

	##########


	##### Methods for sentence splitting

	def get_doc(self):
		return nlp(self.raw_text)

	def get_sentences(self):
		sentences = []
		for sentence in self.doc.sents:
			words=[]
			for word in sentence:
				if re.search("\S", word.string) != None:
					words.append(word.string)
			text=' '.join(words)
			if re.match("^\(.*?\)$", text) != None or re.search("\w", text) == None:
				continue
			sentences.append(text)
		return sentences

	##########

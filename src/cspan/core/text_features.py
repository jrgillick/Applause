import numpy as np, re, spacy
nlp = spacy.load('en')

class TextFeatures:
	def __init__(self, raw_text):
		self.raw_text = raw_text
		self.doc = self.get_doc()
		self.sentences = self.get_sentences()

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

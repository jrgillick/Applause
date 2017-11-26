#import numpy as np, spacy, os, re
#nlp = spacy.load('en')
#import alignment

class Sentence:
	def __init__(self, alignment, start_index, end_index):
		self.alignment = alignment
		self.start_index = start_index
		self.end_index = end_index
		self.text = self.alignment.transcript[start_index:end_index]

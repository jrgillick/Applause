import sys
sys.path.insert(0, '/data/jrgillick/skip-thoughts')

import skipthoughts
model = skipthoughts.load_model()
encoder = skipthoughts.Encoder(model)

class VectorFeatures:
	def __init__(self, text_list):
		self.skip_thought_vectors = encoder.encode(text_list,verbose=False)

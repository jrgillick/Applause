import json
import os
import pickle
import json
from IPython.display import Audio
import keras
import numpy as np
import librosa
from sklearn.utils import shuffle
import pandas as pd
from keras.models import load_model
import speech, alignment, applause_list
s = speech.Speech('donald_trump/donald_trump_10')
applause_list = applause_list.ApplauseList(s.applause_times_file)
instances = applause_list.get_instances()
align = alignment.Alignment(s.alignment_file)
words = align.get_words()
start_times = align.get_start_times()
end_times = align.get_end_times()
indices = align.get_preceding_word_indices(instances[0][0],10)
word_list = align.get_word_list_from_indices(indices)

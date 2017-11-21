import os, sys
import pickle
from IPython.display import Audio
import keras
import numpy as np
import librosa
from sklearn.utils import shuffle
import pandas as pd
from keras.models import load_model
import tensorflow as tf

global frame_rate

def extract_features(f):
    try:
        y, sr = librosa.load(f)
        mfcc = librosa.feature.mfcc(y,n_mfcc=13)
        delta = librosa.feature.delta(mfcc)
        return np.vstack([mfcc,delta])
    except:
        print "%s failed" % (f)

def get_features_and_labels(S,window_size):
    features = []
    for i in range(window_size,S.shape[1]-window_size):
        feature = S[:,i-window_size:i+window_size]
        features.append(feature.reshape((-1)))
    return features

def normalize_X(X,means,std_devs):
    for i in xrange(X.shape[1]):
        X[:,i] -= means[i]
        X[:,i] /= std_devs[i]
    return X

def get_applause_instances(probs, threshold = 0.5, min_length = 25):
    instances = []
    current_list = []
    for i in xrange(len(probs)):
        if np.min(probs[i:i+1]) > threshold:
            current_list.append(i)
        else:
            if len(current_list) > 0:
                instances.append(current_list)
                current_list = []

    instances = [frame_span_to_time_span(collapse_to_start_and_end_frame(i)) for i in instances if len(i) > min_length]
    return instances

def frame_to_time(frame_index):
    return(frame/frame_rate)

def seconds_to_frames(s):
    return(int(s*frame_rate))

def collapse_to_start_and_end_frame(instance_list):
    return (instance_list[0], instance_list[-1])

def frame_span_to_time_span(frame_span):
    return (frame_span[0] / frame_rate, frame_span[1] / frame_rate)

def seconds_to_samples(s,sr):
    return s*sr
with open('../../Detection/means.pkl','r') as f:
    means = pickle.load(f)
    
with open('../../Detection/std_devs.pkl', 'r') as f:
    std_devs = pickle.load(f)

talk_audio_root = '/data/corpora/cspan/audio/'
speech_dirs = [talk_audio_root + f + '/' for f in os.listdir(talk_audio_root)]
files = []
for d in speech_dirs:
    files += [d + f for f in os.listdir(d)]
    
#applause_times_root_dir = '/data/corpora/cspan/applause_times/' 
applause_levels_root_dir = '/data/corpora/cspan/applause_levels/'

def find_and_save_applause_times(speech_audio_file):
    print speech_audio_file
    outfile = applause_levels_root_dir + speech_audio_file.split('audio/')[1].replace('.mp3','.txt')
    print outfile
    y, sr = librosa.load(speech_audio_file)
    feats = extract_features(speech_audio_file)
    all_features = np.array(get_features_and_labels(feats,5))
    all_features = normalize_X(all_features,means,std_devs)
    preds = model.predict_proba(all_features,batch_size=256)
    #smooth_preds = pd.rolling_mean(preds,5)[4:]
    with open(outfile,'wb') as f:
      pickle.dump(preds, f)


if __name__ == '__main__':
    start_file = int(sys.argv[1]); end_file = int(sys.argv[2])
    files=files[start_file:end_file]
    from keras.backend.tensorflow_backend import set_session
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.075
    set_session(tf.Session(config=config))
    model = load_model('../../Detection/applause_model.h5')
    for f in files:
        find_and_save_applause_times(f)

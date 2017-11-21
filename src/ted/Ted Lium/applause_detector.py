import keras
from keras.models import load_model
import pickle, librosa, numpy as np, pandas as pd

class ApplauseDetector:
    def __init__(self, model_file, means_file, std_devs_file):
        self.model = load_model(model_file)
        with open(means_file,'r') as f:
            self.means = pickle.load(f)
        with open(std_devs_file,'r') as f:
            self.std_devs = pickle.load(f)
        
    def predict(self,y,sr):
        feats = self.extract_features(y,sr)
        all_features = np.array(self.get_features_and_labels(feats,5))
        all_features = self.normalize_X(all_features,self.means,self.std_devs)
        return self.model.predict_proba(all_features,batch_size=256,verbose=False)
    
    def classify(self,y,sr):
        preds = self.predict(y,sr)
        return np.max(pd.rolling_mean(preds,10)[9:]) > 0.5
    
    def extract_features(self,y,sr):
        mfcc = librosa.feature.mfcc(y,n_mfcc=13)
        delta = librosa.feature.delta(mfcc)
        return np.vstack([mfcc,delta])
    
    def get_features_and_labels(self,S,window_size):
        features = []
        for i in range(window_size,S.shape[1]-window_size):
            feature = S[:,i-window_size:i+window_size]
            features.append(feature.reshape((-1)))
        return features
    
    def normalize_X(self,X,means,std_devs):
        for i in xrange(X.shape[1]):
            X[:,i] -= means[i]
            X[:,i] /= std_devs[i]
        return X
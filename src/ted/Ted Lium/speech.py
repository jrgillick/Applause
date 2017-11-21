import re, librosa

class Speech:
    def __init__(self, stm_filename):
        self.stm_filename = stm_filename
        self.sph_filename = self.get_sph_filename()
        self.sequences = self.get_sequences()
    
    def get_sph_filename(self):
        return self.stm_filename.replace("stm","sph")
        
    def get_sequences(self):
        lines = open(self.stm_filename).read().split("\n")
        lines = [l for l in lines if l != '']
        return [self.create_line(l) for l in lines]
        
    def create_line(self, line):
        #metadata, text = tuple(re.split(' <F0_[MF]> ',line))
        metadata, speaker_type, text = tuple(re.split(' <(.+)> ',line))
        sm = metadata.split(' ')
        return {'id': sm[0], 'channel': sm[1], 'speaker': sm[2], 'bt':sm[3], 'et':sm[4], 
                'speaker_type': speaker_type, 'text': text, 'applause_follows': False, 'laughter_follows': False}
    
    def load_audio(self):
        self.y, self.sr = librosa.load(self.sph_filename)
        
    def get_audio_sequence(self, line):
        bt = line['bt']; et = line['et']
        return self.y[int(float(line['bt'])*self.sr):int(float(line['et'])*self.sr)]
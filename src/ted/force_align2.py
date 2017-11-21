import pickle
import os, sys
import re
import spacy
from sklearn.utils import shuffle

reload(sys)
sys.setdefaultencoding('utf8')

nlp = spacy.load('en')

class Transcript:
    def __init__(self, filename):
        self.filename = filename
        self.sequences = self.get_sequences()
        self.sentences = self.get_sentence_list()
        
    def get_text(self):
        return open(self.filename).read()
    
    def get_split_lines(self):
        text = self.get_text()
        lines = text.split("\n")
        lines = [l for l in lines if l != '']
        return [line.split("\t") for line in lines]
    
    def get_paragraphs(self):
        split_lines = self.get_split_lines()
        return [l[1] for l in split_lines]
        
    def get_timestamps(self):
        split_lines = self.get_split_lines()
        return [l[0] for l in split_lines]
        
    def get_sentences(self, paragraph):
        #par = unicode(paragraph).encode("utf-8")
        paragraph = paragraph.replace('(Laughter)','')
        sentences = []
        doc = nlp(paragraph)
        for sentence in doc.sents:
            words=[]
            for word in sentence:
                if re.search("\S", word.string) != None:
                    words.append(word.string)
            text=' '.join(words)
            if re.match("^\(.*?\)$", text) != None or re.search("\w", text) == None:
                continue
            sentences.append(text)
        return sentences
    
    def get_words(self):
        words = []
        paragraphs = [p.replace("(Laughter)","").replace("(Applause)","") for p in self.get_paragraphs()]
        for p in paragraphs:
            words += p.split(' ')
        return words
    
    def get_sentences_with_applause_interspersed(self, paragraph):
        paragraph = paragraph.replace('(Laughter)','')
        lines = paragraph.split("(Applause)")
        last_line = lines[-1]; lines = lines[0:-1]  # Don't add applause after last line
        sentences = []
        for line in lines:
            sentences += self.get_sentences(line)
            sentences.append("(Applause)")
        sentences += self.get_sentences(last_line)
        return sentences
      
    def get_sequences(self):
        sequences = []
        split_lines = self.get_split_lines()
        for line in split_lines:
            if "(Applause)" in line[1] and line[1] != "(Applause)":
                timestamp = line[0]; paragraph = line[1]
                sentences = self.get_sentences_with_applause_interspersed(paragraph)
                sequences.append((timestamp, paragraph, sentences))
                #special_cases.append(line[1])
            elif line[1] == "(Applause)":
                timestamp = line[0]; paragraph = line[1]; sentences = ["(Applause)"]
                sequences.append((timestamp, paragraph, sentences))
            else:
                timestamp = line[0]; paragraph = line[1]; sentences = self.get_sentences(paragraph)
                sequences.append((timestamp, paragraph, sentences))
        return sequences
    
    def get_sentence_list(self):
        all_sentences = []
        seqs = self.sequences[0:-1] #exclude last paragraph, which may be final applause
        for sequence_index, sequence in enumerate(seqs): 
            sentences = sequence[2]
            for sentence_index, s in enumerate(sentences):
                if s != "(Applause)":
                    features = np.concatenate((self.get_dense_liwc_features(s),self.get_word_vec_features(s)))
                    # If this is not the last sentence in the seq, check if next sentence in this sequence is applause
                    if sentence_index < len(sentences)-1 and sentences[sentence_index+1] == "(Applause)":
                        applause_follows = 1
                    # If this is the last sentence of this sequence, check first sentence of next sequence
                    elif sentence_index == len(sentences) -1 and sequence_index < len(seqs) - 1:
                        next_sentences = seqs[sequence_index+1][2]
                        if len(next_sentences) > 0 and next_sentences[0] == "(Applause)":
                            applause_follows = 1
                        else:
                            applause_follows = 0    
                    else:
                        applause_follows = 0
                    all_sentences.append((s,features,applause_follows))
        return all_sentences
    
    def get_word_vector_list(self, sentence):
        vecs = []
        for word in nlp(sentence):
            if re.search("\S", word.string) != None: vecs.append(word.vector)
        return np.array(vecs)
    
    def compute_word_features(self):
        self.word_features = []
        for index, sentence in enumerate(self.sentences):
            s = sentence[0]
            word_vecs = self.get_word_vector_list(s)
            self.word_features.append(word_vecs)# self.sentences[index] = (sentence[0], sentence[1], sentence[2], word_vecs)
    
    def compute_alignments(self):
        sentences = [s[0].replace(" '","'") for s in self.sentences]
        alignment_file = self.filename.replace('transcripts_clean','forced_alignments').replace('.html','.json')
        words = json.loads(open(alignment_file).read())['words']
    
    def get_words_in_sentence(self, sentence):
        return [word for word in nlp(sentence) if re.search("\S", word.string) != None]

    def count_words_in_sentence(self, sentence):
        return len(self.get_words_in_sentence(sentence))
    
    def compute_word_count_list(self):
        self.word_count_list = []
        for sentence in self.sentences:
            self.word_count_list.append(self.count_words_in_sentence(sentence[0]))
            
    def count_preceding_words(self, index):
        return np.sum (self.word_count_list[0:index+1])
    
    def count_applause_instances(self):
        c = 0
        sentence_list = self.sentences
        for s in sentence_list:#[0:-1]:
            if s[2] == 1:
                c += 1
        return c
    
    def get_applause_yes_sentences(self):
        return [s for s in self.sentences if s[2] == 1]
    
    def get_applause_no_sentences(self):
        no_sentences = [s for s in self.sentences if s[2] == 0]
        shuffle(no_sentences)
        return no_sentences[0:len(self.get_applause_yes_sentences())]
    
    def get_sparse_liwc_features(self, sentence):
        counts = {}
        text = sentence.lower().split(' ')
        for word in text:
            cats=getLIWC(word)
            for cat in cats:
                if vocab[cat] in counts:
                    counts[vocab[cat]] += 1  # = 1
                else:
                    counts[vocab[cat]] = 1.
            if word in vocab:
                if vocab[word] in counts:
                    counts[vocab[word]] += 1  # = 1
                else:
                    counts[vocab[word]] = 1
        return counts
    
    def get_dense_liwc_features(self,sentence):
        a = np.zeros(len(vocab))
        sparse_feats = self.get_sparse_liwc_features(sentence)
        for k in sparse_feats.keys():
            a[k-1] = float(sparse_feats[k]) / len(sentence)
        return a
        
    def get_word_vec_features(self,sentence):
        return nlp(sentence).vector

def load_transcripts(filename="good_transcripts.pkl"):
    with open(filename, 'rb') as f:
        return pickle.load(f)

all_transcripts = load_transcripts()

"""
def get_liu_transcript_paths():
    pathname="/data/corpora/ted/transcripts_clean/"
    files = [pathname + f for f in os.listdir(pathname)]
    talk_names_path = "talk_names.txt"
    talk_names = open(talk_names_path).read().replace('.txt','.html').split('\n')
    talk_names = ['isabel_allende_how_to_live_passionately_no_matter_your_age.html' if t == 'isabelle_allende_how_to_live_passionately_no_matter_your_age.html' else t for t in talk_names]
    talk_names = [t for t in talk_names if t not in ['', 'test.html', '\r']]
    transcripts = [pathname + t for t in talk_names]
    return(transcripts)

transcripts = get_liu_transcript_paths()
len(transcripts)

alignments_dir = '/data/corpora/ted/old_forced_alignments/'
alignments_files = os.listdir(alignments_dir)

matched = []
for t in transcripts:
    matcher = t.split("/")[-1].replace(".html", ".json")
    if matcher in alignments_files:
        matched.append(t)
"""



c = 0
for t in all_transcripts:
    json_file = t.filename.replace("/transcripts_clean","/forced_alignments").replace(".html",".json")
    if not os.path.exists(json_file): #t.filename in matched:
        txt = " ".join([s[0] for s in t.sentences]).replace(" \'","\'")
        with open("temp_text.txt", "wb") as f:
            f.write(txt)
        audio_file = t.filename.replace("/transcripts_clean","/audio").replace(".html",".mp3")
        cmd = "cp " + audio_file + " temp_audio.mp3"
        print cmd
        os.system(cmd)
        json_file = t.filename.replace("/transcripts_clean","/forced_alignments").replace(".html",".json")
        alignment_cmd = "curl -X POST -F 'audio=@temp_audio.mp3' -F 'transcript=<temp_text.txt' 'http://localhost:32769/transcriptions?async=false' > " + json_file
        print alignment_cmd
        os.system(alignment_cmd)

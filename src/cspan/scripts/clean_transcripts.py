import os

transcripts_dir = '/data/corpora/cspan/transcripts/'
clean_transcripts_dir = '/data/corpora/cspan/transcripts_clean/'

folders = os.listdir(transcripts_dir)

def convert_folder(folder):
    transcript_files = os.listdir(transcripts_dir + folder)
    for transcript_file in transcript_files:
        transcript_file_name = transcripts_dir + folder + "/" + transcript_file
        clean_file_name = clean_transcripts_dir + folder + "/" + transcript_file
        if os.path.exists(transcript_file_name) and not os.path.exists(clean_file_name):
            print transcript_file_name
            lines = open(transcript_file_name).read().split('\n')
            link = lines[0]
            speaker_list = lines[1]
            full_text = ""
            lines=lines[2:]
            for line in lines:
                if '\t' in line:
                    timestamp,speaker,text = line.split('\t')
                    full_text += text + '\n'
            with open(clean_file_name,'wb') as outfile:
                outfile.write(full_text)

for folder in folders:
    convert_folder(folder)

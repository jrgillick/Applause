import os

transcripts_dir = '/data/corpora/cspan/transcripts/'
alignments_dir = '/data/corpora/cspan/alignments/'

exp = re.compile("[\[\(][a-zA-Z0-9_ \,\.]*[\]\)]")


folders = os.listdir(transcripts_dir)

def run_alignments_on_folder(folder):
    transcript_files = os.listdir(transcripts_dir + folder)
    for transcript_file in transcript_files:
        # Create folder to store the alignment files
        alignment_folder_name = alignments_dir + folder + '/' + transcript_file.replace('.txt','')
        alignment_file_name = alignment_folder_name + "/" + transcript_file.replace(".txt",".json")
        transcript_file_name = transcripts_dir+folder+"/" + transcript_file
        if not os.path.isdir(alignment_folder_name):
            os.system('mkdir ' + alignment_folder_name)
        run_alignment(alignment_file_name, transcript_file_name)

def run_alignment(alignment_file_name, transcript_file_name):
    audio_file_name = transcript_file_name.replace("/transcripts","/audio").replace('.txt','.mp3')
    if os.path.exists(audio_file_name) and os.path.exists(transcript_file_name):
        lines = open(transcript_file_name).read().split('\n')
        link = lines[0]
        speaker_list = lines[1]
        full_text = ""
        lines=lines[2:]
        for line in lines:
            if '\t' in line:
                timestamp,speaker,text = line.split('\t')
                full_text += text + '\n'
				full_text = re.sub(exp, '', full_text)
        alignment_cmd = "curl -X POST -F 'audio=@" + audio_file_name + "' -F 'transcript=@" + transcript_file_name.replace("transcripts/","transcripts_clean/") +"' 'http://localhost:32769/transcriptions?async=false' > " + alignment_file_name 
        print alignment_cmd
        os.system(alignment_cmd)

#for folder in folders:
#    run_alignments_on_folder(folder)

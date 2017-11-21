import os

transcripts_root = '/data/corpora/cspan/transcripts_clean/'
all_speeches = []
dirs = os.listdir(transcripts_root)
for d in dirs:
	all_speeches += [transcripts_root + d + '/' + f for f in os.listdir(transcripts_root + d)]

# Find duplicate speeches
non_keepers = []
duplicates_list = open('/data/corpora/cspan/duplicate_speeches.txt').read().split('\n')
for d in duplicates_list:
	non_keepers += d.split('\t')

# Find speeches with less than 2 minutes of applause or 25 instances
applause_times_root = '/data/corpora/cspan/applause_times/'
all_applause_files = []
dirs = os.listdir(applause_times_root)
for d in dirs:
	all_applause_files += [applause_times_root + d + '/' + f for f in os.listdir(applause_times_root + d)]

time_threshold = 2
count_threshold = 25

for f in all_applause_files:
	applause_mins = float(open(f).read().split('\n')[1].split(': ')[1].rstrip())
	applause_count = open(f).read().split('\n')[0].split(': ')[1].rstrip()
	if applause_mins < time_threshold or applause_count < count_threshold:
		non_keepers.append(f.replace('applause_times','transcripts_clean'))

non_keepers = list(set(non_keepers))
non_keepers.remove('')
keepers = [s for s in all_speeches if s not in non_keepers]

# Write keeper list to a file
with open('/data/corpora/cspan/keeper_speeches.txt','wb') as f:
	for s in keepers:
		f.write(s + '\n')
	
# Write non-keeper list to a file
with open('/data/corpora/cspan/non_keeper_speeches.txt','wb') as f:
	for s in non_keepers:
		f.write(s + '\n')

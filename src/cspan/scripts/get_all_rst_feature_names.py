import os
dir = '/data/dbamman/cspan/phrase_list_lower/'
files = [dir+f for f in os.listdir(dir) if f.endswith('rst_features')]

all_feature_names = []
for f in files:
	lines = open(f).read().split('\n')
	split_lines = [l.split(' ') for l in lines]
	feature_name_lists = [[l.split(':')[0] for l in line] for line in split_lines]
	for l in feature_name_lists:
		for feature in l:
			all_feature_names.append(feature)
	all_feature_names = list(set(all_feature_names))

all_feature_names.remove('')
all_feature_names.sort()

with open('/data/corpora/cspan/rst_feature_names.txt','wb') as f:
	for i in range(len(all_feature_names)-1):
		f.write(all_feature_names[i] + '\n')
	f.write(all_feature_names[-1])

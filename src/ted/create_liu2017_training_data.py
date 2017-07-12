from __future__ import unicode_literals
import glob, os, sys,re
import numpy as np
import spacy
from random import shuffle

reload(sys)
sys.setdefaultencoding('utf8')
nlp = spacy.load('en')

applause_yes=[]
applause_no=[]

def proc(filename):

	file=open(filename)
	alltext=""
	for line in file:
		cols=line.split("\t")
		timeparts=cols[0].split(":")
		text=cols[1]
		alltext+="#NEWLINE#" + unicode(text).encode("utf-8")
	
	file.close()
	i=0
	segments=alltext.split("(Applause)")
	
	for i in range(len(segments)-2):
		sentlist=[]

		segment=segments[i]
		pars=segment.split("#NEWLINE#")
		for par in pars:
			doc = nlp(par)
			for sentence in doc.sents:
				words=[]
				for word in sentence:
					if re.search("\S", word.string) != None:
						words.append(word.string)
				text=' '.join(words)
				if re.match("^\(.*?\)$", text) != None or re.search("\w", text) == None:
					continue
				sentlist.append(text)

		for j in range(len(sentlist)):
			if j==len(sentlist)-1:
				applause_yes.append(sentlist[j])
			else:
				applause_no.append(sentlist[j])

pathname=sys.argv[1]
os.chdir(pathname)

allobs=[]
for filename in glob.glob("*.html"):
    obs=proc(filename)

shuffle(applause_no)
for i in range(len(applause_yes)):
	print "%s\t%s" % ("1", re.sub("\s+", " ", applause_yes[i]))
	print "%s\t%s" % ("0", re.sub("\s+", " ", applause_no[i]))


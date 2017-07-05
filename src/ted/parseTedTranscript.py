#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Extract timestamps + text from TED transcripts 
# Input = html file of transcript

import sys,re,string,urllib,time,urllib2
from bs4 import BeautifulSoup
import os.path

reload(sys)
sys.setdefaultencoding('utf8')

def format(text):
	return re.sub("\s+", " ", text)

def proc(filename):
	file=open(filename)

	page=""
	for line in file.readlines():  
		page+=line.rstrip() + " "


	soup=BeautifulSoup(page, "lxml")
	sem=soup.findAll('div', {"class" :"Grid Grid--with-gutter p-b:4"})
	timestamps=[]
	texts=[]

	for s in sem:
		times=s.findAll('div', {"class" :" f:.9 c:gray m-t:.5 "})
		for t in times:
			timestamps.append(format(t.text.rstrip().lstrip()))
		text=s.findAll('div', {"class" :" Grid__cell w:5of6 w:7of8@xs w:9of10@sm w:11of12@md p-r:4 "})
		for te in text:
			texts.append(format(te.text.lstrip().rstrip()))

	for i in range(len(timestamps)):
		print "%s\t%s" % (timestamps[i], texts[i])


proc(sys.argv[1])

import sys,json,gzip,random,re,math
from collections import Counter
import numpy as np
from sklearn.cross_validation import KFold
from sklearn import linear_model
from scipy import sparse
from sklearn.preprocessing import normalize
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV

vocab={}
liwc={}
liwc_vocab={}
regex_liwc={}

# get all flat LIWC categories for a word
def getLIWC(word):
	vals=[]
	if word in liwc:
		vals.extend(liwc[word])
	if len(word) > 1:
		pref=word[0:2]
		if pref in regex_liwc:
			cands=regex_liwc[pref]
			for cand in cands:
				if re.match(cand, word) != None:
					vals.extend(regex_liwc[pref][cand])
	return vals

def readLIWC(filename):
	# Liu excludes "affective or emotional processes"
	invalid={}
	invalid["31"]=1
	invalid["32"]=1
	invalid["33"]=1
	invalid["34"]=1
	invalid["35"]=1
	
	file=open(filename)
	for i in range(75):
		line=file.readline()
		cols=re.split("\s+", line.rstrip())
		if line.rstrip() != "%":
			idd="%s" % cols[0]
			label=cols[1]
			liwc_vocab[idd]=label
	for line in file:
		cols=line.rstrip().split("\t")
		term=cols[0]
		valid=[]
		for x in cols[1:]:
			if x not in invalid:
				valid.append(x)
		cats=["LIWC_%s" % liwc_vocab[x] for x in valid]

		if term.endswith("*"):
			pref=term[0:2]
			if pref not in regex_liwc:
				regex_liwc[pref]={}
			regex_liwc[pref][term]=cats
		else:
			liwc[term]=cats

def read(filename):

	N=0
	fid=1

	for key in liwc_vocab:
		feat="LIWC_%s" % (liwc_vocab[key])
		vocab[feat]=fid
		fid+=1

	counts=Counter()
	file=open(filename)
	for line in file:
		cols=line.rstrip().split("\t")
		label=cols[0]
		text=cols[1].lower().split(" ")
		N+=1
		for word in text:
			counts[word.lower()]+=1
	file.close()
	for word in counts:
		count=counts[word]
		if count >= 500000:
			vocab[word.lower()]=fid
			fid+=1


	X = sparse.dok_matrix((N+1, fid+1))	
	Y = np.zeros(N+1)

	file=open(filename)
	docid=1
	for line in file:
		cols=line.rstrip().split("\t")
		label=int(cols[0])
		text=cols[1].lower().split(" ")

		for word in text:
			cats=getLIWC(word)
			for cat in cats:
				X[docid,vocab[cat]]=1
		for word in text:
			if word in vocab:
				X[docid,vocab[word]]=1
		Y[docid]=label
		docid+=1
	file.close()

	return X, Y

def predict(X, Y):
	X=sparse.csr_matrix(X)


	kf = KFold(len(Y), n_folds=10)

	bigcor=0.
	bigtot=0.

	for train_index, test_index in kf:
		correct=0.
		total=0.
		X_train, X_test = X[train_index], X[test_index]
		y_train, y_test = Y[train_index], Y[test_index]

		logreg=linear_model.LogisticRegression(penalty='l1')

		clf = GridSearchCV(logreg, {'C':(0.001, .01, .1, 1, 3, 5)}, cv=3)
		clf.fit(X_train, y_train)

		print clf.best_params_, len(y_train)
		y_true, y_pred = y_test, clf.predict(X_test)
		for i in range(len(y_true)):
			if y_true[i] == y_pred[i]:
				correct+=1
			total+=1
		bigcor+=correct
		bigtot+=total
	acc=bigcor/bigtot
	std=math.sqrt( (acc * (1-acc)) / bigtot )
	print "Accuracy: %.3f +/- %.3f (%s/%s)" % (acc, 1.96*std, bigcor, bigtot)

	# print feature weights
	logreg=linear_model.LogisticRegression(penalty='l1', C=0.1)
	logreg.fit(X, Y)


	maxFeat=len(vocab)

	reverseVocab=[None]*(maxFeat+1)
	for word in vocab:
		id=vocab[word]
		reverseVocab[id]=word

	zipped=zip(logreg.coef_[0], reverseVocab)			# zip two lists together to iterate through them simultaneously
	zipped.sort(key = lambda t: t[0], reverse=True)		# sort the two lists by the values in the first (the coefficients)
	print "%s\t%.3f\n" % ("INTERCEPT", logreg.intercept_)

	for (weight, word) in zipped[:10]:
		print "%s\t%.3f" % (word, weight)

	for (weight, word) in zipped[-10:]:
		print "%s\t%.3f" % (word, weight)






readLIWC(sys.argv[2])
X, Y=read(sys.argv[1])
predict(X, Y)
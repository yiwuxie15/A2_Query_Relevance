# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 17:12:20 2015

@author: Zidong Wang
@UniqueName: wzidong
"""
import re, string, os, sys, math
from PorterStemmer import PorterStemmer

def removeSGML(inStr):
#Function	that	removes	the	SGML	tags.
#Name:	removeSGML;	input: string;	output:	string   
    return re.sub('<.*?>', '', inStr) 
    
def tokenizeText(inStr):
##Function	that	tokenizes	the	text.	
##Name:	tokenizeText;	input:	string;	output:	list	(of	tokens)    
    words = inStr.replace('\n', ' ').split(" ")
    newwords = []
    for word in words:
        if word.endswith(',') or word.endswith('!') or word.endswith('?') or word.endswith(':') or word.endswith(';') or word.endswith(')'):
            word = word[:-1]
    
        puc = re.match("(\W+)", word)
        if puc or word == '':
            continue
        
        m = re.match("(I)('m)", word)
        d = re.match("(\w*)(n't)", word)
        l = re.match("(\w*)('s)", word) 
        r = re.match("(\w*)('re)", word)
        dig = re.match("(\d+)(\.)", word)
        num = re.search("(\,)(\d+)", word)    
        
        if m:
            newwords.append('I')
            newwords.append('am')
        elif d:
            if d.group(1)=='won':
                newwords.append('will')
            else:
                newwords.append(d.group(1))
            newwords.append('not')
        elif l:
            if l.group(1) == 'let':
                newwords.append('let')
                newwords.append('us')
            elif l.group(1) == 'it':
                newwords.append('it')
                newwords.append('is')
            else:
                newwords.append(l.group(1))
                newwords.append(l.group(2))
        elif r:
            newwords.append(r.group(1))
            newwords.append(r.group(2))
        elif dig:
            newwords.append(dig.group(1))
        elif num:
            if len(num.group(2)) != 3:
                for num in word.split(','):
                    newwords.append(num)
        else:
            newwords.append(word)
    
    return newwords
    
def removeStopwords(inList):    
#Function that removes the stopwords.	
#Name:	removeStopwords;input:list(of tokens);	output:	list(of tokens)
    newlist = []
    with open ("stopwords.txt", "r") as stopfile:
        stopdata=stopfile.read().replace('\n', ' ')
        stopwordlist = stopdata.split(' ')
        #print stopwords    
    exclude = set(string.punctuation)
    for word in inList:
        out = ''.join(ch for ch in word if ch not in exclude)
        if out.lower() in stopwordlist:
            continue
        elif out == "":
            continue
        else:
            newlist.append(out)
    
    stopfile.close()
    return newlist

    
def stemWords(inList):
##Function that stems the	words.
##Name: stemWords; input:	list (of tokens); output: list	(of stemmed tokens)
    outlist = []
    p = PorterStemmer()
    for word in inList:
        outlist.append(p.stem(word, 0, len(word)-1))
    return outlist  


def indexDocument(content, inv_index, weight_doc="tfidf", weight_que="tfidf"):
    #input:	 the	 content of	 the	 document (string); 
    #input: weighting	 scheme for	documents (string);	
    #input:	weighting scheme	for	query	(input); 
    #input/output: inverted	index	(your	choice of	data	structure)
    re_SML = removeSGML(content)
    token = tokenizeText(re_SML)
    wordlist = stemWords(removeStopwords(token))
    doc_num = wordlist[0] #record document name
    doc_dict = {} #count term frequency in the doc
    
    for word in wordlist:
        if word not in doc_dict:
            doc_dict[word] = 1
        else:
            doc_dict[word] += 1
                
    max_tf = max(doc_dict.values())*1.0
    
    if weight_doc == "tfidf" and weight_que == "tfidf":
        
        for key in doc_dict.keys():
            if key not in inv_index.keys():
                storelist = [doc_num, doc_dict[key]/max_tf]
                inv_index[key] = []
                inv_index[key].append(storelist)
            else:
                storelist = [doc_num, doc_dict[key]/max_tf]
                inv_index[key].append(storelist)
    
    elif weight_doc == "nxx-bpx" and weight_que == "nxx-bpx":
        
        for key in doc_dict.keys():
            if key not in inv_index.keys():
                storelist = [doc_num, 0.5+0.5*doc_dict[key]/max_tf]
                inv_index[key] = []
                inv_index[key].append(storelist)
            else:
                storelist = [doc_num, 0.5+0.5*doc_dict[key]/max_tf]
                inv_index[key].append(storelist)
            
    return inv_index
    
def convertInvToDic(inv_index, weight = "tfidf"):
    doc = {}
    if weight == "tfidf":
        for key in inv_index.keys():
            doc_list = inv_index[key]
            df = len(doc_list)
            for item in doc_list:
                if item[0] not in doc.keys():
                    doc[item[0]] = {}
                    doc[item[0]][key] = item[1]*(math.log10(1400.0/df))
                else:
                    doc[item[0]][key] = item[1]*(math.log10(1400.0/df))
    
    elif weight == "nxx-bpx":
        for key in inv_index.keys():
            doc_list = inv_index[key]
            for item in doc_list:
                if item[0] not in doc.keys():
                    doc[item[0]] = {}
                    doc[item[0]][key] = item[1]
                else:
                    doc[item[0]][key] = item[1]
        
    return doc
            

def retrieveDocuments(query, inv_index, weight_doc="tfidf", weight_que="tfidf"):
    # input:	 query	 (string);	 
    # input:	 inverted	 index	 (your	 choice of	 data	structure);	 
    # input:	 weighting	 scheme	 for	 documents	 (string);	 
    # input:	 weighting	 scheme	 for	 query	 (input);	
    #output:	list	of	ids	for	relevant	documents,	along	with	similarity	scores	(dictionary)
    re_SML = removeSGML(query)
    token = tokenizeText(re_SML)
    wordlist = stemWords(removeStopwords(token))
    global doc
    del wordlist[0]
    len_doc = {}
    rel_doc = {}
    que_vec = {}  #store weight vector of query
    que_dict = {} #store the term frequency in query
    
    for doct in doc.keys():
        x = sum([item**2 for item in doc[doct].values()])
        len_doc[doct] = math.sqrt(x)
    
    if weight_doc == "tfidf" and weight_que == "tfidf":
        for word in wordlist:
            if word not in que_dict:
                que_dict[word] = 1
            else:
                que_dict[word] += 1
        
        max_tf = max(que_dict.values())*1.0
        
        for word in wordlist:       
            if word not in inv_index.keys():
                que_vec[word] = 0
            else:
                df = len(inv_index[word])
                que_vec[word] = que_dict[word]/max_tf*math.log10(1400.0/df)
                for item in inv_index[word]:
                    if item[0] not in rel_doc.keys():
                        rel_doc[item[0]] = 0
    elif weight_doc == "nxx-bpx" and weight_que == "nxx-bpx":
        for word in wordlist:       
            if word not in inv_index.keys():
                que_vec[word] = 0
            else:
                df = len(inv_index[word])
                que_vec[word] = math.log10((1400.0-df)/df)
                for item in inv_index[word]:
                    if item[0] not in rel_doc.keys():
                        rel_doc[item[0]] = 0
            
    que_len = math.sqrt(sum([item**2 for item in que_vec.values()]))  
    
    for doct in rel_doc.keys():
        for word in wordlist:
            if word in doc[doct].keys():
                rel_doc[doct] += que_vec[word]*doc[doct][word]
        
        rel_doc[doct] = rel_doc[doct]/(que_len*len_doc[doct])
    
    sort_rel = sorted(rel_doc.items(), key=lambda x:x[1], reverse=True)
    return sort_rel

if len(sys.argv) == 5:
    docpath = '/' + str(sys.argv[3])
    quepath = '/' + str(sys.argv[4])
    wei_doc = str(sys.argv[1])
    wei_que = str(sys.argv[2])
    if wei_doc != wei_que:
        print "#weighting scheme error"
        exit
else:
    print "#Arguments Error"
    exit

path = os.getcwd()+docpath
inv_index = {}
for filename in os.listdir(path):
    if filename.startswith('.'):
        continue
    file_path = path+filename
    with open (file_path, "r") as intext:
        txt=intext.read()
        inv_index = indexDocument(txt, inv_index, wei_doc, wei_que)

doc = convertInvToDic(inv_index, wei_doc)
query_path = os.getcwd()+quepath


#result_list = []
with open(query_path, 'r') as query_txt:
    txt_ptr = query_txt.readline()
    query_num = 1
    while txt_ptr:
        rel_doct = retrieveDocuments(txt_ptr, inv_index, wei_doc, wei_que)       
        for item in rel_doct:
            result = str(query_num) + ' ' + item[0] + ' ' + str(item[1])
            print result
            #result_list.append(result)
        txt_ptr = query_txt.readline()
        query_num += 1

#judge_path = os.getcwd()+'/relevance_judgements.txt'
#judge_list = []
#with open(judge_path, 'r') as judge_txt:
#    judge_ptr = judge_txt.readline()
#    while judge_ptr:
#        judge_list.append(judge_ptr.replace('\n', ''))
#        judge_ptr = judge_txt.readline()
#com = len(set(result_list) & set(judge_list))*1.0     
#prce = com / len(result_list)
#recall = com / len(judge_list)
#print prce, recall
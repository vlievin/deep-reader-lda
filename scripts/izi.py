# imports
from __future__ import division
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import logging, gensim, bz2
from gensim import corpora, models, similarities
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from bs4 import BeautifulSoup
import nltk
import re
from nltk.corpus import stopwords
import string
import itertools
import random
import numpy as np
from lightning import Lightning
from numpy import random, asarray
import networkx as nx
import math
import random
import pickle
from nltk.stem.wordnet import WordNetLemmatizer
import os
import sys
import PIL
from PIL import Image
from os import path
from wordcloud import WordCloud
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from scipy.sparse import *
from scipy import *
import community
from textstat.textstat import textstat
import json


DOSSIER_UPS = 'ups/'
ROOT = 'scripts/'

colours_ordered = []
colours_ordered.append( "#2ecc71")
colours_ordered.append( "#3498db")
colours_ordered.append( "#f1c40f")
# colours.append( "#2ecc71")
colours_ordered.append( "#e67e22")
colours_ordered.append( "#e74c3c")

colours = []
colours.append( "#7f8c8d")
colours.append( "#e74c3c")
colours.append( "#3498db")
colours.append( "#f1c40f")
colours.append( "#9b59b6")
colours.append( "#1abc9c")
colours.append( "#34495e")
colours.append( "#e67e22")


# constants
min_score = 0.03

# load lda
lda = gensim.models.ldamodel.LdaModel.load( ROOT +  u'lda/wikipedia_lda', mmap='r')
N_TOPICS = 100

# freq_english = pickle.load( open(ROOT +  "english_frequencies.p", "rb" ) )
import nltk
from nltk.corpus import reuters
freq_english = nltk.FreqDist(reuters.words())
print "--------------------> english word frequencies loaded"


# load text xliff or txt format
def loadText(path):   
    if path[-4:] == 'liff':
        soup = BeautifulSoup( open(path), 'lxml')
        s = ' '
        for string in soup.find_all("source"):
            s += ' ' + string.string
        return s
    elif path[-3:] == 'txt':
        return open(path, 'r').read()
    else:
    	print "EXTENSION ERROR: " + path


# def getChunks(text):
# 	0


# raw tokenize
def raw_tokenize(text):
	text = text
	text = text.lower()
    # tokenize + punctuation
	from nltk.tokenize import RegexpTokenizer
	tokenizer = RegexpTokenizer(r'\w+') # remove punctuation
	return tokenizer.tokenize(text)


# tokenize
def tokenize(text):
    text = raw_tokenize(text)
    # remove stopwords
    from nltk.corpus import stopwords
    stops = stopwords.words('english')
    text = [ w.replace (" ", "_") for w in text if w.lower() not in stops]
    # Exclude numbers
    text = [s for s in text if not re.search(r'\d',s)]
    #remove word with less than 3letters
    text = [s for s in text if len(s) > 2]
    # stemmer
    lmtzr = WordNetLemmatizer()
    text =  [(lmtzr.lemmatize(t)) for t in text] 
    return text

# count words
def count_words(text):
    text = text.lower()
    # tokenize + punctuation
    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'\w+') # remove punctuation
    text = tokenizer.tokenize(text)
    
    return len(text)


def calculateSentiment( tokens ):
	file = open(ROOT + 'Data_Set_S1.txt', 'r')
	sentiments_dataset = file.readlines()
	word_sentiment = dict()
	for l in sentiments_dataset:
		if len(l) and l[0] != '!':
			ll = l.split('\t')
			word_sentiment[ll[0]] = float(ll[2])
	s = 0.0
	keys = set(word_sentiment.keys())
	total = 0
	for t in tokens:
	    if t in keys:
	        s += word_sentiment[t]
	        total +=1
	if s:
	    return float(s)/float(total)
	else:
	    return 0.0

# get filelist
def getFileList(root):
	filelist = []
	for filename in os.listdir(root):
		filename = root + filename
		filelist.append(filename.encode(sys.getfilesystemencoding()))

	return filelist


# get topics froms tokens
def topicsFromTokens( tokens ):
    bow = lda.id2word.doc2bow( tokens )
    return lda.get_document_topics(bow)


# print word cloud
def WordCloudTopic( items , imagePath = None):
    # Generate a word cloud image
    plt.axis("off")
    if imagePath:
    	alice_coloring = np.array(Image.open(imagePath))

    	wc = WordCloud(background_color="white", max_words=200, mask=alice_coloring,
                   stopwords=STOPWORDS.add("said"),
                   max_font_size=300)
    	# generate word cloud
    	wc.generate_from_frequencies(items)
    	image_colors = ImageColorGenerator(alice_coloring)
    	plt.imshow(wc.recolor(color_func=image_colors))
    else:
    	wc = WordCloud(background_color="white", max_words=300,
        max_font_size=40, random_state=42)
    	wordcloud = wc.generate_from_frequencies(items)    
    	plt.imshow(wordcloud)
	plt.savefig( DOSSIER_UPS + 'cloud.png' )
    

## similarity
# get topic from a single word
def getTopicFromWord( unique_word ):
    bow = lda.id2word.doc2bow( [unique_word] )
    topic = lda.get_document_topics(bow)
    if len(topic):
        return topic[0][0]
    else:
        return None

def norm(v):
    s = 0
    for d in v.itervalues():
        s+= d**2
    return sqrt(s)

def similarity( a, b):
    # cosine similarity
    p = (a.dot(b.transpose()) / (norm(a) * norm(b))).data
    if len(p):
        return p[0]

def listToDOK(vec):
	v = dok_matrix((1,N_TOPICS), dtype=float32)
	for i in range(0, len(vec)):
		v[0,i] = vec[i]
	return v

def getSimilaritiesScores( vec ,semantic_vectors ):
    u = dok_matrix((1,N_TOPICS), dtype=float32)
    i = 0
    for i in range(0,N_TOPICS):
        u[0,i ]= vec[i]
    similarities = []
    for s in semantic_vectors:
        vec = semantic_vectors[s]
        v = listToDOK(vec)
        score = dict()
        score['name'] = s
        score['similarity'] = similarity(v,u)  
        similarities.append(score)
        
    return similarities


def getSimilarity( a ,b ):
    return similarity(listToDOK(a),listToDOK(b))  


def complexityAlongtheText( text, n_chunk = 10 ):
	words = text.split()
	chunk_length = len(words) / n_chunk
	if chunk_length < 200:
		chunk_length = 200

	chunk_length = int(chunk_length)

	x = []
	y = []
	cur = 0
	# average = textstat.flesch_reading_ease(text)

	while ( cur < len(words) ):
	    sub = words[cur:cur+chunk_length]
	    sub.append('.')
	    sub_text = ' '.join(sub)
	    try:
		    diff = 100 - textstat.flesch_reading_ease(sub_text)
		    if diff < 100:
		    	y.append( 100 - textstat.flesch_reading_ease(sub_text)  )
		    	x.append( cur)
	    except:
    		print "cannot compute complexity in 'complexityAlongtheText' "
	    cur += chunk_length
	   
	average = float(sum(y))/float(len(y))
	print "average reading ease: %s "%average

	if average < 20:
	    col = colours_ordered[0]
	elif average < 40:
	    col = colours_ordered[1]
	elif average < 60:
	    col = colours_ordered[2]
	elif average < 80:
	    col = colours_ordered[3]
	else:
	    col = colours_ordered[4]

	full_data = dict()
	data = []
	for i in range(0,len(y)):
		tmp = dict()
		tmp['x'] = x[i]
		tmp['y'] = y[i]
		# tmp['color'] = col
		data.append(tmp)

	full_data['values'] = data
	full_data['color'] = col
	#     plt.plot( [0,max(x)], [average,average], color = 'gray')
	
	return full_data


def getComplexityData(path):
	return complexityAlongtheText( path)

def getMostSignificativeWords_pseudo_idf( path ):
	idf = pickle.load( open(ROOT +  "english_idf.p", "rb" ) )
	min_idf = min(idf.values())
	text = loadText(path)
	tokens = tokenize(text)
	f = nltk.FreqDist(tokens)
	max_f = float( tokens.count(f.max()))
	word_set = set(tokens)
	result = dict()
	for w in word_set:
		if w in idf.keys():
			idf_word = idf[w]
		else:
			idf_word = min_idf * 0.5
		score = float(len(w)) * float(f[w]) / max_f * float(idf_word)  
		result[w] = score
	return result

def getMostSignificativeWords( tokens, limit = False, defaultLimit = 300 ):
	# f = nltk.FreqDist(tokens)
	word_set = set(tokens)
	result = dict()
	for w in word_set:
	# 	if w in freq_english.keys():
	# 		f_w = freq_english[w]
	# 	else:
	# 		f_w = 0
		score = len(w)  / np.log(2 + freq_english[w] )
		result[w] = score
		# print w,

	if limit:
		result_keys = sorted(result, key=lambda tup: tup[1], reverse = True)[:defaultLimit]
		return { r: result[r] for r in result_keys}

	else:
		return result


def getMostSignificantWordsData( tokens, topics ):
	topic_names = pickle.load( open(ROOT +  "topics_names.p", "rb" ) )
	x_topics = []
	for i in range(0, len(topics)):
		x_topics.append( ( i, topics[i] ))
	significant = getMostSignificativeWords(tokens)
	significants_words_per_topic = dict()

	k = 1
	for i in sorted(x_topics, key=lambda tup: tup[1], reverse = True):
		if i[1] > min_score:
		    significants_words_per_topic[topic_names[i[0]]] = dict()
		    significants_words_per_topic[topic_names[i[0]]]['size'] = i[1]
		    significants_words_per_topic[topic_names[i[0]]]['values'] = dict()
		    significants_words_per_topic[topic_names[i[0]]]['color'] = colours[k]
		    max_significant = max(significant.values())
		    k += 1
		    if k >= len(colours):
		    	k = 0


	others = dict()
	for w in significant:
	    t = getTopicFromWord(w)
	    if t != None:
	    	t = topic_names[t]
	    if t in significants_words_per_topic.keys():
	        y = dict()
	        significants_words_per_topic[t]['values'][w] = significant[w]
	    else:
	        others[w] = significant[w]
	# significants_words_per_topic['others']['values'] = others


	data = []
	for topic_name in significants_words_per_topic:
		topic = significants_words_per_topic[topic_name]
		color = topic['color']
		words = topic['values']
		for w in words:
			word = dict()
			word['text'] = w
			word['color'] = color
			word['size'] = words[w]
			data.append(word)

	return data


def SignificantWordsGraph( tokens, topics ):
	gen = idGenerator()
	topic_names = pickle.load( open(ROOT +  "topics_names.p", "rb" ) )
	x_topics = []
	for i in range(0, len(topics)):
		x_topics.append( ( i, topics[i] ))
	significant = getMostSignificativeWords(tokens)
	significants_words_per_topic = dict()
	max_significant = max(significant.values())

	k = 1
	total_size = 0.0
	for i in sorted(x_topics, key=lambda tup: tup[1], reverse = True):
		if i[1] > min_score:
		    significants_words_per_topic[topic_names[i[0]]] = dict()
		    significants_words_per_topic[topic_names[i[0]]]['size'] = i[1]
		    total_size += i[1]
		    significants_words_per_topic[topic_names[i[0]]]['values'] = dict()
		    significants_words_per_topic[topic_names[i[0]]]['color'] = colours[k]

		    k += 1
		    if k >= len(colours):
		    	k = 0

	significants_words_per_topic['others'] = dict()
	significants_words_per_topic['others']['size'] = 1 - total_size
	significants_words_per_topic['others']['values'] = dict()
	significants_words_per_topic['others']['color'] = "#cccccc"

	for w in significant:
	    t = getTopicFromWord(w)
	    if t != None:
	    	t = topic_names[t]
	    if t in significants_words_per_topic.keys():
	        y = dict()
	        significants_words_per_topic[t]['values'][w] = significant[w]
	    else:
			significants_words_per_topic['others']['values'][w] = significant[w]

	nodes = []
	edges = []

	id0 = gen.get()
	main = dict()
	main['id'] = id0
	main['name'] = "text"
	main['color'] = "#555555"
	main['size'] = 30
	nodes.append(main)

	added_words = set()

	for topic_name in significants_words_per_topic:
		topic = significants_words_per_topic[topic_name]
		color = topic['color']
		words = topic['values']

		id_topic = gen.get()
		topic_node = dict()
		topic_node['id'] = id_topic
		topic_node['name'] = topic_name
		topic_node['color'] = color
		topic_node['size'] = 60 * topic['size']
		nodes.append(topic_node)
		edges.append( {'source': id0 , 'target': id_topic, 'value': topic_node['size']})

		for ww in sorted(words, key=lambda x: x[1], reverse = True):
			if ww not in added_words:
				id_word = gen.get()
				word = dict()
				word['id'] = id_word
				word['name'] = ww
				word['color'] = color
				word['size'] = words[ww]
				nodes.append(word)
				edges.append( {'source': id_topic , 'target': id_word, 'value': word['size']})
				added_words.add(w)

	graph = dict()
	graph['nodes'] = nodes
	graph['links'] = edges

	return graph


def getTopTopics( vec ):
	topic_names = pickle.load( open(ROOT +  "topics_names.p", "rb" ) )
	pairs = []
	result = []
	for i in range(0, len(vec)):
	    pairs.append( (i , vec[i] ) )
	k = 1
	s = 0.0
	for i in sorted(pairs, key=lambda tup: tup[1], reverse = True):
	    if i[1] > min_score and k < len(colours):
	    	tmp = dict()
	    	tmp[ 'value' ] = i[1] 
	    	s += i[1]
	    	tmp['name'] = topic_names[i[0]]
	    	tmp['color'] = colours[k]
	    	result.append( tmp )
	    	k += 1
	    	# if k >= len(colours):
	    	# 	k = 0

	others = dict()
	others[ 'value' ] = 1.0 - s
	others['name'] = 'others'
	others['color'] = 'lightgray'
	result.append(others)

	return result




def getTopicsDistributionWithinTheText(text, semantic_vec, n_chunk = 30 ):
	global_scores = []
	for i in range(0, len(semantic_vec)):
		global_scores.append( ( i, semantic_vec[i] ))
	words = text.split()
	chunk_length = len(words) / n_chunk
	if chunk_length < 200:
		chunk_length = 200

	chunk_length = int(chunk_length)

	scores = dict()
	for i in sorted(global_scores, key=lambda tup: tup[1], reverse = True):
	    if i[1] > min_score:
	        scores[i[0]] = []
	x = []
	y = []
	cur = 0
	i = 1
	while ( cur < len(words) ):
	    sub = words[cur:cur+chunk_length]
	    sub.append('.')
	    sub_text = ' '.join(sub)
	    cur += chunk_length
	    
	    bow = lda.id2word.doc2bow(raw_tokenize(sub_text))
	    score = lda.get_document_topics(bow)
	    for s in score:
	        if s[0] in scores.keys():
	            scores[s[0]].append(s[1])
	            
	    for s in scores:
	        if len(scores[s]) < i:
	            scores[s].append(0)
	    i += 1
	    
    
	return scores, global_scores, chunk_length


def getTopicDistributionData( txt, n_chunk = 20):

	colours_copy = colours[:]
	# random.shuffle(colours_copy)
	topic_names = pickle.load( open(ROOT +  "topics_names.p", "rb" ) )
	distribAlongText, global_scores, chunk_length = getTopicsDistributionWithinTheText(txt, n_chunk)

	global_scores =  sorted(global_scores, key=lambda tup: tup[1], reverse = True)
	scores = []
	for g in global_scores:
	    if g[0] in distribAlongText.keys():
	        scores.append( distribAlongText[g[0]])

	values = []
	labels = []
	somme= 0.
	for s in global_scores:
	    if s[1] > min_score:
	        values.append(s[1])
	        somme+= s[1]**2
	        labels.append(topic_names[s[0]])

	values = [ float(v)/float(somme) for v in values]

	data = []

	patches = []    
	x = range( 0, len(scores[0]))
	x = [ chunk_length * i for i in x]
	i = 0
	k = 1
	for s in scores:
		topic = dict()
		topic['color'] = colours_copy[k]
		topic['values'] = []

		for j in range(0, len(s)):
			pt = dict()
			pt['x'] = x[j]
			pt['y'] = s[j]
			topic['values'].append(pt)
			topic['label'] = labels[i]
		# patches.append(mpatches.Patch(color=c, label=labels[i]))
		data.append(topic)
		k += 1
		i +=1
		if k >= len(colours_copy):
		    k = 0

	return data




def displayTopicsDistributionWithinTheText(f, chunk_length = 300, dispLabels = True,pie = False):
	topic_names = pickle.load( open(ROOT +  "topics_names.p", "rb" ) )
	distribAlongText, global_scores = getTopicsDistributionWithinTheText(f, chunk_length)

	global_scores =  sorted(global_scores, key=lambda tup: tup[1], reverse = True)
	scores = []
	for g in global_scores:
	    if g[0] in distribAlongText.keys():
	        scores.append( distribAlongText[g[0]])

	values = []
	labels = []
	somme= 0.
	for s in global_scores:
	    if s[1] > min_score:
	        values.append(s[1])
	        somme+= s[1]**2
	        labels.append(topic_names[s[0]])

	values = [ float(v)/float(somme) for v in values]

	if pie:
	    # draw pie chart
	    plt.pie(values,  labels=labels, colors = [ [1.0 / 255.0 * c for c in cc] for cc in colours[1:]])
	    plt.savefig( DOSSIER_UPS + 'topics_pie.png' )


	patches = []    
	x = range( 0, len(scores[0]))
	x = [ chunk_length * i for i in x]
	i = 0
	k = 1
	for s in scores:
		c = [ 1.0 / 255.0 * c for c in colours[k] ]
		plt.plot(x, s,linewidth = 5, color = c, alpha = 0.6)
		plt.fill_between(x, s,linewidth = 5, color = c, alpha = 0.3)
		patches.append(mpatches.Patch(color=c, label=labels[i]))
		k += 1
		i +=1
		if k >= len(colours):
		    k = 0
	        
	fig = plt.figure()
	if dispLabels:
	    plt.legend(handles=patches)
	    plt.ylabel('proportion')
	    plt.xlabel('number of words')
	else:
	    plt.axis('off')

	plt.savefig( DOSSIER_UPS + 'topics_distribution.png' )
	plt.close(fig)






class idGenerator:
    def __init__(self):
        self.id = 0
    def get(self):
        self.id += 1
        return self.id - 1


# convert raw semantic vector to sprse DOK vector
def semantic_vec_to_dok( semantic_vec , n_topics = N_TOPICS):
    u = dok_matrix((1,n_topics), dtype=float32)
    for t in semantic_vec:
        u[0,t[0]] = t[1]
    return u

# draw graph 
def getGraph(semantics_vectors, color, similarity_cutoff = 0.85):
	filelist = semantics_vectors.keys()
	id_gen  = idGenerator()
	graph = nx.Graph()
	filename2id = dict()
	base_weight = 5.0

    # construct nodes
	for f in filelist:
	    i = id_gen.get()
	    filename2id[f] = i
	    filename2id[i] = f
	    graph.add_node( i , weight = base_weight, label = f.decode('unicode_escape').encode('ascii','ignore'), color = color)

	# construct edges
	for f in filelist:  
	    i = filename2id[f]
	    u = semantic_vec_to_dok( semantics_vectors[f])
	    for ff in filelist:
	        if ff != f:
	            ii = filename2id[ff]
	            v = semantic_vec_to_dok(semantics_vectors[ff])
	            sim = similarity(u,v)
	            if sim > similarity_cutoff:
	                distance = 1 - sim
	                if distance < 0:
	                	distance = 0
	                graph.add_edge(i, ii, weight = distance)
	                
	return graph, filename2id



def plotGraphNX( G ):
	groups = []
	i = 0
	tresh = 0.1
	while i <1:
	    groups.append((i , [(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <i and d['weight'] >= i - tresh ]))
	    i += tresh
	pos=nx.spring_layout(G) # positions for all nodes
	# nodes
	nx.draw_networkx_nodes(G,pos,node_size=400, node_color = 'orange', alpha = 0.6)
	# edges
	for g in groups:
	    nx.draw_networkx_edges(G,pos,edgelist=g[1],
	                    width=1, alpha = g[0])
	# nx.draw_networkx_edges(G,pos,edgelist=esmall,width=6,alpha=0.5,edge_color='b',style='dashed')
	# labels
	# nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
	plt.axis('off')
	plt.savefig( DOSSIER_UPS + 'nx_graph.png' )
	return pos

def computeModularity ( graph_undirect, sub_graphs):
	M = 0
	L = len( graph_undirect.edges() )
	for c in sub_graphs:
	    kc = 0
	    for n in c:
	        kc+= c.degree(n)
	    Lc = len( c.edges() )
	    M += ( float( Lc / float(L) - pow( float(kc) / ( 2.0 * float(L) ) ,2) ))
	return M


def LouvainModularity( G, colours, node_size = 80):

	graphs = list(nx.connected_component_subgraphs(G))
	graphs.sort(key=lambda x: len( x.nodes() ), reverse = True)
	G = graphs[0]

	#first compute the best partition
	partition = community.best_partition(G)

	#drawing
	size = float(len(set(partition.values())))
	pos = nx.spring_layout(G)
	count = 0.
	nx.draw_networkx_edges(G,pos,  edge_color = "#aaaaaa", alpha = 0.8)
	sub_graphs_louvain = []

	k = 0
	for com in set(partition.values()) :
	    count = count + 1.
	    list_nodes = [nodes for nodes in partition.keys()
	                                if partition[nodes] == com]

	    nx.draw_networkx_nodes(G, pos, list_nodes, linewidths = 0,  node_size = node_size,
	                                node_color = colours[k])
	    #place partition in subgraphs
	    sub_graphs_louvain.append( G.subgraph(list_nodes ) )
	    k += 1
	    if k >= len(colours):
	        k = 0


	plt.axis("off")
	plt.savefig('grap_communties_louvain.png')
	plt.show()

	print "modularity: %s" %computeModularity ( G, sub_graphs_louvain)
	print "%s communities" %len(sub_graphs_louvain)
	return sub_graphs_louvain


def displayResults( path ):
	print "stats"
	text = loadText(path)
	raw_tokens = raw_tokenize(text)
	print "number of words %s" %count_words(text)
	print "number of sentences %s" %textstat.sentence_count(text)
	print "uniques words: %s" %len(set(raw_tokenize(text)))
	print "Difficulty %s / 100 " %(100 - textstat.flesch_reading_ease(text))
	print "Average sentiment %s (negative: 0, neutral: 5, positive: 10)"%calculateSentiment(raw_tokens)
	print
	print "topic distribution"
	# displayTopicsDistributionWithinTheText(path, 300, pie = True)
	print "difficulty over the text "
	data =  complexityAlongtheText( path, 300)
	return data
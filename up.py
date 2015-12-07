#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, request, flash, redirect, url_for, render_template, jsonify
from flask import send_file
from werkzeug import secure_filename
import os
import json
import pickle

# Use a database already created on mongolab 
server = 'ds059694.mongolab.com'
port = 59694
db_name = 'deepreader'
username = 'deepreaderuser'
password = '1ecolequimonte45'

from pymongo import MongoClient as Connection

# from pymongo import Connection

# what versions are we using
import sys
print 'Python version', sys.version

import pymongo
print 'Pymongo version', pymongo.version
##

# connect to server
print '\nConnecting ...'
conn = Connection(server, port)

# Get the database
print '\nGetting database ...'
db = conn[db_name]

# Have to authenticate to get access
print '\nAuthenticating ...'
db.authenticate(username, password)


min_score = 0.04

colours = []
colours.append( "#7f8c8d")
colours.append( "#e74c3c")
colours.append( "#3498db")
colours.append( "#f1c40f")
colours.append( "#9b59b6")
colours.append( "#1abc9c")
colours.append( "#34495e")
colours.append( "#e67e22")


class idGenerator:
	def __init__(self):
		self.id = 0
	def get(self):
		self.id += 1
		return self.id - 1

def getTopTopics( vec ):
	topic_names = pickle.load( open( 'scripts/' +  "topics_names.p", "rb" ) )
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
			#   k = 0

	others = dict()
	others[ 'value' ] = 1.0 - s
	others['name'] = 'others'
	others['color'] = 'lightgray'
	result.append(others)

	return result



# from scripts import izi


app = Flask(__name__)
app.secret_key = 'd66HR8dç"f_-àgjYYic*dh'

print"#### DATABASE ####"
print db.dataset
print"#### COLLECTIONS ####"
names = db.collection_names(include_system_collections=False)
for n in names:
	print " --   " + str(n)
print "###############################   READY   ###############################"

app.debug = True

n_topics = 100



def getLastAdded():
	current_id = None
	for d in db.documents.find().sort("_id", -1).limit(1) :
		current_id = d
	return db.documents.find_one( { "_id" : current_id["_id"] })
	# return db.documents.find_one()


@app.route('/d3/')
def d3():
    txt =  getLastAdded()
    if txt:
        data = dict()
        return render_template('analysis.html', file_title = txt['title'] )
    else:
        return "failed to get text"

@app.route('/')
@app.route('/presentation/')
def intro():
    return render_template('presentation.html' )


@app.route("/complexity/<title>", methods=['GET', 'POST'])
def complexity(title):
	if title == '':
		doc = getLastAdded()
	else:
		doc = db.documents.find_one( { "title" : title })
	return json.dumps(doc['complexity'])
	# return json.dumps(izi.getComplexityData(lasDoc['full_text']))

@app.route("/topics/<title>", methods=['GET', 'POST'])
def topics(title):
	if title == '':
		doc = getLastAdded()
	else:
		doc = db.documents.find_one( { "title" : title })
	return json.dumps(doc['full_topics'])
	# return json.dumps(izi.getTopicDistributionData( lasDoc['full_text'], lasDoc['semantic_vec']))

@app.route("/significantWords/<title>", methods=['GET', 'POST'])
def significantWords(title):
	if title == '':
		doc = getLastAdded()
	else:
		doc = db.documents.find_one( { "title" : title })
	return json.dumps( doc['significantWords'])
	# return json.dumps(izi.getMostSignificantWordsData(lasDoc['tokens'] , lasDoc['semantic_vec']))

@app.route("/topicsGraph/<title>", methods=['GET', 'POST'])
def topicsGraph(title):
	if title == '':
		doc = getLastAdded()
	else:
		doc = db.documents.find_one( { "title" : title })
	return json.dumps(doc['topicsGraph'])
	# return json.dumps(izi.SignificantWordsGraph(lasDoc['tokens'] , lasDoc['semantic_vec'] ))

@app.route('/translator/<name>')
def getTranslator(name):
	nameT =  db.translators.find_one({'name' : name})
	if nameT:
		data = dict()
		data['topics'] = nameT['topics']
		return json.dumps(data)
	else:
		return "failed to get topicsT"


@app.route('/translator/')
def translator():
	return render_template('translators.html')



@app.route('/getText/<title>')
def getText(title):
	txt =  db.documents.find_one({'title' : title})
	if txt:
		data = dict()
		data['text'] = '<a href="/analysis/'+ title + '" class="btn btn-red">analyse it! </a>' + '<br><br>'  + txt['full_text']
		return json.dumps(data)
	else:
		return "failed to get text"

@app.route('/getTopics/<title>')
def getTopics(title):
	txt =  db.documents.find_one({'title' : title})
	if txt:
		data = dict()
		vec = txt['semantic_vec']
		topics = getTopTopics(vec)
		data['topics'] = topics
		return json.dumps(data)
	else:
		return "failed to get text"

@app.route('/analysis/<title>')
def analysis(title):
	txt =  db.documents.find_one({'title' : title})
	if txt:
		data = dict()
		return render_template('analysis.html', file_title = title )
	else:
		return "failed to get text"



@app.route("/network", methods=['GET', 'POST'])
def network():
	graph = db.graph.find_one()
	data = dict()
	data['nodes'] = graph['nodes']
	data['links'] = graph['links']
	return json.dumps(data)

def processFile( path ):
	return izi.displayResults( path )


def extension_ok(nomfic):
	""" Renvoie True si le fichier possède une extension d'image valide. """
	return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('txt', 'mxliff')

def is_image(nomfic):
	""" Renvoie True si le fichier possède une extension d'image valide. """
	return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('jpg', 'png')


# @app.route('/', methods=['GET', 'POST'])
# @app.route('/up/', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         # if request.form['pw'] == 'up': # on vérifie que le mot de passe est bon
#         f = request.files['fic']
#         if f: # on vérifie qu'un fichier a bien été envoyé
#             if extension_ok(f.filename): # on vérifie que son extension est valide
#                 nom = secure_filename(f.filename)
#                 # remove previous files
#                 images = [img for img in os.listdir(DOSSIER_UPS)]
#                 for i in images:
#                     os.remove(DOSSIER_UPS + i)
#                 txts = [t for t in os.listdir(TEXT_FOLDERS)]
#                 for i in txts:
#                     os.remove(TEXT_FOLDERS + i)
#                 f.save(TEXT_FOLDERS + nom)
#                 insertDoc(TEXT_FOLDERS + nom)
#                 # processFile( TEXT_FOLDERS + nom )
#                 flash(u'File sent. Here is the <a href="{lien}"> link </a>.'.format(lien=url_for('d3')), 'succes')
#             else:
#                 flash(u'Ce fichier ne porte pas une extension autorisée !', 'error')
#         else:
#             flash(u'Vous avez oublié le fichier !', 'error')
#         # else:
#         #     flash(u'Mot de passe incorrect', 'error')
#     return render_template('up_up.html')



@app.route('/corpusnet/')
def corpusnet():
	return render_template('corpusnet.html')

if __name__ == '__main__':
	app.run(host = '0.0.0.0')

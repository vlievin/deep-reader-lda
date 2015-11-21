#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, request, flash, redirect, url_for, render_template, jsonify
from flask import send_file
from werkzeug import secure_filename
import os
from PIL import Image
from StringIO import StringIO
import shutil
import json
from flask.ext.pymongo import PyMongo

from pymongo import MongoClient

client = MongoClient()
db = client.izidb


from scripts import izi


app = Flask(__name__)
app.secret_key = 'd66HR8dç"f_-àgjYYic*dh'


mongo = PyMongo(app)

print"#### DATABASE ####"
print db.dataset
print"#### COLLECTIONS ####"
names = db.collection_names(include_system_collections=False)
for n in names:
    print " --   " + str(n)
print "###############################   READY   ###############################"

app.debug = True

DOSSIER_UPS = 'ups/'
TEXT_FOLDERS = 'texts/'
DATA_FOLDERS = 'data/'
n_topics = 100

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy

data_complexity = []
current_id = None
root = u"../izi_data/"


def getLastAdded():
	current_id = None
	for d in db.documents.find(fields = {"_id"}).sort("_id", -1).limit(1):
		current_id = d
	return db.documents.find_one( { "_id" : current_id["_id"] })

@app.route("/complexity", methods=['GET', 'POST'])
def complexity():
    lasDoc = getLastAdded()
    return json.dumps(izi.getComplexityData(lasDoc['full_text']))

@app.route("/topics", methods=['GET', 'POST'])
def topics():
    lasDoc = getLastAdded()
    return json.dumps(izi.getTopicDistributionData( lasDoc['full_text'], lasDoc['semantic_vec']))

@app.route("/significantWords", methods=['GET', 'POST'])
def significantWords():
    lasDoc = getLastAdded()
    return json.dumps(izi.getMostSignificantWordsData(lasDoc['tokens'] , lasDoc['semantic_vec']))

@app.route("/topicsGraph", methods=['GET', 'POST'])
def topicsGraph():
    lasDoc = getLastAdded()
    return json.dumps(izi.SignificantWordsGraph(lasDoc['tokens'] , lasDoc['semantic_vec'] ))

@app.route("/similarities", methods=['GET', 'POST'])
def similarities():
	lasDoc = getLastAdded()
	semantic_vectors = dict()
	cursor = db.documents.find()
	for doc in cursor:
		semantic_vectors[doc['title']] = doc['semantic_vec']
	# return json.dumps( result )
	return json.dumps(izi.getSimilaritiesScores(lasDoc['semantic_vec'], semantic_vectors))

def processFile( path ):
    return izi.displayResults( path )


def extension_ok(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('txt', 'mxliff')

def is_image(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('jpg', 'png')


@app.route('/', methods=['GET', 'POST'])
@app.route('/up/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # if request.form['pw'] == 'up': # on vérifie que le mot de passe est bon
        f = request.files['fic']
        if f: # on vérifie qu'un fichier a bien été envoyé
            if extension_ok(f.filename): # on vérifie que son extension est valide
                nom = secure_filename(f.filename)
                # remove previous files
                images = [img for img in os.listdir(DOSSIER_UPS)]
                for i in images:
                    os.remove(DOSSIER_UPS + i)
                txts = [t for t in os.listdir(TEXT_FOLDERS)]
                for i in txts:
                    os.remove(TEXT_FOLDERS + i)
                f.save(TEXT_FOLDERS + nom)
                insertDoc(TEXT_FOLDERS + nom)
                # processFile( TEXT_FOLDERS + nom )
                flash(u'File sent. Here is the <a href="{lien}"> link </a>.'.format(lien=url_for('d3')), 'succes')
            else:
                flash(u'Ce fichier ne porte pas une extension autorisée !', 'error')
        else:
            flash(u'Vous avez oublié le fichier !', 'error')
        # else:
        #     flash(u'Mot de passe incorrect', 'error')
    return render_template('up_up.html')

@app.route('/up/view/', methods=['GET', 'POST'])
def liste_upped():
    images = [img for img in os.listdir(DOSSIER_UPS) if is_image(img)] # la liste des images dans le dossier
    if request.method == 'POST':
        if request.form['submit']:
            print "maybe here ?"
        if request.form['submit'] == 'Delete All Files':
            print "YOLO it works"
    return render_template('up_liste.html', images=images)


@app.route('/d3/')
def d3():
    d = [d for d in os.listdir(DATA_FOLDERS) ]
    return render_template('d3.html')


@app.route('/up/view/<nom>')
def upped(nom):
    nom = secure_filename(nom)
    if os.path.isfile(DOSSIER_UPS + nom): # si le fichier existe
        return send_file(DOSSIER_UPS + nom, as_attachment=True) # on l'envoie
    else:
        flash(u'Fichier {nom} inexistant.'.format(nom=nom), 'error')
        return redirect(url_for('liste_upped')) # sinon on redirige vers la liste des images, avec un message d'erreur

def insertDoc(path):
    document = dict()
    document['title'] = path[len(TEXT_FOLDERS):]
    full_text = izi.loadText(path)
    tokens = izi.tokenize( full_text)
    document['full_text'] = full_text
    document['tokens'] = tokens
    topics =  izi.topicsFromTokens(izi.tokenize(full_text))
    semantic_vec = [0.] * n_topics
    for i in topics:
        semantic_vec[i[0]] = i[1]
    document['semantic_vec'] = semantic_vec
    current_id = db.documents.save(document)
    print " ---- current id ---- "
    print current_id
    print


if __name__ == '__main__':
    app.run(host = '0.0.0.0')

#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, request, flash, redirect, url_for, render_template, jsonify
from flask import send_file
from werkzeug import secure_filename
import os
import json
import pickle

from pymongo import MongoClient

client = MongoClient()
db = client.izidb

min_score = 0.04

from scripts import izi
reload(izi)

n_topics = 100


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


TEXT_FOLDERS = 'tmp/'



def getLastAdded():
    current_id = None
    for d in db.documents.find().sort("_id", -1).limit(1) :
        current_id = d
    return db.documents.find_one( { "_id" : current_id["_id"] })
    # return db.documents.find_one()

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
        data['text'] = txt['title'] + '  <br> <br>' + '<a href="/analysis/'+ title + '" class="btn btn-red">analyse it! </a>' + '<br><br>'  + txt['full_text']
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

@app.route('/d3/')
def d3():
    txt =  getLastAdded()
    if txt:
        data = dict()
        return render_template('analysis.html', file_title = txt['title'] )
    else:
        return "failed to get text"


@app.route('/closest_translator/')
def closest():
    txt =  getLastAdded()
    if txt:
        cursor = db.similarities.find()
        documents = []
        m = 0
        translators = []
        for e in cursor:
            key_doc = None
            if e['target'] == txt['_id']:
                key_doc = e['source'] 
            if e['source'] == txt['_id']:
                key_doc = e['target'] 

            if key_doc:
                tmp_doc = db.documents.find_one( {'_id': key_doc } )
                dat = dict()
                dat['translator'] = tmp_doc['translator']
                dat['similarity'] = e['value']
                translators.append( dat )

        return json.dumps( sorted( translators, key = lambda x: x['similarity'], reverse = True )[:10])
    else:
        return "failed to get text"


@app.route("/network", methods=['GET', 'POST'])
def network():
    SIMILARITY_CUTOFF = 0.85

    lasDoc = getLastAdded()
    semantic_vectors = dict()
    list_ids = db.documents.find().distinct("_id")
    current_id = lasDoc["_id"]

    id2db = dict()
    gen = idGenerator()

    nodes = []
    for ii in list_ids:
        doc = db.documents.find_one( {'_id' : ii} )
        node = dict()
        tmp_id = doc["_id"]
        i = gen.get()
        id2db[str(tmp_id)] = i
        node["id"] = i
        if tmp_id == current_id:
            node['color'] = "#3498db"
        else:
            node['color'] = "#555555"
        node['size'] = 5
        node['id_db'] = str(tmp_id)
        node['name'] = doc['title']
        nodes.append(node)

    cursor = db.similarities.find()
    edges = []
    for e in cursor:
        if e['value'] > SIMILARITY_CUTOFF:
            a = e['source']
            b = e['target']
            edge = {'source': id2db[str(a)] , 'target': id2db[str(b)], 'value': e['value']}
            edges.append(edge)


    graph = dict()
    graph['nodes'] = nodes
    graph['links'] = edges
    return json.dumps(graph)

def processFile( path ):
    return izi.displayResults( path )


def extension_ok(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('txt', 'mxliff')

def is_image(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('jpg', 'png')


@app.route('/', methods=['GET', 'POST'])
@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # if request.form['pw'] == 'up': # on vérifie que le mot de passe est bon
        f = request.files['fic']
        if f: # on vérifie qu'un fichier a bien été envoyé
            if extension_ok(f.filename): # on vérifie que son extension est valide
                nom = secure_filename(f.filename)
                # remove previous files
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



@app.route('/corpusnet/')
def corpusnet():
    return render_template('corpusnet.html')

def safe_str(value):
    if type(value) == str:
    # Ignore errors even if the string is not proper UTF-8 or has
    # broken marker bytes.
    # Python built-in function unicode() can do this.
        value = unicode(value, "utf-8", errors="ignore")
    else:
    # Assume the value object has proper __unicode__() method
        value = unicode(value)
    return value

from bs4 import BeautifulSoup
def loadTranslator(path):   
    if path[-4:] == 'liff':
        soup = BeautifulSoup( open(path), 'lxml')
        for string in soup.find_all("file"):
            try:
                return string['m:task-id']
            except:
                return -1

def insertDoc(path):
    document = dict()
    document['title'] = path[len(TEXT_FOLDERS):]
    document['translator'] = loadTranslator(path)
    current_translator = db.translators.find_one({'name': document['translator']})
        
        
    try:
        full_text = izi.loadText(path)
    #     full_text = unicode(full_text, errors='ignore')
        full_text = safe_str(full_text)

        if len(full_text) > 500:
            if not current_translator:
                translator = dict()
                translator['name'] = document['translator']
                translator['document'] = []
                id_current_translator = db.translators.save(translator)
                current_translator = db.translators.find_one({'name': document['translator']})

            # text and tokens
            tokens = izi.tokenize( full_text)
            document['full_text'] = full_text
            document['tokens'] = tokens
            # topics
            topics =  izi.topicsFromTokens(izi.tokenize(full_text))
            semantic_vec = [0.] * n_topics
            for i in topics:
                semantic_vec[i[0]] = i[1]
            document['semantic_vec'] = semantic_vec
            # complexity
            document['complexity'] = izi.complexityAlongtheText(full_text)
            # topic distribution
            document['full_topics'] = izi.getTopicDistributionData( document['full_text'], document['semantic_vec'])
            # significants words
            document['significantWords'] = izi.getMostSignificantWordsData(document['tokens'] , document['semantic_vec'])
            # significant words graph
            document['topicsGraph'] = izi.SignificantWordsGraph(document['tokens'] , document['semantic_vec'] )

            ##
            # savec doc
            current_id = db.documents.save(document)
            current_translator['document'].append(current_id)
            db.translators.update({'name': document['translator']}, {'name': document['translator'],\
                                                                     'document': current_translator['document']})


            ###################
            # create links
            cursor = db.documents.find()
            for doc in cursor:
                y = doc['semantic_vec']
                y_id = doc["_id"]
                if y_id != current_id:
                    s = izi.getSimilarity( semantic_vec, y)
                    db.similarities.insert({'source': current_id , 'target': y_id, 'value': s})
    except:
        print "############################################################"
        print "#### ERROR: " + document['title']




if __name__ == '__main__':
    app.run(host = '0.0.0.0')

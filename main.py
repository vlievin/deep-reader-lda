#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request, make_response, abort, redirect,render_template
from PIL import Image
from StringIO import StringIO
app = Flask(__name__)
app.debug = True

from datetime import datetime

@app.route('/date')
def date():
    d = datetime.today().isoformat()
    return render_template('accueil.html', la_date=d)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return "Vous avez envoyé : {msg}".format(msg=request.form['msg'])
    return '<form action="" method="post"><input type="text" name="msg" /><input type="submit" value="Envoyer" /></form>'


@app.route('/discussion/page/<int:num_page>')
def mon_chat(num_page):
    premier_msg = 1 + 50 * (num_page - 1)
    dernier_msg = premier_msg + 50
    return 'affichage des messages {} à {}'.format(premier_msg, dernier_msg)



@app.route('/image')
def genere_image():
    mon_image = StringIO()
    Image.new("RGB", (300,300), "#92C41D").save(mon_image, 'BMP')
    print type(mon_image)
    reponse = make_response(mon_image.getvalue())
    reponse.mimetype = "image/bmp"  # à la place de "text/html"
    return reponse


@app.route('/profil')
def profil():
    if utilisateur_non_identifie:
        abort(401)
    return "Vous êtes bien identifié, voici la page demandée : ..."


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def ma_page_erreur(error):
    return "Ma jolie page {}".format(error.code), error.code


@app.route('/google')
def redirection_google():
    return redirect('http://www.google.fr')





if __name__ == '__main__':
    app.run(host = '0.0.0.0')

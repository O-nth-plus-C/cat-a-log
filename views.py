from flask import Flask, render_template, url_for, request, redirect, flash
from flask import session as login_session

import random, string

from models import Base, Category, Item, User

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy import create_engine

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']
APPLICATION_NAME = "Cat-a-log"
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

#Home Page, shows all categories, and newest items
@app.route('/')
@app.route('/catalog')
def show_catalog():
    catalog = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('public_catalog.html', catalog=catalog)
    else:
        return render_template('catalog.html', catalog=catalog)

#New Category page
@app.route('/catalog/add_category', methods=['GET','POST'])
def add_category():
    if 'username' not in login_session:
        return redirect ('/catalog/sign_in')
    if request.method == 'POST':
        newCategory = Category(category_name = request.form['name'], category_image = request.form['image'], user_id = login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('add_category.html')

#Delete Category Page
@app.route('/catalog/<int:category_id>/delete', methods = ['GET','POST'])
def delete_category(category_id):
    if 'username' not in login_session:
        return redirect ('/catalog/sign_in')
    category_to_delete = session.query(Category).filter_by(id = category_id).one()
    if category_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not the owner of this category. Please use the back button.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(category_to_delete)
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('delete_category.html', category=category_to_delete)

#Edit Category Page
@app.route('/catalog/<int:category_id>/edit', methods = ['GET','POST'])
def edit_category(category_id):
    if 'username' not in login_session:
        return redirect ('/catalog/sign_in')
    category_to_edit = session.query(Category).filter_by(id = category_id).one()
    if category_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not the owner of this category. Please use the back button.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            category_to_edit.category_name = request.form['name']
        if request.form['image']:
            category_to_edit.category_image = request.form['image']
        session.add(category_to_edit)
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('edit_category.html', category = category_to_edit)

#Category Page, shows all items in category
@app.route('/catalog/<int:category_id>')
def show_category(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    if 'username' not in login_session:
        return render_template('public_category.html', category=category, items = items)
    else:
        return render_template('category.html', category=category, items = items)

#Item page
@app.route('/catalog/<int:category_id>/<int:item_id>')
def show_item(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', item = item)

#Page to Add New item
@app.route('/catalog/<int:category_id>/add_item', methods=['GET','POST'])
def add_item(category_id):
    if 'username' not in login_session:
        return redirect('catalog/sign_in')
    if request.method == 'POST':
        newItem = Item(
        item_name = request.form['name'],
        item_description = request.form['description'],
        item_price = request.form['price'],
        item_image = request.form['image'],
        category_id = category_id,
        user_id=login_session['user_id']
        )
        session.add(newItem)
        session.commit()
        return redirect(url_for('show_category', category_id=category_id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('add_item.html', category=category)

#Page to Edit item
@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods = ['GET','POST'])
def edit_item(category_id, item_id):
    editedItem = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.item_name = request.form['name']
        if request.form['description']:
            editedItem.item_description = request.form['description']
        if request.form['image']:
            editedItem.item_image = request.form['image']
        if request.form['price']:
            editedItem.item_image = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('show_item', category_id = category_id, item_id = item_id))
    else:
        return render_template('edit_item.html', item = editedItem)

#Page to Delete Item
@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods = ['GET','POST'])
def delete_item(category_id, item_id):
    deletedItem = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        return redirect(url_for('show_category', category_id = category_id))
    else:
        return render_template('delete_item.html', item = deletedItem)

#
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        #Upgrade the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the auth code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #check that token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If error in token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    #verify token is used for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn match given id"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #verify token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app"), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    #check to see if user is logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Store the token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id']= gplus_id

    #Get User info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if not make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

#Disconnect - revoke a user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    #Only disconnect a connected userself.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        #Reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        #For whatever reason, given token was invalid.
        response = make_response(json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = applicaiton/json
        return response

#Login page
@app.route('/catalog/sign_in')
def sign_in():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('sign_in.html', STATE=state)

#Logout page
@app.route('/catalog/sign_out')
def sign_out():
    return 'This will be the page to logout.'

#Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

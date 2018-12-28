from flask import Flask, render_template, url_for, request, redirect

from models import Base, Category, Item

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

#Home Page, shows all categories, and newest items
@app.route('/')
@app.route('/catalog')
def show_catalog():
    #return 'This will show the main catalog page, with categories, and newest.'
    catalog = session.query(Category).all()
    return render_template('catalog.html', catalog=catalog)

#Category Page, shows all items in category
@app.route('/catalog/<string:category>')
def show_category(category):
    return 'This will show the page for a category: %s.' % category

#New Category page
@app.route('/catalog/add_category', methods=['GET','POST'])
def add_category():
    if request.method == 'POST':
        newCategory = Category(category_name = request.form['name'], category_image = request.form['image'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('add_category.html')

#Item page
@app.route('/catalog/<string:category>/<string:item>')
def show_item(category, item):
    return 'This will be the item page for: %s %s.' % (category, item)

#Page to Add New item
@app.route('/catalog/add_item')
def add_item():
    return 'This will be the page to add a new item.'

#Page to Edit item
@app.route('/catalog/<string:category>/<string:item>/edit')
def edit_item(category, item):
    return 'This will be the page to edit item: %s %s.' % (category, item)

#Page to Delete Item
@app.route('/catalog/<string:category>/<string:item>/delete')
def delete_item(category, item):
    return 'This will be the page to delete item: %s %s.' % (category, item)

#Create New User
@app.route('/catalog/add_user')
def add_user():
    return 'This will be a page to add a new user.'

#Login page
@app.route('/catalog/sign_in')
def sign_in():
    return 'This will be the page to login.'

#Logout page
@app.route('/catalog/sign_out')
def sign_out():
    return 'This will be the page to logout.'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

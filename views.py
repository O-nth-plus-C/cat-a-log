from flask import Flask, render_template, url_for, request, redirect

from models import Base, Category, Item

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy import create_engine

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
    return render_template('catalog.html', catalog=catalog)

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

#Delete Category Page
@app.route('/catalog/<int:category_id>/delete', methods = ['GET','POST'])
def delete_category(category_id):
    category_to_delete = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(category_to_delete)
        session.commit()
        return redirect(url_for('show_catalog'))
    else:
        return render_template('delete_category.html', category=category_to_delete)

#Edit Category Page
@app.route('/catalog/<int:category_id>/edit', methods = ['GET','POST'])
def edit_category(category_id):
    category_to_edit = session.query(Category).filter_by(id = category_id).one()
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
    return render_template('category.html', category=category, items = items)

#Item page
@app.route('/catalog/<int:category_id>/<int:item_id>')
def show_item(category_id, item_id):
    return 'This will be the item page for: %s %s.' % (category_id, item_id)

#Page to Add New item
@app.route('/catalog/<int:category_id>/add_item', methods=['GET','POST'])
def add_item(category_id):
    if request.method == 'POST':
        newItem = Item(
        item_name = request.form['name'],
        item_description = request.form['description'],
        item_price = request.form['price'],
        item_image = request.form['image'],
        category_id = category_id
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
    editedItem = session.query(Item).filter_by(item_id = item_id)
    if request.method = 'POST':
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
        return redirect(url_for('show_category', category_id = category_id))
    else:
        return render_template('edit_item.html', item = editedItem)

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

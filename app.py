from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
# Connect to MongoDB
uri = "mongodb+srv://jinyoonok:jinyoon981023@cmpsc487-jinyoon.vuymlgv.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['CMPSC487-Project2']
collection = db['itemsCollection']

@app.route('/')
def index():
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'name')

    if sort_by not in ['_id', 'name']:
        sort_by = 'name'  # Default sorting parameter

    if query:
        # Using a regex to perform a case-insensitive search
        items = collection.find({"name": {"$regex": query, "$options": "i"}}).sort(sort_by)
    else:
        items = collection.find().sort(sort_by)

    return render_template('index.html', items=items)


@app.route('/browse')
def browse():
    items = collection.find()
    return render_template('browse.html', items=items)


@app.route('/edit/<item_id>', methods=['GET'])
def edit_item(item_id):
    # Retrieve the item from the database using the provided item_id
    item = collection.find_one({'_id': ObjectId(item_id)})
    return render_template('item_edit.html', item=item)


@app.route('/create', methods=['GET'])
def create_item():
    # Render the form without pre-filled data
    return render_template('item_edit.html', item=None)


@app.route('/save', methods=['POST'])
def save_item():
    item_id = request.form.get('item_id')
    name = request.form.get('name')
    description = request.form.get('description')

    if item_id:  # Update existing item
        collection.update_one({'_id': ObjectId(item_id)}, {"$set": {"name": name, "description": description}})
    else:  # Create new item
        collection.insert_one({"name": name, "description": description, "image": "your_image_path"})

    return redirect(url_for('index'))  # Redirect back to the index page after saving

@app.route('/delete/<item_id>')
def delete_item(item_id):
    # Delete the specified item from the database
    collection.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('index'))  # Redirect back to the index page

if __name__ == '__main__':
    app.run(debug=True)

# Main objective: get familiar with developing web-based applications and CRUD operations.
# Suppose you have a list of items. The items here could be the products of an online store, or the
# employees that work for an organization. Each item should have at least 4 attributes: ID, name,
# description, and image.
# Implement the following operations:
# • Browse the list of items.
# • Sort the list by item ID, or by item name.
# • Search an item by a keyword or by ID.
# • Add a new item to the list (assuming the ID is auto generated).
# • Select an item to edit (assuming you can edit any attribute except for the ID).
# • Remove an item.
# All operations are web-based.
# You are free to select the programming language and the database management system.
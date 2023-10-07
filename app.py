from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import os
from os import path
from werkzeug.utils import secure_filename

# Connect to MongoDB
uri = "mongodb+srv://jinyoonok:jinyoon981023@cmpsc487-jinyoon.vuymlgv.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['CMPSC487-Project2']
collection = db['itemsCollection']

app = Flask(__name__)
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    query = request.args.get('query', '')
    sort_by = request.args.get('sort_by', 'name')

    if sort_by not in ['_id', 'name']:
        sort_by = 'name'  # Default sorting parameter

    if query:
        # using a regex to perform a case-insensitive search
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/save', methods=['POST'])
def save_item():
    item_id = request.form.get('item_id')
    name = request.form.get('name')
    description = request.form.get('description')

    # Initial dictionary for the new item
    new_item = {"name": name, "description": description, "image": "your_image_path"}

    # Image Upload From Here
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':  # check file was selected
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Check if file already exists and delete it if does
                if path.exists(file_path):
                    os.remove(file_path)

                file.save(file_path)
                print(f"Image saved at: {file_path}")
                # Update the file_path for database insertion
                db_file_path = 'images/' + filename  # Updated to use forward slash
                print(f"Path for DB: {db_file_path}")
                new_item['image'] = db_file_path  # Update image path in new_item dictionary

    # If item_id exists, update the existing item; otherwise, insert a new item
    if item_id:
        collection.update_one({'_id': ObjectId(item_id)}, {"$set": new_item})
    else:
        collection.insert_one(new_item)

    return redirect(url_for('index'))  # Redirect back to the index page after saving


@app.route('/delete/<item_id>')
def delete_item(item_id):
    # Retrieve the item from the database using the provided item_id
    item = collection.find_one({'_id': ObjectId(item_id)})

    # Check if the item exists and it has an image field
    if item and 'image' in item:
        image_path = item['image']
        absolute_image_path = os.path.join(os.getcwd(), 'static', image_path)

        # count the number of items that reference the same image
        image_count = collection.count_documents({'image': image_path})

        # if that count is only 1, we delete image, otherwise keep
        if image_count <= 1:
            # Check if the file exists before trying to delete it
            if os.path.exists(absolute_image_path):
                os.remove(absolute_image_path)
                print(f"Image {absolute_image_path} deleted.")
            else:
                print(f"Image {absolute_image_path} not found.")

    # Delete the specified item from the database
    collection.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('index'))  # Redirect back to the index page

if __name__ == '__main__':
    app.run(debug=True)
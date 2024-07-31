from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key

# MongoDB connection setup
client = MongoClient('mongodb+srv://tiak:mongodb.ak17@portfolio-dataset.ha4l0ka.mongodb.net/')

db_users = client['users']
users_collection = db_users['users']

# Route to render the main page
@app.route('/')
def login():
    return render_template('login.html')

# Route for main page to get database and collection names
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        db_name = request.form.get('db_name')
        collection_name = request.form.get('collection_name')
        session['db_name'] = db_name
        session['collection_name'] = collection_name
        return redirect(url_for('list_documents', db_name=db_name))
    return render_template('dashboard.html')

# Route for displaying documents based on selected DB and Collection
@app.route('/<db_name>')
def list_documents(db_name):
    collection_name = session.get('collection_name')

    if collection_name and 'username' in session:
        db = client[db_name]
        collection = db[collection_name]
        dataset = collection.find()
        return render_template('index.html', dataset=dataset, db_name=db_name)
    else:
        return redirect(url_for('dashboard'))

# Route for creating a new document (blog, project, certificate)
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST' and 'username' in session:
        db_name = session.get('db_name')
        collection_name = session.get('collection_name')

        if db_name and collection_name:
            db = client[db_name]
            collection = db[collection_name]

            if collection_name == 'blogs':
                data = {
                    'title': request.form.get('title').replace('\r', ''),
                    'author': request.form.get('author').replace('\r', ''),
                    'imageurl': request.form.get('imageurl').replace('\r', ''),
                    'description': request.form.get('description').replace('\r', ''),
                    'content': request.form.get('content').replace('\r', ''),
                    'date': request.form.get('date').replace('\r', ''),
                    'dateString': request.form.get('dateString').replace('\r', ''),
                    'category': request.form.get('category').replace('\r', ''),
                    'pinned': request.form.get('pinned') == 'true'
                }
            elif collection_name == 'projects':
                data = {
                    'imageUrl': request.form.get('imageUrl').replace('\r', ''),
                    'title': request.form.get('title').replace('\r', ''),
                    'date': request.form.get('date').replace('\r', ''),
                    'description': request.form.get('description').replace('\r', ''),
                    'link': request.form.get('link').replace('\r', ''),
                    'dateString': request.form.get('dateString').replace('\r', '')
                }
            elif collection_name == 'certificates':
                data = {
                    'date': request.form.get('date').replace('\r', ''),
                    'description': request.form.get('description').replace('\r', ''),
                    'imageUrl': request.form.get('imageUrl').replace('\r', ''),
                    'title': request.form.get('title').replace('\r', '')
                }

            collection.insert_one(data)
            return redirect(url_for('list_documents', db_name=db_name))
    return render_template('create.html')

# Route for editing a document (blog, project, certificate)
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' in session:
        db_name = session.get('db_name')
        collection_name = session.get('collection_name')
        if db_name and collection_name:
            db = client[db_name]
            collection = db[collection_name]
        else:
            return redirect(url_for('dashboard'))

        try:
            doc_id = ObjectId(id)
            document = collection.find_one({'_id': doc_id})
            if not document:
                document = collection.find_one({'_id': id})
        except Exception as e:
            print(f"Error fetching document: {e}")
            return redirect(url_for('list_documents', db_name=db_name))

        if request.method == 'POST':
            if collection_name == 'blogs':
                updated_data = {
                    'title': request.form.get('title').replace('\r', ''),
                    'author': request.form.get('author').replace('\r', ''),
                    'imageurl': request.form.get('imageurl').replace('\r', ''),
                    'description': request.form.get('description').replace('\r', ''),
                    'content': request.form.get('content').replace('\r', ''),
                    'date': request.form.get('date').replace('\r', ''),
                    'dateString': request.form.get('dateString').replace('\r', ''),
                    'category': request.form.get('category').replace('\r', ''),
                    'pinned': request.form.get('pinned') == 'true'
                }
            elif collection_name == 'projects':
                updated_data = {
                    'imageUrl': request.form.get('imageUrl').replace('\r', ''),
                    'title': request.form.get('title').replace('\r', ''),
                    'date': request.form.get('date').replace('\r', ''),
                    'description': request.form.get('description').replace('\r', ''),
                    'link': request.form.get('link').replace('\r', ''),
                    'dateString': request.form.get('dateString').replace('\r', '')
                }
            elif collection_name == 'certificates':
                updated_data = {
                    'date': request.form.get('date').replace('\r', ''),
                    'description': request.form.get('description').replace('\r', ''),
                    'imageUrl': request.form.get('imageUrl').replace('\r', ''),
                    'title': request.form.get('title').replace('\r', '')
                }

            collection.update_one({'_id': doc_id}, {'$set': updated_data})
            return redirect(url_for('list_documents', db_name=db_name))

        return render_template('edit.html', document=document, db_name=db_name)
    else:
        return render_template('login.html')

# Route for deleting a document (blog, project, certificate)
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    db_name = session.get('db_name')
    collection_name = session.get('collection_name')
    if db_name and collection_name:
        db = client[db_name]
        collection = db[collection_name]
        collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_documents', db_name=db_name))

# Route to verify login credentials
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return jsonify({'success': True, "message": "success"})
    else:
        return jsonify({'success': False, 'message': 'Unable to Log you in.'})

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

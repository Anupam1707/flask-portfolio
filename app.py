from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key

# MongoDB connection setup
client = MongoClient('mongodb+srv://tiak:mongodb.ak17@portfolio-dataset.ha4l0ka.mongodb.net/')
# db_blogs = client['blogs']
# blogs_collection = db_blogs['blogs']

# db_projects = client['projects']
# projects_collection = db_projects['test']

# db_certificates = client['certificates']
# certificates_collection = db_certificates['certificates']

db_users = client['users']
users_collection = db_users['users']


# Route to render the main page
@app.route('/')
def login():
    return render_template('login.html')

# Route for main page to get database and collection names
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST' and 'username' in session:
        db_name = request.form.get('db_name')
        collection_name = request.form.get('collection_name')
        session['db_name'] = db_name
        session['collection_name'] = collection_name
        return redirect(url_for('list_blogs'))
    return render_template('dashboard.html')

# Route for displaying blogs based on selected DB and Collection
@app.route('/documents')
def list_blogs():
    db_name = session.get('db_name')
    collection_name = session.get('collection_name')

    if db_name and collection_name and 'username' in session:
        db = client[db_name]
        collection = db[collection_name]
        dataset = collection.find()
        return render_template('index.html', dataset=dataset)
    else:
        return redirect(url_for('dashboard'))

# Route for creating a new blog post
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST' and 'username' in session :
        date_str = request.form.get('date')
        date_string = request.form.get('dateString')

        data = {
            'title': request.form.get('title').replace('\r', ''),
            'author': request.form.get('author').replace('\r', ''),
            'imageurl': request.form.get('imageurl').replace('\r', ''),
            'description': request.form.get('description').replace('\r', ''),
            'content': request.form.get('content').replace('\r', ''),
            'date': date_str.replace('\r', ''),
            'dateString': date_string.replace('\r', ''),
            'category': request.form.get('category').replace('\r', ''),
            'pinned': request.form.get('pinned') == 'true'
        }
        blogs_collection.insert_one(data)
        return redirect(url_for('list_blogs'))
    return render_template('create.html')

# Route for editing a blog post
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
            blog_id = ObjectId(id)
            blog = collection.find_one({'_id': blog_id})
        except Exception as e:
            print(f"Error fetching blog: {e}")
            return redirect(url_for('list_blogs'))

        if request.method == 'POST':
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
            collection.update_one({'_id': blog_id}, {'$set': updated_data})
            return redirect(url_for('list_blogs'))

        return render_template('edit.html', blog=blog)
    else:
        return render_template('login.html')

# Route for deleting a blog post
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    blogs_collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_blogs'))

# Route to verify login credentials
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password) and 'username' not in session:
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

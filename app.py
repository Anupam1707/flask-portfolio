from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://tiak:mongodb.ak17@portfolio-dataset.ha4l0ka.mongodb.net/blogs"
mongo_blog = PyMongo(app, uri="mongodb+srv://tiak:mongodb.ak17@portfolio-dataset.ha4l0ka.mongodb.net/blogs")
mongo_users = PyMongo(app, uri="mongodb+srv://<username>:<password>@<your-cluster>.mongodb.net/users")
##db = mongo.db.blogs

@app.route('/')
def index():
    db = mongo_blogs.db.blogs
    blogs = db.find()
    return render_template('index.html', blogs=blogs)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        date_str = request.form.get('date')
        date_string = request.form.get('dateString')
        
        # Use date_str for actual date storage, and date_string for readable format
        data = {
            'title': request.form.get('title').replace('\r', ''),
            'author': request.form.get('author').replace('\r', ''),
            'imageurl': request.form.get('imageurl').replace('\r', ''),
            'description': request.form.get('description').replace('\r', ''),
            'content': request.form.get('content').replace('\r', ''),
            'date': date_str.replace('\r', ''),
            'dateString': date_string.replace('\r', ''),  # Add this line
            'category': request.form.get('category').replace('\r', ''),
            'pinned': request.form.get('pinned') == 'true'  # Convert to boolean
        }
        db.insert_one(data)
        return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    try:
        blog_id = ObjectId(id)
        blog = db.find_one({'_id': blog_id})
    except Exception as e:
        print(f"Error fetching blog: {e}")
        return redirect(url_for('index'))

    if request.method == 'POST':
        updated_data = {
            'title': request.form.get('title').replace('\r', ''),
            'author': request.form.get('author').replace('\r', ''),
            'imageurl': request.form.get('imageurl').replace('\r', ''),
            'description': request.form.get('description').replace('\r', ''),
            'content': request.form.get('content').replace('\r', ''),
            'date': request.form.get('date').replace('\r', ''),
            'dateString': request.form.get('dateString').replace('\r', ''),  # Add this line
            'category': request.form.get('category').replace('\r', ''),
            'pinned': request.form.get('pinned') == 'true'  # Convert to boolean
        }
        db.update_one({'_id': blog_id}, {'$set': updated_data})
        return redirect(url_for('index'))

    return render_template('edit.html', blog=blog)

@app.route('/delete/<id>')
def delete(id):
    db.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

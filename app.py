from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://tiak:mongodb.ak17@portfolio-dataset.ha4l0ka.mongodb.net/blogs"
mongo = PyMongo(app)

@app.route('/')
def index():
    collections = mongo.db.list_collection_names()
    return render_template('index.html', collections=collections)

@app.route('/collection/<name>')
def collection(name):
    documents = mongo.db[name].find()
    return render_template('collection.html', name=name, documents=documents)

@app.route('/add/<name>', methods=['POST'])
def add_document(name):
    data = request.form.to_dict()
    mongo.db[name].insert_one(data)
    return redirect(url_for('collection', name=name))

@app.route('/delete/<name>/<id>')
def delete_document(name, id):
    mongo.db[name].delete_one({'_id': ObjectId(id)})
    return redirect(url_for('collection', name=name))

if __name__ == '__main__':
    app.run(debug=True)

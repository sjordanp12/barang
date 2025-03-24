from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
from bson.objectid import ObjectId

app = Flask(__name__)

# Access the MONGO_URI from environment variables
mongo_uri = os.getenv('MONGO_URI')

# Setup MongoDB connection
client = MongoClient(mongo_uri)

db = client.mydatabase  

# Route untuk menampilkan daftar barang

@app.route('/')
def index():
    items = list(db.items.find()) 
    return render_template('index.html', items=items)

# Route untuk menambahkan barang
@app.route('/add', methods=['POST'])
def add_item():
    nama_barang = request.form.get('nama_barang')
    harga_barang = request.form.get('harga_barang')

    if  nama_barang and harga_barang:
        db.items.insert_one({
            'nama_barang': nama_barang,
            'harga_barang': harga_barang
        })
    return redirect(url_for('index'))

# Route untuk menghapus barang
@app.route('/delete/<item_id>')
def delete_item(item_id):
    db.items.delete_one({'_id': ObjectId(item_id)})
    return redirect(url_for('index'))

# Route untuk mengedit barang
@app.route('/edit/<item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'POST':
        nama_barang = request.form.get('nama_barang')
        harga_barang = request.form.get('harga_barang')

        db.items.update_one(
            {'_id': ObjectId(item_id)}, 
            {'$set': {
                'nama_barang': nama_barang,
                'harga_barang': harga_barang
            }}
        )
        return redirect(url_for('index'))

    item = db.items.find_one({'_id': ObjectId(item_id)})
    return render_template('edit.html', item=item)

# Route untuk mencari barang berdasarkan kode barang
@app.route('/search', methods=['GET'])
def search_item():
    nama_barang = request.args.get('nama_barang')  # Mendapatkan input nama barang dari URL query string
    if nama_barang:
        # Mencari barang berdasarkan nama barang di MongoDB dengan case-insensitive
        item = db.items.find_one({'nama_barang': {'$regex': f'^{nama_barang}$', '$options': 'i'}})
        if item:
            # Jika barang ditemukan, render template hasil pencarian
            return render_template('search_result.html', item=item)
        else:
            # Jika barang tidak ditemukan, berikan pesan
            return render_template('search_result.html', message='Barang tidak ditemukan.')
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

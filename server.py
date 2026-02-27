from flask import Flask, jsonify, send_from_directory
import sqlite3
import json

app = Flask(__name__, static_folder='.')

def get_db():
    conn = sqlite3.connect('blue_plaques.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/favicon.svg')
def favicon():
    return send_from_directory('.', 'favicon.svg')

@app.route('/api/plaques')
def get_plaques():
    conn = get_db()
    plaques = conn.execute('''
        SELECT p.id, p.title, p.geo_location, p.address, p.categories, 
               p.description, p.local_image_path, p.url
        FROM plaques p
        WHERE p.geo_location IS NOT NULL
    ''').fetchall()
    
    result = []
    for plaque in plaques:
        geo = json.loads(plaque['geo_location']) if plaque['geo_location'] else None
        if geo and geo.get('lat') and geo.get('lon'):
            images = conn.execute('''
                SELECT local_image_path, image_url, image_title, image_order
                FROM plaque_images
                WHERE plaque_id = ?
                ORDER BY image_order
            ''', (plaque['id'],)).fetchall()
            
            result.append({
                'id': plaque['id'],
                'title': plaque['title'],
                'lat': float(geo['lat']),
                'lon': float(geo['lon']),
                'address': plaque['address'],
                'categories': plaque['categories'].split(', ') if plaque['categories'] else [],
                'description': plaque['description'],
                'mainImage': plaque['local_image_path'],
                'images': [{'path': img['local_image_path'] or img['image_url'], 
                           'title': img['image_title']} 
                          for img in images if img['local_image_path'] or img['image_url']],
                'url': plaque['url']
            })
    
    conn.close()
    return jsonify(result)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    import os
    debug = os.getenv('DEBUG', 'False') == 'True'
    app.run(debug=debug, port=5000)

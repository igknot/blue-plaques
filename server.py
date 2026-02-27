from flask import Flask, jsonify, send_from_directory
import sqlite3
import json
import logging
import os

app = Flask(__name__, static_folder='.')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db():
    try:
        conn = sqlite3.connect('blue_plaques.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/favicon.svg')
def favicon():
    return send_from_directory('.', 'favicon.svg')

@app.route('/api/plaques')
def get_plaques():
    try:
        conn = get_db()
        plaques = conn.execute('''
            SELECT p.id, p.title, p.geo_location, p.address, p.categories, 
                   p.description, p.local_image_path, p.url
            FROM plaques p
            WHERE p.geo_location IS NOT NULL
        ''').fetchall()
        
        result = []
        for plaque in plaques:
            try:
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
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"Skipping plaque {plaque['id']} due to data error: {e}")
                continue
        
        conn.close()
        return jsonify(result)
    except sqlite3.Error as e:
        logger.error(f"Database error in get_plaques: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_plaques: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch plaques'}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    import os
    debug = os.getenv('DEBUG', 'False') == 'True'
    app.run(debug=debug, port=5000)

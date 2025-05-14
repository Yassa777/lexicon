from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# initialize database
def get_db():
    try:
        conn = sqlite3.connect('cache/db.sqlite')
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

@app.route('/ping', methods=['GET'])
def ping():
    logger.debug("Ping endpoint called")
    return jsonify({"message": "pong"}), 200

@app.route('/explain', methods=['POST'])
def explain():
    try:
        logger.debug(f"Received request: {request.json}")
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        term = data.get('term')
        context = data.get('context')
        
        if not term or not context:
            return jsonify({"error": "Both term and context are required"}), 400

        # hash the term + context to check cache
        cache_key = hashlib.sha256(f"{term}{context}".encode()).hexdigest()
        logger.debug(f"Cache key generated: {cache_key}")

        # check cache
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT explanation FROM cache WHERE key = ?", (cache_key,))
        row = cursor.fetchone()

        if row:
            logger.debug("Cache hit")
            return jsonify({"explanation": row[0]}), 200
        else:
            logger.debug("Cache miss")
            explanation = f"Explain {term} in context of {context}"  # temp placeholder
            cursor.execute("INSERT INTO cache (key, explanation) VALUES (?, ?)", (cache_key, explanation))
            conn.commit()
            return jsonify({"explanation": explanation}), 200
            
    except Exception as e:
        logger.error(f"Error in explain endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)

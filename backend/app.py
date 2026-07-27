import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from models import db

def create_app():
    # Set static folder to the compiled React frontend dist directory
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ram_dss.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Will create all the new tables
        db.create_all()

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "RAM-DSS running",
            "version": "v1.0-Research"
        })

    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({"status": "RAM-DSS Backend is running", "version": "1.0.1"})

    from routes import api
    app.register_blueprint(api, url_prefix='/api')

    # Catch-all route to serve React frontend for all non-API paths
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

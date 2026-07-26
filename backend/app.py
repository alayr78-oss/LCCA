import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import db

def create_app():
    app = Flask(__name__)
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ram_dss.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Will create all the new tables
        db.create_all()

    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({"status": "RAM-DSS Backend is running", "version": "1.0.1"})

    from routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

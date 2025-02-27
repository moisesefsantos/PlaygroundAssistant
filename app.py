import sys
from flask import Flask
from config import Config, db
from routes import register_routes

sys.stdout.reconfigure(encoding='utf-8')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    register_routes(app)
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

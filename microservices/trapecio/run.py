from flask import Flask
from .routes import main  

def create_app():
    app = Flask(__name__)

    app.register_blueprint(main)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
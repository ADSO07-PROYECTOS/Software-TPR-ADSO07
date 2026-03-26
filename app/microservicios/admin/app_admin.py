"""
Microservicio Admin – Sabores Unidos
Puerto: 5006
Rutas: /api/admin/*
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from rutas import modulos
for mod in modulos:
    app.register_blueprint(mod)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)

from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from conexion import *
from routes.routeUsuario import appbp

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-key"
app.permanent_session_lifetime = timedelta(minutes=30)
app = crear_conexion()  
app.register_blueprint(appbp) 


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
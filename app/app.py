from flask import Flask, render_template
import mysql.connector
from datetime import timedelta
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("auth/iniciar_sesion.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  
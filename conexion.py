from datetime import timedelta
from random import randint
from flask import * 
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = str(randint(0, 1000000))
app.config["PERMANENT_SESSION_LIFETIME"]= timedelta(minutes=1)
miDB = mysql.connector.connect(host="localhost",
                               port="3306",
                               user="root",
                               password="",
                               database="tpr_proyecto_final")
mi_cursor = miDB.cursor()
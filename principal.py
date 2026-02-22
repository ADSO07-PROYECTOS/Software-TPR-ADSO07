from conexion import *

@app.route("/")
def raiz():
    return render_template("index.html")

if __name__=='__main__':
    app.run (host="0.0.0.0", port=5000, debug=True)

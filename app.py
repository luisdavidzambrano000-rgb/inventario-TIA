from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.secret_key = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


usuarios = {
    "luis.zambrano": {
        "password": "1316926995"
    }
}


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


conexion = sqlite3.connect("inventario.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    producto TEXT,
    marca TEXT,
    cantidad INTEGER,
    caducidad TEXT
)
""")

conexion.commit()
conexion.close()


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in usuarios and usuarios[username]["password"] == password:

            user = User(username)
            login_user(user)

            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")


@app.route("/", methods=["GET", "POST"])
@login_required
def inicio():

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        codigo = request.form["codigo"]
        producto = request.form["producto"]
        marca = request.form["marca"]
        cantidad = request.form["cantidad"]
        caducidad = request.form["caducidad"]

        cursor.execute("""
        INSERT INTO productos
        (codigo, producto, marca, cantidad, caducidad)
        VALUES (?, ?, ?, ?, ?)
        """, (codigo, producto, marca, cantidad, caducidad))

        conexion.commit()

    buscar = request.args.get("buscar")

    if buscar:

        cursor.execute("""
        SELECT * FROM productos
        WHERE codigo LIKE ?
        OR producto LIKE ?
        OR marca LIKE ?
        """, (f"%{buscar}%", f"%{buscar}%", f"%{buscar}%"))

    else:

        cursor.execute("SELECT * FROM productos")

    productos_db = cursor.fetchall()

    productos = []

    hoy = datetime.now()

    vencidos = 0
    proximos = 0
    cantidad_total = 0

    for producto in productos_db:

        fecha = datetime.strptime(producto[5], "%Y-%m-%d")

        dias_restantes = (fecha - hoy).days

        cantidad_total += int(producto[4])

        if dias_restantes < 0:
            estado = "vencido"
            vencidos += 1

        elif dias_restantes <= 3:
            estado = "proximo"
            proximos += 1

        else:
            estado = "normal"

        productos.append({
            "id": producto[0],
            "codigo": producto[1],
            "nombre": producto[2],
            "marca": producto[3],
            "cantidad": producto[4],
            "caducidad": producto[5],
            "estado": estado
        })

    total_productos = len(productos)

    conexion.close()

    return render_template(
        "index.html",
        productos=productos,
        total_productos=total_productos,
        vencidos=vencidos,
        proximos=proximos,
        cantidad_total=cantidad_total
    )


@app.route("/eliminar/<int:id>")
@login_required
def eliminar(id):

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM productos WHERE id = ?", (id,))

    conexion.commit()
    conexion.close()

    return redirect("/")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        codigo = request.form["codigo"]
        producto = request.form["producto"]
        marca = request.form["marca"]
        cantidad = request.form["cantidad"]
        caducidad = request.form["caducidad"]

        cursor.execute("""
        UPDATE productos
        SET codigo = ?,
            producto = ?,
            marca = ?,
            cantidad = ?,
            caducidad = ?
        WHERE id = ?
        """, (codigo, producto, marca, cantidad, caducidad, id))

        conexion.commit()

        return redirect("/")

    cursor.execute("SELECT * FROM productos WHERE id = ?", (id,))
    producto = cursor.fetchone()

    conexion.close()

    return render_template("editar.html", producto=producto)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import random
from itertools import combinations
from flask import Flask, render_template, request, redirect
from conexion import conectar_bd

app = Flask(__name__)


@app.route("/")
def inicio():
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM Jugadores")
    jugadores = cursor.fetchall()

    conexion.close()

    return render_template("index.html", jugadores=jugadores, mensaje=None)


@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    nivel = request.form["nivel"]

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM Jugadores")
    cantidad = cursor.fetchone()[0]

    if cantidad >= 10:
        cursor.execute("SELECT * FROM Jugadores")
        jugadores = cursor.fetchall()

        conexion.close()

        return render_template(
            "index.html",
            jugadores=jugadores,
            mensaje="Ya hay 10 jugadores registrados. No podés agregar más."
        )

    cursor.execute(
        "INSERT INTO Jugadores (nombre, nivel) VALUES (?, ?)",
        (nombre, nivel)
    )

    conexion.commit()
    conexion.close()

    return redirect("/")


@app.route("/editar/<int:id_jugador>", methods=["GET", "POST"])
def editar(id_jugador):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        nivel = request.form["nivel"]

        cursor.execute(
            "UPDATE Jugadores SET nombre = ?, nivel = ? WHERE id_jugador = ?",
            (nombre, nivel, id_jugador)
        )

        conexion.commit()
        conexion.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM Jugadores WHERE id_jugador = ?",
        (id_jugador,)
    )

    jugador = cursor.fetchone()
    conexion.close()

    return render_template("editar.html", jugador=jugador)


@app.route("/eliminar/<int:id_jugador>", methods=["POST"])
def eliminar(id_jugador):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM Jugadores WHERE id_jugador = ?",
        (id_jugador,)
    )

    conexion.commit()
    conexion.close()

    return redirect("/")


@app.route("/generar_equipos", methods=["POST"])
def generar_equipos():
    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM Jugadores")
    jugadores = cursor.fetchall()

    conexion.close()

    if len(jugadores) != 10:
        return render_template(
            "index.html",
            jugadores=jugadores,
            mensaje="Necesitás tener exactamente 10 jugadores para generar los equipos."
        )

    # Obtener el equipo anterior, si existe
    equipo_anterior = set(
        request.form.getlist("equipo1")
    )

    # Probar las combinaciones posibles
    mejores_equipos = []
    menor_diferencia = None

    for equipo1 in combinations(jugadores, 5):

        # Evitar repetir la misma distribución con los equipos intercambiados
        if jugadores[0] not in equipo1:
            continue

        equipo2 = []

        for jugador in jugadores:
            if jugador not in equipo1:
                equipo2.append(jugador)

        # No repetir la distribución anterior
        ids_equipo1 = set(
            str(jugador.id_jugador) for jugador in equipo1
        )

        if ids_equipo1 == equipo_anterior:
            continue

        puntos1 = sum(jugador.nivel for jugador in equipo1)
        puntos2 = sum(jugador.nivel for jugador in equipo2)

        diferencia = abs(puntos1 - puntos2)

        if menor_diferencia is None or diferencia < menor_diferencia:
            menor_diferencia = diferencia
            mejores_equipos = [(equipo1, equipo2)]

        elif diferencia == menor_diferencia:
            mejores_equipos.append((equipo1, equipo2))

    # Elegir al azar entre las mejores distribuciones disponibles
    if mejores_equipos:
        equipo1, equipo2 = random.choice(mejores_equipos)
    else:
        return redirect("/")

    puntos1 = sum(jugador.nivel for jugador in equipo1)
    puntos2 = sum(jugador.nivel for jugador in equipo2)

    return render_template(
        "equipos.html",
        equipo1=equipo1,
        equipo2=equipo2,
        puntos1=puntos1,
        puntos2=puntos2
    )


if __name__ == "__main__":
    app.run(debug=True)

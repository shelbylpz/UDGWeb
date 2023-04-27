import os
from flask import Flask, render_template, request, redirect, session
import psycopg2
from datetime import datetime
from flask import send_from_directory

app = Flask(__name__)
app.secret_key="develoteca"


def conectar_db():
    conexion = psycopg2.connect(
        user = 'postgres',
        password = '22042003-a',
        host = 'azure-flask-dbapp.postgres.database.azure.com',
        port = '5432',
        database = 'UDGDB'
    )
    return conexion


#Sitio principal
@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route('/css/<archivocss>')
def css_link(archivocss):
    return send_from_directory(os.path.join("templates/sitio/css"),archivocss)


# Tablas
@app.route('/tablas')
def tables():
    return render_template('sitio/tablas.html')

@app.route('/tablas/<tabla>')
def tablas_seleccion(tabla):
    print(tabla)
    conexion = conectar_db()
    cursor = conexion.cursor()
    if(tabla == 'administrativo'):
        query = 'SELECT * FROM administrativo ORDER BY id'
    if (tabla == 'centro'):
        query = 'SELECT id_cent,nombre_cent,localizacion_cent,nombre FROM centro, administrativo WHERE id_adminis = id ORDER BY id_cent'
    if(tabla == 'campus'):
        query = 'SELECT id_camp,nombre_camp,localizacion_camp,nombre,nombre_cent FROM campus, centro, administrativo WHERE campus.id_adminis = administrativo.id and campus.id_cent = centro.id_cent ORDER BY id_camp'
    if(tabla == 'carrera'):
        query = 'SELECT id_car,nombre_car,cupos_car,nombre,nombre_camp FROM carrera, campus, administrativo WHERE carrera.id_adminis = administrativo.id and carrera.id_camp = campus.id_camp ORDER BY id_car'
    cursor.execute(query)
    seleccion = cursor.fetchall()
    conexion.commit()
    return render_template('sitio/tablas.html',tabla=tabla, seleccions=seleccion)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')


# Caracteristicas de Administrador
@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect('/admin/login')
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    if "login" in session:
        return redirect("/admin")
    
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario == "admin" and _password == "123":
        session["login"] = True
        session["usuario"] = "Administrador"
        return redirect("/admin")
    
    return render_template("admin/login.html", mensaje = "Acceso denegado")

@app.route('/admin/cerrar')
def admin_cerrar():
    session.clear()
    return redirect('/admin/login')

 # Administracion de datos
    #adminitrativo
@app.route('/admin/administrativo')
def admin_administrativo():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM administrativo ORDER BY id")
    administrativo = cursor.fetchall()
    conexion.commit()
    print(administrativo)

    return render_template('admin/administrativo.html', administrativo=administrativo)

@app.route('/admin/administrativo/guardar', methods=['POST'])
def admin_administrativo_guardar():
    if not 'login' in session:
        return redirect('/admin/login')
    _nombre = request.form['txtNombre']
   
    sql = "INSERT INTO administrativo (id, nombre) VALUES (DEFAULT, '"+_nombre+"');"
    

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(sql)
    conexion.commit()

    print(_nombre)
    return redirect('/admin/administrativo')

@app.route('/admin/administrativo/borrar', methods=['POST'])
def admin_administrativo_borrar():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)
    admin_administrativo_delete(_id)
    return redirect("/admin/administrativo")

def admin_administrativo_delete(_id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cent FROM centro WHERE id_adminis='"+_id+"'")
    centros = cursor.fetchall()
    for centro in centros:
        admin_centro_delete(centro[0])
    #cursor.execute("DELETE FROM administrativo WHERE id='"+_id+"'")
    cursor.execute("SELECT id_camp FROM campus WHERE id_adminis='"+_id+"'")
    campus = cursor.fetchall()
    for campu in campus:
        admin_campus_delete(campu[0])
    conexion.commit()
    conexion.close()


#centro
@app.route('/admin/centro')
def admin_centro():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM administrativo ORDER BY id")
    administrativos = cursor.fetchall()
    conexion.commit()
    print(administrativos)
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cent,nombre_cent,localizacion_cent,nombre FROM centro, administrativo WHERE id_adminis = id ORDER BY id_cent")
    centros = cursor.fetchall()
    conexion.commit()
    print(centros)
    return render_template('admin/centro.html', administrativos=administrativos, centros=centros)

@app.route('/admin/centro/guardar', methods=['POST'])
def admin_centro_guardar():
    if not 'login' in session:
        return redirect('/admin/login')
    _nombre = request.form['txtNombre']
    _localizacion = request.form['txtLocalizacion']
    _id_admin = request.form.get("txtAdmin")
   
    sql = "INSERT INTO centro (id_cent, nombre_cent,localizacion_cent,id_adminis) VALUES (DEFAULT, '"+_nombre+"','"+_localizacion+"','"+_id_admin+"');"
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(sql)
    conexion.commit()
    print(_nombre)
    print(_localizacion)
    print(_id_admin)
    return redirect('/admin/centro')

@app.route('/admin/centro/borrar', methods=['POST'])
def admin_centro_borrar():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)
    admin_centro_delete(_id)
    return redirect("/admin/centro")

def admin_centro_delete(_id):
    print(_id);
    sql = "SELECT * FROM campus WHERE id_cent="+str(_id)+";"
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(sql)
    campuss = cursor.fetchall()
    for campus in campuss:
        admin_campus_delete(campus[0])
    cursor.execute("DELETE FROM centro WHERE id_cent='"+str(_id)+"';")
    conexion.commit()
    conexion.close()
    
@app.route('/admin/centro/edit', methods=['POST'])
def admin_centro_edit():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM administrativo ORDER BY id")
    administrativos = cursor.fetchall()
    sql = "SELECT id_cent,nombre_cent,localizacion_cent,nombre FROM centro, administrativo WHERE id_adminis = id AND id_cent='"+_id+"';"
    cursor.execute(sql)
    centro = cursor.fetchall()
    conexion.commit()
    print(centro)

    return render_template('admin/centro/update.html', centro=centro, administrativos=administrativos)

@app.route('/admin/centro/update', methods=['POST'])
def admin_centro_update():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']

    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "SELECT * FROM centro WHERE id_cent='"+_id+"';"
    cursor.execute(sql,_id)
    centroOld = cursor.fetchall()
    conexion.commit()
    print(centroOld)

    _nombre = request.form['txtNombre']
    if _nombre == '':
        print("Si esta vacia nombre")
        _nombre = centroOld[0][1]
    _localizacion = request.form['txtLocalizacion']
    if _localizacion == '':
        print("Si esta vacia marca")
        _localizacion = centroOld[0][2]
    _admin = request.form['txtAdmin']
    if _admin == '':
        print("Si esta vacia modelo")
        _admin = centroOld[0][3]
    print(_id)
    print(_nombre)
    print(_localizacion)
    print(_admin)

    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "UPDATE centro SET nombre_cent='"+_nombre+"', localizacion_cent='"+_localizacion+"', id_adminis="+str(_admin)+" WHERE id_cent="+_id
    cursor.execute(sql)
    conexion.commit()


    return redirect("/admin/centro")

#Campus
@app.route('/admin/campus')
def admin_campus():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM administrativo ORDER BY id")
    administrativos = cursor.fetchall()
    cursor.execute("SELECT * FROM centro ORDER BY id_cent")
    centros = cursor.fetchall()
    conexion.commit()
    print(administrativos)
    print(centros)
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_camp,nombre_camp,localizacion_camp,nombre,nombre_cent FROM campus, centro, administrativo WHERE campus.id_adminis = administrativo.id and campus.id_cent = centro.id_cent ORDER BY id_camp")
    campuss = cursor.fetchall()
    conexion.commit()
    print(campuss)
    return render_template('admin/campus.html', administrativos=administrativos, campuss=campuss, centros=centros)

@app.route('/admin/campus/guardar', methods=['POST'])
def admin_campus_guardar():
    if not 'login' in session:
        return redirect('/admin/login')
    _nombre = request.form['txtNombre']
    _localizacion = request.form['txtLocalizacion']
    _id_admin = request.form.get("txtAdmin")
    _id_centro = request.form.get("txtCentro")
   
    sql = "INSERT INTO campus (id_camp, nombre_camp,localizacion_camp,id_adminis,id_cent) VALUES (DEFAULT, '"+_nombre+"','"+_localizacion+"','"+_id_admin+"','"+_id_centro+"');"
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(sql)
    conexion.commit()
    print(_nombre)
    print(_localizacion)
    print(_id_admin)
    return redirect('/admin/campus')

@app.route('/admin/campus/borrar', methods=['POST'])
def admin_campus_borrar():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)
    admin_campus_delete(_id)
    return redirect("/admin/campus")

def admin_campus_delete(id):
    print(id)
    sql = "DELETE FROM campus WHERE id_camp='"+str(id)+"';"
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(sql)
    conexion.commit()
    conexion.close()

@app.route('/admin/campus/edit', methods=['POST'])
def admin_campus_edit():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM administrativo ORDER BY id")
    administrativos = cursor.fetchall()
    cursor.execute("SELECT * FROM centro ORDER BY id_cent")
    centros = cursor.fetchall()
    cursor.execute("SELECT id_camp,nombre_camp,localizacion_camp,nombre,nombre_cent FROM campus, centro, administrativo WHERE campus.id_adminis = administrativo.id and id_camp="+_id+";")
    campus = cursor.fetchall()
    conexion.commit()
    return render_template('admin/campus/update.html', campus=campus,centros=centros, administrativos=administrativos)

@app.route('/admin/campus/update', methods=['POST'])
def admin_campus_update():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']

    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "SELECT * FROM campus WHERE id_camp='"+_id+"';"
    cursor.execute(sql,_id)
    old = cursor.fetchall()
    conexion.commit()
    print(old)

    _nombre = request.form['txtNombre']
    if _nombre == '':
        print("Si esta vacia nombre")
        _nombre = old[0][1]
    _localizacion = request.form['txtLocalizacion']
    if _localizacion == '':
        print("Si esta vacia localizacion")
        _localizacion = old[0][2]
    _admin = request.form.get('txtAdmin')
    if _admin == '':
        print("Si esta vacia administrativo")
        _admin = old[0][3]
    _centro = request.form.get('txtCentro')
    if _centro == '':
        print("Si esta vacia centro")
        _centro = old[0][4]
    print(_id)
    print(_nombre)
    print(_localizacion)
    print(_admin)

    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "UPDATE campus SET nombre_camp='"+_nombre+"', localizacion_camp='"+_localizacion+"', id_adminis="+str(_admin)+", id_cent="+str(_centro)+" WHERE id_camp="+_id
    cursor.execute(sql)
    conexion.commit()


    return redirect("/admin/campus")
#PArte de administracion de datos

@app.route('/admin/autos')
def admin_autos():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM auto ORDER BY id")
    autos = cursor.fetchall()
    conexion.commit()
    print(autos)

    return render_template('admin/autos.html', autos=autos)

@app.route('/admin/autos/guardar', methods=['POST'])
def admin_autos_guardar():
    if not 'login' in session:
        return redirect('/admin/login')
    _matricula = request.form['txtMatricula']
    _marca = request.form['txtMarca']
    _modelo = request.form['txtModelo']

    sql = "INSERT INTO auto (id, matricula, marca, modelo) VALUES (DEFAULT, %s, %s, %s);"
    datos=(_matricula,_marca,_modelo)

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    print(_matricula)
    print(_marca)
    print(_modelo)

    return redirect('/admin/autos')

@app.route('/admin/autos/borrar', methods=['POST'])
def admin_autos_borrar():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)


    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM auto WHERE id=%s",(_id))
    conexion.commit()


    return redirect("/admin/autos")
@app.route('/admin/autos/edit', methods=['POST'])
def admin_edit_auto():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']
    print(_id)
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "SELECT * FROM auto WHERE id=%s"
    cursor.execute(sql,_id)
    autos = cursor.fetchall()
    conexion.commit()
    print(autos)

    return render_template('admin/update.html', autos=autos)

@app.route('/admin/autos/update', methods=['POST'])
def admin_auto_update():
    if not 'login' in session:
        return redirect('/admin/login')
    _id = request.form['txtID']

    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "SELECT * FROM auto WHERE id=%s"
    cursor.execute(sql,_id)
    autoOld = cursor.fetchall()
    conexion.commit()
    print(autoOld)

    _matricula = request.form['txtMatricula']
    if _matricula == '':
        print("Si esta vacia matricula")
        _matricula = autoOld[0][1]
    _marca = request.form['txtMarca']
    if _marca == '':
        print("Si esta vacia marca")
        _marca = autoOld[0][2]
    _modelo = request.form['txtModelo']
    if _modelo == '':
        print("Si esta vacia modelo")
        _modelo = autoOld[0][3]
    print(_id)
    print(_matricula)
    print(_marca)
    print(_modelo)

    conexion = conectar_db()
    cursor = conexion.cursor()
    sql = "UPDATE auto SET matricula='"+_matricula+"', marca='"+_marca+"', modelo='"+_modelo+"' WHERE id="+_id
    cursor.execute(sql)
    conexion.commit()


    return redirect("/admin/autos")

if __name__ == '__main__':
    app.run(debug=True)
from IO import *
from tabulate import tabulate
from Empresas import AgregarTrabajos, CrearEmpresa
from datetime import date

import psycopg2
conn = psycopg2.connect(database="grupo3", user="grupo3", password="2gKdbj", host="201.238.213.114", port="54321")
# ----------QUERYS----------
CONTACTOS_USUARIO = '(SELECT todos.correo correo, todos.amigo amigo' \
                    ' FROM ' \
                    '(SELECT u.correo correo, COUNT(*) amigos, ' \
                    ' CASE  WHEN u.correo = s.correo_usuario_emisor THEN s.correo_usuario_receptor ' \
                    'WHEN u.correo = s.correo_usuario_receptor THEN s.correo_usuario_emisor ' \
                    'END amigo ' \
                    'FROM ' \
                    'usuario u JOIN solicitud s ON (u.correo = s.correo_usuario_emisor OR u.correo = s.correo_usuario_receptor) ' \
                    'WHERE  s.estado = \'aceptada\' ' \
                    'GROUP BY u.correo, s.correo_usuario_receptor, s.correo_usuario_emisor ORDER BY amigos DESC) todos ' \
                    'ORDER BY todos.correo DESC)'
VER_PERFIL = "SELECT * FROM Perfil WHERE correo_usuario = '{}' "
VER_ESTUDIOS = "SELECT em.nombre, e.grado_academico, e.descripcion, e.fecha_inicio, e.fecha_termino " \
               "FROM Estudio e JOIN Empresa em ON e.id_empresa = em.id " \
               "WHERE correo_usuario = '{}'"
VER_TRABAJOS = "SELECT t.id, e.nombre, t.descripcion, tr.fecha_inicio, tr.fecha_termino" \
               " FROM " \
               "Trabajo t JOIN Empresa e ON t.id_empresa = e.id " \
               "JOIN Trabajado tr ON t.id = tr.id_trabajo " \
               "JOIN Perfil p ON p.id = tr.id_perfil" \
               " WHERE p.correo_usuario = '{}'"
VER_ULTIMAS2_PUBLICACIONES = "SELECT texto, foto, link, fecha " \
                             "FROM Publicacion " \
                             "WHERE correo_usuario = '{}' AND borrada = false " \
                             "ORDER BY fecha DESC " \
                             "LIMIT 2"
VER_HABILIDADES = "SELECT h.id, h.nombre, COUNT(v.id_perfil_habilidad) " \
                  "FROM Habilidad h JOIN Perfil_habilidad pf ON h.id = pf.id_habilidad " \
                  "JOIN Perfil p ON p.id=pf.id_perfil " \
                  "LEFT JOIN Validacion v ON pf.id = v.id_perfil_habilidad " \
                  "WHERE p.correo_usuario = '{}' " \
                  "GROUP BY h.id"
VER_CONTACTOS_COMUNES = "SELECT amigo FROM {} contactos" \
                        " WHERE amigo in (SELECT amigo FROM {} contactos WHERE correo = '{}')" \
                        " AND amigo IN (SELECT amigo FROM {} contactos WHERE correo = '{}') "
VER_IDPERFILHABILIDAD = "SELECT pf.id " \
                        "FROM Habilidad h JOIN Perfil_habilidad pf ON h.id = pf.id_habilidad " \
                        "JOIN Perfil p ON p.id=pf.id_perfil " \
                        "LEFT JOIN Validacion v ON pf.id = v.id_perfil_habilidad " \
                        "WHERE p.correo_usuario = '{}' AND h.nombre = '{}'"
VER_IDVALIDACIONES = "SELECT id FROM Validacion"
VER_SOLICITUDESPENDIENTES = "SELECT * FROM Solicitud WHERE correo_usuario_receptor = '{}' AND estado = 'pendiente'"

HABILIDADES_VALIDACIONES = "select h.id, v.id, v.correo_usuario_calificador "\
                        "from habilidad h, perfil_habilidad ph, validacion v, perfil p "\
                        "where h.id = ph.id_habilidad and ph.id = v.id_perfil_habilidad "\
                        "and p.id = ph.id_perfil and h.id = {} and p.correo_usuario = '{}'"

NUEVA_EXPERIENCIA_LABORAL = "INSERT INTO trabajado(id, id_trabajo, id_perfil, fecha_inicio) "\
                            "VALUES({}, {}, {}, '{}')"

def MenuVerPerfil(usuario, conn):
    volver = False
    while not volver:
        VerPerfilHastaHabilidad(usuario, conn)
        ImprimirTitulo("Ver perfil")
        Imprimir("Que desea hacer?\n"
                 "(1) Editar Perfil\n"
                 "(2) Seleccionar nueva foto de perfil\n"
                 "(3) Ver Habilidades\n"
                 "(4) Ver experiencia laboral\n"
                 "(5) Ver educacion\n"
                 "(6) Eliminar Cuenta\n"
                 "(7) Volver\n"
                 "(8) Salir\n")
        opcion = ValidarOpcion(range(1,9))
        if opcion == 1:
            EditarPerfil(usuario, conn)
        elif opcion == 2:
            CambiarFoto(usuario, conn)
        elif opcion == 3:
            VerHabilidades(usuario, conn)
        elif opcion == 4:
            VerExperienciaLaboral(usuario, conn)
        elif opcion == 5:
            VerEducacion(usuario, conn)
        elif opcion == 6:
            EliminarCuenta(usuario, conn)
        elif opcion == 7:
            volver = True
            return
        elif opcion == 8:
            conn.close()
            sys.exit(0)
    return
#MenuVerPerfil("Mono1Apellido1@gmail.com", conn)


def EditarPerfil(usuario, conn):
    cur = conn.cursor()
    VerPerfilHastaHabilidad(usuario, conn)
    atributosPerfil=["Correo", "Nombre", "Apellido", "Fecha de Nacimiento", "Pais", "Sexo", "Descripcion"]
    cont = 0
    for i in atributosPerfil:
        cont+=1
        Imprimir("({}) {}".format(cont, i))
    opcion = ValidarOpcion(range(1,7))
    atributosPerfil = ["correo", "nombre", "apellido", "fecha_nacimiento", "pais", "sexo", "descripcion"]
    atributoCambiar=atributosPerfil[opcion-1]
    info = input("Ingrese {}: ".format(atributoCambiar))
    if atributoCambiar == "correo":
        cur.execute("UPDATE Usuario SET correo = {} WHERE correo = '{}'".format(info, usuario))
    else:
        cur.execute("UPDATE Perfil SET {} = {} WHERE correo_usuario = '{}'".format(atributoCambiar,info, usuario))
    conn.commit()
    return
def CambiarFoto(usuario, conn):
    cur = conn.cursor()
    foto = input("Ingrese el nombre del archivo:")
    cur.execute("SELECT id FROM Perfil WHERE correo_usuario = '{}'".format(usuario))
    row = cur.fetchall()
    id = row[0][0]
    cur.execute("UPDATE foto_perfil SET foto = '{}' WHERE id_perfil = {} ".format(foto, id))
    Imprimir("Foto cambiada")
    return
def VerHabilidades(usuario, conn):
    while(True):
        cur = conn.cursor()
        cur.execute("select id from perfil where correo_usuario = '{}'".format(usuario))
        id_perfil = cur.fetchone()
        id_perfil = id_perfil[0]
        ImprimirTitulo("ver habilidades")
        cur.execute(VER_HABILIDADES.format(usuario))
        respuesta_inicio = cur.fetchall()
        matriz_mostrar_inicio = [["HABILIDAD", "DESCRIPCION", "CANTIDAD DE VALIDACIONES"]]
        ids = []
        for tupla in respuesta_inicio:
            ids.append(tupla[0])
            matriz_mostrar_inicio.append([tupla[0], tupla[1], tupla[2]])
        Imprimir(tabulate(matriz_mostrar_inicio))
        Imprimir("Que desea hacer?\n"
                 "(1) Ver Habilidad\n"
                 "(2) Agregar Habilidad\n"
                 "(3) Eliminar Habilidad\n"
                 "(4) Volver al menu anterior\n"
                 "(5) Salir\n")
        opcion = ValidarOpcion(range(1,6))
        if opcion == 5:
            if HayConexionBD(conn):
                conn.close()
            sys.exit(0)
        elif opcion == 4:
            return
        elif opcion == 1: # ver habilidad
            habilidad_seleccionada = ValidarOpcion(ids, "Seleccione la habilidad que quiere ver: ")
            cur.execute(HABILIDADES_VALIDACIONES.format(habilidad_seleccionada, usuario))
            respuesta = cur.fetchall()
            if len(respuesta) > 0:
                matriz_mostrar = [["HABILIDAD", "VALIDACION", "VALIDADA POR"]]
                for tupla in respuesta:
                    matriz_mostrar.append([tupla[0], tupla[1], tupla[2]])
                Imprimir(tabulate(matriz_mostrar))
            else:
                Imprimir("La habilidad seleccionada no tiene validaciones")
        elif opcion == 2: # agregar habilidad
            cur.execute("select * from habilidad")
            respuesta = cur.fetchall()
            idsNoDelUsuario = []
            matriz_mostrar = [["HABILIDAD", "DESCRIPCION"]]
            for tupla in respuesta:
                if tupla[0] not in ids:
                    idsNoDelUsuario.append(tupla[0])
                    matriz_mostrar.append([tupla[0], tupla[1]])
            Imprimir(tabulate(matriz_mostrar))
            Imprimir("Que deseas hacer?\n"
                     "\t(1) Seleccionar una habilidad existente\n"
                     "\t(2) Crear una habilidad nueva\n")
            seleccionarOcrear = ValidarOpcion(range(1,3))
            if seleccionarOcrear == 1:
                habilidadAagregar = ValidarOpcion(idsNoDelUsuario,
                "Seleccione la habilidad que quiere agregar a su perfil: ")
                cur.execute("insert into perfil_habilidad(id, id_perfil, id_habilidad) "
                            "values({}, {}, {})".format(SiguienteID("perfil_habilidad", conn),
                                                        id_perfil, habilidadAagregar))
                conn.commit()
            elif seleccionarOcrear == 2:
                nombre_nuevo = input("Ingrese el nombre de la nueva habilidad: ")
                while len(nombre_nuevo) == 0 or len(nombre_nuevo) > 100:
                    nombre_nuevo = input("Error, largo del nombre invalido, ingreselo nuevamente:")
                nuevoIDhabilidad = SiguienteID("habilidad", conn)
                cur.execute("insert into habilidad(id, nombre) "
                            "values({}, '{}')".format(nuevoIDhabilidad, nombre_nuevo))
                conn.commit()
                cur.execute("insert into perfil_habilidad(id, id_perfil, id_habilidad) "
                            "values({}, {}, {})".format(SiguienteID("perfil_habilidad", conn),
                                                        id_perfil, nuevoIDhabilidad))
                conn.commit()
        elif opcion == 3: # eliminar habilidad
            habilidad_seleccionada = ValidarOpcion(ids, "Seleccione la habilidad que quiere eliminar: ")

        cur.close()

u = "Mono3Apellido3@gmail.com"

def VerExperienciaLaboral(usuario,conn):
    while(True):
        cur = conn.cursor()
        cur.execute("select id from perfil where correo_usuario = '{}'".format(usuario))
        id_perfil = cur.fetchone()
        id_perfil = id_perfil[0]
        ImprimirTitulo("experiencia laboral: trabajos")
        cur.execute(VER_TRABAJOS.format(usuario))
        trabajos = cur.fetchall()
        tab = [["TRABAJO", "EMPRESA"]]
        idsTrabajos = []
        for t in trabajos:
            tab.append([t[0], t[1]])
            idsTrabajos.append(t[0])
        Imprimir(tabulate(tab))

        Imprimir("Que desea hacer?\n"
                 "(1) Ver Experiencia Laboral\n"
                 "(2) Agregar Experiencia Laboral\n"
                 "(3) Eliminar Experiencia Laboral\n"
                 "(4) Volver al menu anterior\n"
                 "(5) Salir\n")
        opcion = ValidarOpcion(range(1, 6))
        if opcion == 5:
            if HayConexionBD(conn):
                conn.close()
            sys.exit(0)
        elif opcion == 4:
            return
        elif opcion == 1:
            trabajo_elegido = ValidarOpcion(idsTrabajos, "Seleccione el trabajo que quiere ver: ")
            tablaTrabajos = list()
            atributosTrabajo = ["Trabajo", "Empresa", "Descripcion del trabajo", "Fecha inicio", "Fecha termino"]

            for trabajo in trabajos:
                if trabajo[0] == trabajo_elegido:
                    for i in range(len(trabajo)):
                        tablaTrabajos.append([atributosTrabajo[i], trabajo[i]])
                    Imprimir(tabulate(tablaTrabajos))

        elif opcion == 2:
            cur.execute("SELECT id, nombre FROM empresa")
            emp = cur.fetchall()
            idsEmpresasTodas = []
            tab = [["EMPRESA", "NOMBRE"]]
            for e in emp:
                idsEmpresasTodas.append(e[0])
                tab.append([e[0], e[1]])
            Imprimir(tabulate(tab))
            Imprimir("Que deseas hacer?\n"
                     "\t(1) Agregar empresa a experiencia laboral\n"
                     "\t(2) Crear empresa nueva\n")
            hacer = ValidarOpcion(range(1,3))
            fecha_actual = date.today()
            if hacer == 1:
                empresaAagregar = ValidarOpcion(idsEmpresasTodas, "Seleccione la empresa que quiere agregar: ")
                AgregarTrabajos(empresaAagregar, conn)
                idNuevoTrabajo = SiguienteID("trabajo", conn)
                cur.execute(NUEVA_EXPERIENCIA_LABORAL.format(SiguienteID("trabajado", conn),
                            idNuevoTrabajo-1, id_perfil, fecha_actual))
                conn.commit()
            elif hacer == 2:
                CrearEmpresa(usuario, conn)
                nuevaEmpresa = SiguienteID("empresa", conn)
                Imprimir()
                Imprimir("AHORA CREE UN TRABAJO")
                AgregarTrabajos(nuevaEmpresa-1, conn)
                idNuevoTrabajo = SiguienteID("trabajo", conn)
                cur.execute(NUEVA_EXPERIENCIA_LABORAL.format(SiguienteID("trabajado", conn),
                            idNuevoTrabajo-1, id_perfil, fecha_actual))
                conn.commit()
            elif hacer == 3:
                print("Aca hay que eliminar una experiencia laboral")


def VerEducacion(usuario, conn):
    return
def EliminarCuenta(usuario, conn):
    opcion = input("Ingresa 'Si' si deseas eliminar tu cuenta, si no, ingresa cualquier cosa")
    if opcion in ["si, SI, Si, sI"]:
        cur = conn. cursor()
        cur.execute("DELETE FROM Usuario WHERE correo = '{}'".format(usuario))#Quedo tan corto porque lo hicimos con cascade
        conn.commit()

    return
EliminarCuenta("a@a.a", conn)
from IO import *
from tabulate import tabulate
import psycopg2
conn = psycopg2.connect(database="grupo3", user="grupo3", password="2gKdbj", host="201.238.213.114", port="54321")

u = "Mono50Apellido50@gmail.com"

def MenuVerNotificacion(usuario, conn):
    cur = conn.cursor()
    cur.execute("select * from notificacion where leida = FALSE"
                " and correo_usuario = '{}';".format(usuario))
    notis = cur.fetchall()
    print(notis)
    ImprimirTitulo("NOTIFICACIONES NO LEIDAS")
    ListaNotificaciones = []
    ln = []
    for n in notis:
        ListaNotificaciones.append([n[0]])
        ln.append(n[0])
    Imprimir(tabulate(ListaNotificaciones))
    Imprimir("Que desea hacer?\n"
             "\t(1) Ver notificacion\n"
             "\t(2) Seleccionar todas las notificaciones como leidas\n"
             "\t(3) Ver notificaciones leidas\n"
             "\t(4) Volver al menu anterior\n"
             "\t(5) Salir\n")
    opcion = ValidarOpcion(range(1, 6))
    if opcion == 5:
        sys.exit(0)
    elif opcion == 4:
        return
    elif opcion == 1:
        opcionNotificacion = ValidarOpcion(ln, "Seleccione la notificacion que quiere ver: ")
        atributosNotificacion = ["Notificacion", "Evento", "Correo", "Leida"]
        ListaNotisDetalles = []
        for n in notis:
            if n[0] == opcionNotificacion:
                for i in range(len(atributosNotificacion)):
                   ListaNotisDetalles.append([atributosNotificacion[i], n[i]])

        Imprimir(tabulate(ListaNotisDetalles))
        cur.execute("update notificacion set leida = TRUE"
                    " where id = {} and correo_usuario = '{}';".format(opcionNotificacion, usuario))
        conn.commit()

    elif opcion == 2:
        cur.execute("update notificacion set leida = TRUE"
                    " where leida = FALSE and correo_usuario = '{}';".format(usuario))
        conn.commit()
    elif opcion == 3:
        cur.execute("select * from notificacion where leida = TRUE"
                    " and correo_usuario = '{}';".format(usuario))
        notisLeidas = cur.fetchall()
        lnl = []
        ListaNotificacionesLeidas = []
        for nl in notisLeidas:
            ListaNotificacionesLeidas.append([nl[0]])
            lnl.append(nl[0])
        Imprimir(tabulate(ListaNotificacionesLeidas))
        respuesta = ValidarOpcion(range(1,3),"Quiere ver alguna notificacion en detalle?\n"
                          "\t(1) si\n"
                          "\t(2) no\n"
                          "Ingrese su opcion: ")
        if respuesta == 1:
            opcionNotificacionLeida = ValidarOpcion(lnl, "Seleccione la notificacion que quiere ver: ")
            atributosNotificacion = ["Notificacion", "Publicacion", "Correo", "Leida"]
            ListaNotisDetalles = []
            for n in notisLeidas:
                if n[0] == opcionNotificacionLeida:
                    for i in range(len(atributosNotificacion)):
                        ListaNotisDetalles.append([atributosNotificacion[i], n[i]])
            Imprimir(tabulate(ListaNotisDetalles))
    cur.close()
    conn.close()


MenuVerNotificacion(u, conn)
import cv2, numpy as np, psycopg2
from datetime import datetime
from cv2 import cv2
from pyzbar.pyzbar import decode

datosQr = ""

# Conexcion a la base de datos
conexion = psycopg2.connect("dbname=Empleados user=postgres password=1q2w3e4r")
# Creamos el cursor con el objeto conexion
cur = conexion.cursor()

# Función para consultar a una base de datos
def consulta(identificacion):
    cur.execute( "SELECT identificacion, nombres, apellidos FROM reg_empleados WHERE identificacion = %s", (identificacion,))
    return cur.fetchone()

# Función para registrar la entrada de un empleado al leer el codigo QR
def registrarEntrada(empleado, fecha):
    empleado = int(empleado)
    fechaHoy = fecha.strftime('%Y-%m-%d')
    horaHoy = fecha.strftime('%H:%M:%S')
    cur.execute( "INSERT INTO registro_entrada (empleado, fecha, hora_entrada) VALUES (%s, %s, %s);", (empleado, fechaHoy, horaHoy))
    conexion.commit()

# Función para registrar la salida de un empleado al leer el codigo QR
def registrarSalida(empleado, fecha):
    empleado = int(empleado)
    fechaHoy = fecha.strftime('%Y-%m-%d')
    horaHoy = fecha.strftime('%H:%M:%S')
    cur.execute( "INSERT INTO registro_entrada (empleado, fecha, hora_salida) VALUES (%s, %s, %s);", (empleado, fechaHoy, horaHoy))
    conexion.commit()

cap = cv2.VideoCapture(0) # Iniciamos la camara
cap.set(3,640)
cap.set(4,480)

while 1:

    fecha = datetime.now()

    success, img = cap.read() # Capturamos un frame
    for qrcode in decode(img):
        myQR = qrcode.data.decode('utf-8') # Decodificamos el codigo QR
        
        # Comparamos el codigo decodificado con una variable
        # la cual se reemplaza al ser diferente, esto para evitar la inserción del mismo registro.
        if myQR != datosQr:
            datosQr = myQR
            consul = consulta(myQR)

            # Comaración para registrar la hora de salida y la hora de entrada
            if (fecha.strftime('%H:%M') >= "07:00") and (fecha.strftime('%H:M') <= "19:00"):
                registrarEntrada(myQR, fecha)
            else:
                registrarSalida(myQR, fecha)

        if consul != "":
            salida = 'Authorizado'
            color = (0,255,0)

        else:
            salida = 'No-Authorizado'
            color = (0, 0, 255)

        pts = np.array([qrcode.polygon],np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(img,[pts],True,color,5)
        pts2 = qrcode.rect
        cv2.putText(img,salida,(pts2[0],pts2[1]),cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,color,2)

    cv2.imshow('Result',img)

    #Salir con 'ESC'
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
import sys
import serial
import random
from protocol import *
from socket_wrapp import Socket


class DataGeneratorMock():
    def readline(self):
        return ','.join(str(random.random()*10) for _ in range(3)).encode()


class DataGenerator():
    def __init__(self):
        try:
            self.arduino = serial.Serial('/dev/ttyACM0')    # Pasar como argv
        except serial.serialutil.SerialException:
            self.arduino = DataGeneratorMock()

    def get_data(self):
        return self.arduino.readline().strip()


class Fuente(Protocol):
    def __init__(self, sock, dataGenerator):
        self.sock = sock
        self.dgenerator = dataGenerator
        self.id = None

    def connect_server(self, host, port):
        self.sock.connect(host, port)

    def send_data(self):
        data = self.dgenerator.get_data()
        if data == b'fail':
            print("La fuente fallo")

        self.send_post(data)
        time.sleep(4)


if __name__ == '__main__':
    fuente = Fuente(Socket(), DataGenerator())
    fuente.connect_server(sys.argv[1], int(sys.argv[2]))

    fuente.send_sus(SUS_OP_FUENTE, 'text;temperatura,humedad,presion')

    while True:
        opcode, dlen = fuente.recive_header()
        print("Recibi un mensaje del tipo {} con un dlen {}".
                format(opcode, dlen))
        if opcode == RESP:
            msg = fuente.recive_resp(dlen)
            if msg[0] == RESP_TIPO_OK:
                if msg[1] == RESP_CODIGO_101:
                    fuente.id = int(msg[2])
                    print("Solicitud aceptada. Enviando datos")
                if msg[1] == RESP_CODIGO_101 or msg[1] == RESP_CODIGO_103:
                    fuente.send_data()

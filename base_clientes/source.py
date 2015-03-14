import sys
import serial
import random
import time
from .protocol import (
        BaseClient,
        SUS_OP_FUENTE,
        RESP_TIPO_OK,
        RESP_CODIGO_101,
        RESP_CODIGO_103
        )
from .socket_wrapp import Socket


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


class Fuente(BaseClient):
    def __init__(self, sock, dataGenerator):
        if sock is None:
            sock = Socket()
        super().__init__(sock)
        self.dgenerator = dataGenerator

    def send_data(self):
        data = self.dgenerator.get_data()
        if data == b'fail':
            print("La fuente fallo")

        self.send_post(data)
        tipo, codigo, datos = self.recive_response()
        if (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_103):
            time.sleep(4)
            return True
        return False

    def send_suscription(self, datatype, description):
        self.send_sus(SUS_OP_FUENTE, datatype + ';' + description)
        tipo, codigo, datos = self.recive_response()
        if (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_101):
            self.id = int(datos)
            return True
        return False


if __name__ == '__main__':
    fuente = Fuente(Socket(), DataGenerator())
    fuente.connect_server(sys.argv[1], int(sys.argv[2]))

    if fuente.send_suscription("text", "temperatura,humdedad,presion"):
        while fuente.send_data():
            pass

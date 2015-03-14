""" Source

Usage:
    source.py <host> <port> source --serial <sport> [--baud=<int>]
    source.py <host> <port> source --fake <ndata>

Options:
    -s --serial          connect the source to serial port
    -f --fake            Fake data
    -b --baud=<int>      Baud rate [default: 9600]
    -h --help            Show this help
    -v --version         Show Version
"""

__version__ = 0.1

import serial
import random
import time
from docopt import docopt
from protocol import (
            BaseClient,
            SUS_OP_FUENTE,
            RESP_TIPO_OK,
            RESP_CODIGO_101,
            RESP_CODIGO_103
            )
from socket_wrapp import Socket


class DataGeneratorMock():
    def __init__(self, num_data):
        self.num_data = num_data

    def get_data(self):
        data = ((str(random.random() * 10)) for _ in range(self.num_data))
        return ','.join(data).encode()


class DataGenerator():
    def __init__(self, port, baud):
        self.arduino = serial.Serial(port, baud)

    def get_data(self):
        return self.arduino.readline().strip()


class Fuente(BaseClient):
    def __init__(self, dataGenerator):
        super().__init__(Socket())
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
    arg = docopt(__doc__, version=__version__)
    if arg['--fake']:
        data_generator = DataGeneratorMock(int(arg['<ndata>']))
    else:
        data_generator = DataGenerator(arg['<sport>'], int(arg['--baud']))

    fuente = Fuente(data_generator)
    fuente.connect_server(arg['<host>'], int(arg['<port>']))

    data_type = input(">> Ingrese de codificación (text|int): ")
    datos = input(">> Ingrese el nombre de los datos separados por coma " +
                  "(temp,humedad): ")

    if fuente.send_suscription(data_type, datos):
        while fuente.send_data():
            pass

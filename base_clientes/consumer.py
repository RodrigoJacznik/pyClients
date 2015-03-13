import sys
from protocol import *
from socket_wrapp import Socket


class Consumidor(BaseClient):
    def __init__(self, sock):
        super().__init__(sock)

    def request_sources(self):
        self.send_get(GET_OP_NORMAL, ALL_SOURCES)
        tipo, codigo, datos = self.recive_response()
        if (tipo != RESP_TIPO_FAIL):
            return datos.decode().strip().split(";")
        return []

    def select_source(self, idSource):
        cons.send_sus(SUS_OP_CONS, idSource)
        tipo, codigo, datos = self.recive_response()
        if (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_101):
            self.id = int(datos)
            return True
        return False

    def start_stream(self, op, idSource, tm_inicio=0, tm_fin=0):
        self.send_get(op, idSource, tm_inicio, tm_fin)
        tipo, codigo, datos = self.recive_response()
        while (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_104):
            yield datos
            tipo, codigo, datos = self.recive_response()


if __name__ == '__main__':
    cons = Consumidor(Socket())
    cons.connect_server(sys.argv[1], int(sys.argv[2]))
    datos = []

    sources = cons.request_sources()
    if (cons.select_source("1")):
        for dato in cons.start_stream(GET_OP_NORMAL, 1):
            datos.append(dato)
    print(datos)

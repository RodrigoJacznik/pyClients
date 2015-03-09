import sys
from protocol import *
from socket_wrapp import Socket


class Consumidor(BaseClient):
    def __init__(self, sock):
        super().__init__(sock)


if __name__ == '__main__':
    cons = Consumidor(Socket())
    cons.connect_server(sys.argv[1], int(sys.argv[2]))

    cons.send_get(0, 0)
    opcode, dlen = cons.recive_header()
    tipo, codigo, datos = cons.recive_resp(dlen)
    cons.send_sus(1, '1')
    opcode, dlen = cons.recive_header()
    tipo, codigo, datos = cons.recive_resp(dlen)
    if (tipo == RESP_TIPO_OK and codigo == RESP_CODIGO_101):
        cons.id = int(datos)
        cons.send_get(0, 1)
        opcode, dlen = cons.recive_header()
        tipo, codigo, datos = cons.recive_resp(dlen)
        codigo = RESP_CODIGO_104
        while (codigo == RESP_CODIGO_104):
            print(datos)
            opcode, dlen = cons.recive_header()
            tipo, codigo, datos = cons.recive_resp(dlen)


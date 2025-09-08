import socket
import sys

tests={
    ('AD','0.50'): 'Romanesque church of Santa Coloma',
    ('AT','0.20'): 'Belvedere Palace',
    ('BE','0.02'): 'Portrait of King Philippe',
    ('CY','0.05'): 'Kyrenia ship',
    ('EE','0.01'): 'Geographical image of Estonia',
    ('FI','0.05'): 'Lion from Finnish coat of arms',
    ('FR','0.50'): 'Marianne',
    ('DE','2'): 'Oak twig',
    ('GR','1'): 'Owl from ancient Athenian tetradrachm',
    ('HR','0.50'): 'Nikola Tesla portrait on chequerboard',
    ('IE','0.02'): 'Celtic harp',
    ('IT','0.20'): 'Futurist sculpture by Umberto Boccioni',
    ('LV','1'): 'Latvian folk maiden',
    ('LT','0.05'): 'Coat of arms (Vytis)',
    ('LU','0.10'): 'Portrait of Grand Duke Henri',
    ('MT','1'): 'Maltese Cross',
    ('MC','0.10'): 'Monogram of Prince Albert II',
    ('NL','0.01'): 'Portrait of King Willem-Alexander',
    ('PT','0.02'): 'Royal seal of 1142',
    ('SM','0.50'): 'Three Towers of San Marino',
    ('SK','0.10'): 'Bratislava Castle',
    ('SI','0.20'): 'Pair of Lipizzaner horses',
    ('ES','0.05'): 'Miguel de Cervantes',
    ('VA','0.20'): 'Coat of arms of Pope Leo XIV',
    ('IT','2 cent'): 'Not found',    
    ('Italy','2'): 'Not found',    
    ('UK','2'): 'Not found',    
}


HOST = '127.0.0.1'
PORT = 4321

def make_request(country_code, coin_value):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(f"{country_code},{coin_value}\x00".encode('utf-8'))
            response_data = b''
            while True:
                chunk = s.recv(1024)
                response_data += chunk
                if not chunk or b'\x00' in chunk: break
            description = response_data.decode('utf-8').rstrip('\x00')
            return description
    except Exception as e:
        return None

if __name__ == "__main__":
    for k in tests.keys():
        cc, val = k
        rv = make_request(cc, val)
        status = 'FAIL' if rv != tests[k] else 'PASS'
        print(f'{status}: ({cc}, {val}) -> {rv}')

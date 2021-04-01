from argparse import ArgumentParser
import socket
from time import sleep
from pyaudio import PyAudio
from config import CONFIG
import logging


def client(host: str, port: int):
    END_LISTEN = False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        pa = PyAudio()
        stream = pa.open(
            format=CONFIG['FORMAT'],
            channels=CONFIG['CHANNELS'],
            rate=CONFIG['RATE'],
            input=True,
            frames_per_buffer=CONFIG['CHUNK']
        )
        
        try:
            sock.send(b'send_file')
            print(f"start recording...")
            logging.debug(f"Trying to send reccord to server.")

            while not END_LISTEN:
                try:
                    data = stream.read(CONFIG['CHUNK'])
                    sock.send(data)

                except KeyboardInterrupt:
                    print(f"\nStoping")
                    logging.debug(f"Trying to stop record.")
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    sock.send(b'end')
                    END_LISTEN = True
            
            logging.debug(f"Record has been sended.")

        except BrokenPipeError as e:
            logging.exception(e)

            stream.stop_stream()
            stream.close()
            pa.terminate()


def main(args):
    try:
        print(f"For exit press CTRL + C")
        logging.debug(f"Trying to connect server {args.host}:{args.port}")
        client(args.host, args.port)

    except ConnectionRefusedError:

        logging.error(f"Connection refused from server {args.host}:{args.port}")
        print(f"Sorry, i can't connect to server {args.host}:{args.port} =(")


if __name__ == '__main__':
    logging.basicConfig(
        filename='client.log', 
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    parser = ArgumentParser()

    parser.add_argument('--host', default='localhost', help='default value is localhost')
    parser.add_argument('--port', default=25000, help='default value is 25000')

    main(parser.parse_args())

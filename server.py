from argparse import ArgumentParser
from datetime import datetime as dt
from uuid import uuid4
from socketserver import BaseRequestHandler, TCPServer
import wave
from pyaudio import get_sample_size
from config import CONFIG
from os.path import isfile
from os import remove
import logging


class VoiceSaveServer(BaseRequestHandler):
    """Class for handle user voice stream.

    Every stream save to .wav file
    Filename format <uuid4>_<timestamp>.wav    
    """

    def handle(self):
        END = False
        msg = self.request.recv(CONFIG['CHUNK'])

        if msg == b'send_file':
            print(f"Listening stream...")
            timestamp = str(dt.now().timestamp())
            uniq_id = uuid4()
            uniq_filename = f"{uniq_id}_{timestamp}.wav"
            
            try:
                wf = self._get_wave_file(uniq_filename)
                logging.debug(f"Trying to save stream to {uniq_filename}")

                while not END:
                    data = self.request.recv(CONFIG['CHUNK'])
                    if data == b'end':
                        END = True
                    wf.writeframes(data)

            except wave.Error as e:
                logging.exception(e)
                if isfile(uniq_filename):
                    logging.debug(f"Trying to remove {uniq_filename}.")
                    remove(uniq_filename)
                    logging.debug(f"{uniq_filename} has been removed.")
            finally:
                wf.close()

            print(f"File {uniq_filename} has been saved.")
            logging.debug(f"File {uniq_filename} has been saved.")

    def _get_wave_file(self, filename: str):
        wf = wave.open(filename, mode='wb')
        wf.setnchannels(CONFIG['CHANNELS'])
        wf.setsampwidth(get_sample_size(CONFIG['FORMAT']))
        wf.setframerate(CONFIG['RATE'])

        return wf


def main(args):
    try:
        logging.debug(f"Server running on port: {args.port}")
        print(f"Server running on port: {args.port}")
        print(f"For exit press CTRL + C")
        
        with TCPServer((args.host, args.port), VoiceSaveServer) as server:
            server.serve_forever()

    except KeyboardInterrupt:
        logging.debug(f"user stoped server")
        print("\nBye!")

    except Exception as e:
        logging.exception(e)
        print(f"other unhandled exception: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        filename='server.log', 
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    parser = ArgumentParser()

    parser.add_argument('--host', default='localhost', help='default value is localhost')
    parser.add_argument('--port', default=25000, help='default value is 25000')

    main(parser.parse_args())
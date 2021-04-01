"""
Config file for 2 sides client and server
"""
from pyaudio import paInt16


CONFIG = {
    'CHUNK': 1024,
    'FORMAT': paInt16,
    'CHANNELS': 2,
    'RATE': 44100
}
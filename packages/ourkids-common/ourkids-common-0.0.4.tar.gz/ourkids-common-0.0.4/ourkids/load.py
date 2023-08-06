from dotenv import load_dotenv
from os.path import join

def load_env(place):
    dotenv_path = join(place, '../../.env')
    load_dotenv(dotenv_path) 
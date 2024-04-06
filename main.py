import os
from os.path import join, dirname
from dotenv import load_dotenv
import time

dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

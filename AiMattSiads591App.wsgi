#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/AiMattSiads591App/")

from AiMattSiads591App import server as application
application

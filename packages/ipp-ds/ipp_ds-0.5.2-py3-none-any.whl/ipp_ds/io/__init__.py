"""
Modulo de configuracao da lib de io
"""

import os
import json

CONTAINERS = json.loads(os.environ.get("CONTAINERS",'{}'))
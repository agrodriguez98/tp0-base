from configparser import ConfigParser
import os

config = ConfigParser(os.environ)
config.read("config.ini")
config_params = {}
try:
    config_params["ip"] = os.getenv('SERVER_IP', config["DEFAULT"]["SERVER_IP"])
    config_params["port"] = os.getenv('SERVER_PORT', config["DEFAULT"]["SERVER_PORT"])
except KeyError as e:
    raise KeyError("Key was not found. Error: {}".format(e))
except ValueError as e:
    raise ValueError("Key could not be parsed. Error: {}".format(e))

with open("ip_file", "w") as ip_file:
    ip_file.write(config_params["ip"])

with open("port_file", "w") as port_file:
    port_file.write(config_params["port"])

import datetime
import json
import time
import sys
import time
from paho.mqtt.publish import single as publish_single
from .calendar import seasons, ordinary, overrides


class Calculator(object):
    def __init__(self):
        self._overrides = {t.date: t.colour for t in overrides}

    def lookup(self, dt):
        if dt in self._overrides:
            return self._overrides[dt]
        return self.get_season(dt).colour

    def get_season(self, dt):
        for season in seasons:
            if dt >= season.start and dt <= season.end:
                return season
        return ordinary


def get_config():
    with open("./config/fristad.json") as fd:
        return json.load(fd)


def cli():
    conf = get_config()
    calc = Calculator()
    current = None

    def hex2rgb(hex):
        r, g, b = tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
        return {"r": r, "g": g, "b": b}

    while True:
        today = datetime.datetime.today().date()
        colour = calc.lookup(today)
        if colour != current:
            print("set colour:", colour, file=sys.stderr)
            payload = {"state": "ON", "color": hex2rgb(colour)}
            publish_single(
                conf["topic"], json.dumps(payload), hostname=conf["hostname"]
            )
        time.sleep((60 - time.time() % 60) + 0.5)

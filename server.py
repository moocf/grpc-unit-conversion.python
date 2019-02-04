from concurrent import futures
import time
import grpc
import unit_pb2
import unit_pb2_grpc


ABBREVIATION_PREFIX = {
  "yocto": "y",
  "zepto": "z",
  "atto": "a",
  "femto": "f",
  "pico": "p",
  "nano": "n",
  "micro": "u",
  "milli": "m",
  "centi": "c",
  "deci": "d",
  "deca": "da",
  "hecto": "h",
  "kilo": "k",
  "mega": "M",
  "giga": "G",
  "tera": "T",
  "peta": "P",
  "exa": "E",
  "zetta": "Z",
  "yotta": "Y"
}

ABBREVIATION = {
  # length
  "metre": "m",
  "meter": "m",
  "inch": "in",
  "feet": "ft",
  "foot": "ft",
  "yard": "yd",
  "mile": "mi",
  # mass
  "gramme": "g",
  "gram": "g",
  "gm": "g",
  "quintal": "q",
  "tonne": "t",
  "ton": "t",
  "carat": "ct",
  "ounce": "oz",
  "pound": "lb",
  # time
  "second": "s",
  "minute": "min",
  "hour": "hr",
  "day": "dy",
  "week" : "wk",
  "month": "mo",
  "year" :"yr",
}

LENGTH = {
  "fm": 1e-15,
  "pm": 1e-12,
  "nm": 1e-9,
  "um": 1e-6,
  "mm": 1e-3,
  "cm": 1e-2,
  "dm": 1e-1,
  "m": 1,
  "dam": 1e+1,
  "hm": 1e+2,
  "km": 1e+3,
  "in": 0.0254,
  "ft": 0.31622776602,
  "yd": 0.9144,
  "mi": 1609.344
}

MASS = {
  "fg": 1e-15,
  "pg": 1e-12,
  "ng": 1e-9,
  "ug": 1e-6,
  "mg": 1e-3,
  "g": 1,
  "kg": 1e+3,
  "q": 1e+5,
  "t": 1e+6,
  "ct": 0.2,
  "oz": 28,
  "lb": 453.59237
}

TIME = {
  "fs": 1e-15,
  "ps": 1e-12,
  "ns": 1e-9,
  "us": 1e-6,
  "ms": 1e-3,
  "s": 1,
  "min": 60,
  "hr": 3.6e+3,
  "dy": 86.4e+3,
  "wk": 604.8e+3,
  "mo": 2.6297e+6,
  "yr": 31.556925e+6,
}


def abbreviation_prefix(name):
  for full,abbr in ABBREVIATION_PREFIX:
    i = name.find(full)
    i = i if i>=0 else name.lower().find(full)
    if i>=0:
      return abbr,name[:i]+name[i+len(full):]
  return "",name

def abbreviation(name):
  prefix,name = abbreviation_prefix(name)
  if name in ABBREVIATION:
    return prefix+ABBREVIATION[name]
  name = name.lower()
  if name in ABBREVIATION:
    return prefix+ABBREVIATION[name]
  name = name[:-2] if name[-2:]=="is" else name
  name = name[:-1] if name[-1:]=="s" else name
  if name in ABBREVIATION:
    return prefix+ABBREVIATION[name]
  return prefix+name

def unit_map(name):
  if name in LENGTH:
    return LENGTH
  if name in MASS:
    return MASS
  if name in TIME:
    return TIME
  return None

def unit_convert(value, source, target):
  source_abbr = abbreviation(source)
  target_abbr = abbreviation(target)
  source_map = unit_map(source_abbr)
  target_map = unit_map(target_abbr)
  if source_map is None:
    return "Unknown unit "+source+"!",0
  if target_map is None:
    return "Unknown unit "+target+"!",0
  if source_map != target_map:
    return source+" and "+target+" are different physical quantities!",0
  return "",value*source_map[source_abbr]/source_map[target_abbr]

class Unit(unit_pb2_grpc.UnitServicer):
  def Convert(self, request, context):
    error,value = unit_convert(request.value, request.souce, request.target)
    return unit_pb2.ConvertReply(error=error, value=value)


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
unit_pb2_grpc.add_UnitServicer_to_server(Unit(), server)
server.add_insecure_port('[::]:50051')
server.start()
try:
    while True:
        time.sleep(1000)
except KeyboardInterrupt:
    server.stop(0)

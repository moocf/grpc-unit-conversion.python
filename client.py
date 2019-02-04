import grpc
import unit_pb2
import unit_pb2_grpc
import sys
import optparse


parser = optparse.OptionParser()
parser.set_defaults(server="localhost:50051")
parser.add_option("--server", dest="server", help="Set server address")
parser.usage = "python client.py <value> <source unit> <target unit> [--server <address>]"
(options, args) = parser.parse_args()

if len(args)<3:
  parser.print_help()
  sys.exit()

address = options.server
value,source,target = (float(args[0]),args[1],args[2])
with grpc.insecure_channel(address) as channel:
  stub = unit_pb2_grpc.UnitStub(channel)
  response = stub.Convert(unit_pb2.ConvertRequest(value=value,source=source,target=target))
if response.error=="":
  print(str(value)+" "+source+" = "+str(response.value)+" "+target)
else:
  print(response.error)

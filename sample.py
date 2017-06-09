from pprint import pprint

import pythonvault.net as pv
import pythonvault.enums as pve
import pythonvault.types as pvt

def connect():
    v = pv.Client('10.252.2.115')
    msg = pv.encode(pve.Procedure.discoverControllers)
    v.send_message(msg)
    r = v.receive_message()
    pprint(r)
    pprint(pv.decode(r, pvt.DiscoveryResponse()))

def encode():
    msg = pv.encode(pve.Procedure.discoverControllers)
    pprint(msg)

def decode():
    hex = "591cb140000000000000000253594d420000000100000006000000000000000000000000000000000000003400000004000000030000000700000006000000000000000100000002000000000000000c00000002000000040000ffff00000001"
    msg = bytes(int(a + b, 16) for a, b in zip(hex[0::2], hex[1::2]))
    pprint(pv.decode(msg))

decode()

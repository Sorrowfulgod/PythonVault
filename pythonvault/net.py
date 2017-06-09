import socket
import struct
import time
import xdrlib

from .enums import *

class Client:
    def __init__(self, ip, port=2463):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

    def __enter__(self):
        return self

    def __exit__(self):
        if self.socket:
            self.socket.close()
    
    def send_message(self, msg):
        if type(msg) is bytes:
            buffers = [msg]
        else:
            buffers = msg

        total_size = sum(len(m) for m in buffers)
        sent = 0
        nextBuff = 0

        while sent < total_size:
            data = buffers[nextBuff]
            nextBuff += 1
            will_send = min(len(data), total_size - sent)
            length_code = will_send
            if sent + will_send >= total_size:
                length_code |= 0x80000000
            header = struct.pack('>I', length_code)

            self.socket.send(header)
            self.socket.send(data)
            sent += will_send

    def receive_message(self):
        done = False
        buffers = []
        while not done:
            header = self.socket.recv(4)
            length_code = struct.unpack('>I', header)[0]

            will_receive = length_code & 0x7FFFFFFF
            if will_receive != 0:
                data = self.socket.recv(will_receive)
                buffers.append(data)
            done = (length_code & 0x80000000) != 0
        #pprint(buffers)
        #print("There were {0} buffers".format(len(buffers)))
        return b''.join(buffers)

def decode(msg, argument = None):
    u = xdrlib.Unpacker(msg)
    
    xid = u.unpack_uint()
    #print('XID: {0}'.format(xid))

    msg_type = MessageType(u.unpack_uint())
    #print('MSG_TYPE: {0}'.format(msg_type))

    if msg_type == MessageType.CALL:
        rpc_version = u.unpack_uint()
        program_no = u.unpack_uint()
        version_no = u.unpack_uint()
        procedure = Procedure(u.unpack_uint())

        # Credential
        cred_type = CredentialType(u.unpack_uint())
        cred_data = u.unpack_opaque()

        # Verifier
        verif_type = CredentialType(u.unpack_uint())
        verif_data = u.unpack_opaque()

        if argument:
            arg = argument.unpack(u)

    elif msg_type == MessageType.REPLY:
        reply_status = ReplyStatus(u.unpack_uint())
        print('Reply status:', reply_status)
        if reply_status == ReplyStatus.MSG_ACCEPTED:
            # Verifier
            verif_type = CredentialType(u.unpack_uint())
            verif_data = u.unpack_opaque()

            # Body
            accepted_status = AcceptedStatus(u.unpack_uint())
            if accepted_status == AcceptedStatus.PROG_MISMATCH:
                low_version = u.unpack_uint()
                high_version = u.unpack_uint()

            ret = argument.unpack(u)

        elif reply_status == ReplyStatus.MSG_REJECTED:
            pass
        else: # Error
            raise ValueError('Unknown reply type')
    else: # Error
        raise ValueError('Unknown message type')

    return locals()


def encode(procedure, argument = None):
    p = xdrlib.Packer()
    
    xid = int(time.time())
    p.pack_uint(xid)

    msg_type = MessageType.CALL
    p.pack_uint(msg_type.value)

    if msg_type == MessageType.CALL:
        rpcVersion = 2
        programNo = 1398361410
        versionNo = 1

        p.pack_uint(rpcVersion)
        p.pack_uint(programNo)
        p.pack_uint(versionNo)
        p.pack_uint(procedure.value)

        # Credential
        p.pack_uint(CredentialType.AUTH_NONE.value)
        p.pack_opaque(b'')

        # Verifier
        p.pack_uint(CredentialType.AUTH_NONE.value)
        p.pack_opaque(b'')

        if argument:
            argument.pack(p)
    elif msg_type == MessageType.REPLY:
        reply_status = ReplyStatus.MSG_ACCEPTED
        if reply_status == ReplyStatus.MSG_ACCEPTED:
            # Verifier
            p.pack_uint(CredentialType.AUTH_NON.valueE)
            p.pack_opaque(b'')

            # Body
            accepted_status = AcceptedStatus.SUCCESS
            p.pack_uint(accepted_status.value)

            if accepted_status == AcceptedStatus.PROG_MISMATCH:
                low_version = 1
                high_version = 2
                p.pack_uint(low_version)
                p.pack_uint(high_version)
    return p.get_buffer()

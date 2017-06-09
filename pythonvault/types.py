import xdrlib

class Printable:
    def __repr__(self):
        return self.__class__.__name__ + '|' + repr(self.__dict__)

class Argument(Printable):
    def pack(self, p):
        raise NotImplementedError()

    def unpack(self, u):
        raise NotImplementedError()

class ControllerDescriptor(Argument):
    def unpack(self, u):
        self.token = u.unpack_fopaque(12)
        self.wwn = u.unpack_opaque()

class AccessibleController(Printable):
    trayId = None
    slot = None
    wwn = None
    token = None
    controller_refs = None

class DiscoveryResponse(Argument):
    def unpack(self, u: xdrlib.Unpacker):
        self.response_from_agent = u.unpack_bool()
        self.agent_id = u.unpack_opaque()
        
        n = u.unpack_uint()
        self.controllers = []
        for i in range(n):
            c = AccessibleController()
            c.trayId = u.unpack_uint()
            c.slot = u.unpack_uint()
            c.wwn = u.unpack_opaque()
            c.token = u.unpack_fopaque(12)
            c.controller_refs = []

            m = u.unpack_uint()
            for j in range(m):
                c.controller_refs.append(u.unpack_fopaque(12))
            
            self.controllers.append(c)

#####
class SAData(Argument):
    def unpack(self, u: xdrlib.Unpacker):
        self.needs_attention = u.unpack_bool()
        self.fixing = u.unpack_bool()
        self.wwn = u.unpack_opaque()
        self.management_class_name = u.unpack_string()
        self.storage_array_label = u.unpack_string().decode('utf-16be')
        self.boot_time = struct.unpack('>Q', u.unpack_fopaque(8))[0]
        self.fw_version = u.unpack_fopaque(4)
        self.app_version = u.unpack_fopaque(4)
        self.boot_version = u.unpack_fopaque(4)
        self.nvsram_version = u.unpack_string()
        self.fw_prefix = u.unpack_string()
        self.chassis_serial_number = u.unpack_string()
        self.event_configuration_data_version = u.unpack_string()
        
        self.array_attributes = []
        nb = u.unpack_uint()
        for i in range(nb):
            self.array_attributes.append(u.unpack_uint())
        self.res4 = []
        nb = u.unpack_uint()
        for i in range(nb):
            self.res4.append(u.unpack_uint())
        self.res5 = []
        nb = u.unpack_uint()
        for i in range(nb):
            self.res5.append(u.unpack_uint())
        self.res6 = []
        nb = u.unpack_uint()
        for i in range(nb):
            self.res6.append(u.unpack_uint())
        self.res7 = u.unpack_opaque()

        last = u.unpack_int()
        if last > 0:
            this.reserved1 = u.get_opaque()
            u.set_position(u.get_position() + last)

class ControllerTime(Argument):
    def unpack(self, u: xdrlib.Unpacker):
        last = u.unpack_uint() + u.get_position()
        if u.get_position() < last:
            self.time_A = struct.unpack('>Q', u.unpack_fopaque(8))[0]
        if u.get_position() < last:
            self.time_B = struct.unpack('>Q', u.unpack_fopaque(8))[0]
        u.set_position(last)

class SAViewPasswordDigest(Argument):
    def unpack(self, u: xdrlib.Unpacker):
        last = u.unpack_uint() + u.get_position()
        ret = ReturnCode.unpack(u)

        if ret == ReturnCode.OK:
            last2 = u.unpack_uint() + u.get_position()
            if u.get_position() < last2:
                self.digest = u.unpack_fopaque(20)
            if u.get_position() < last2:
                self.salt = u.unpack_fopaque(8)
            u.set_position(last2)
        u.set_position(last)

class VolumeCandidateRequest(Argument):
    def unpack(self, u: xdrlib.Unpacker):
        last = u.unpack_uint() + u.get_position()
        if u.get_position() < last:
            last2 = u.unpack_uint()
            self.canditate_selection_type = CandidateSelectionType(u.unpack_uint())
            if self.canditate_selection_type == CandidateSelectionType.CANDIDATE_SEL_MANUAL:
                last3 = u.unpack_uint() + u.get_position()
                if u.get_position() < last3:
                    nb = u.unpack_uint()
                    self.drive_refs = []
                    for i in range(nb):
                        self.drive_refs.append(u.unpack_fopaque(20))
                u.set_position(last3)
            u.set_position(last2)
        
        if u.get_position() < last:
            self.raid_level = RaidLevel(u.unpack_int())
        if u.get_position() < last:
            self.phyiscal_drive_type = PhysicalDriveType(u.unpack_int())

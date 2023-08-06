from frotech_adapter.utils import adapter_modbus_config_t, adapter_modbus_bit_t, get_crc, MODBUS_SLAVE_ADDR, BAUDRATE, PORT, Communicator
import modbus_tk.defines as cst
import atexit

__all__ = ['SerialServo', 'LIMIT_RANGE']

_id_map = {
    "up": (
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_UP_SERVO_ANGLE,
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_UP_SERVO_TIME,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_UP_SERVO_RELEASE,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_UP_SERVO_LOCK,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_READ_UP_ANGLE,
        (1365, 2458),
    ),
    "down": (
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_DOWN_SERVO_ANGLE,
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_DOWN_SERVO_TIME,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_DOWN_SERVO_RELEASE,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_DOWN_SERVO_LOCK,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_READ_DOWN_ANGLE,
        (1638, 2458),
    ),
    "left": (
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LEFT_SERVO_ANGLE,
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LEFT_SERVO_TIME,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_LEFT_SERVO_RELEASE,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_LEFT_SERVO_LOCK,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_READ_LEFT_ANGLE,
        (548, 2048),
    ),
    "right": (
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_RIGHT_SERVO_ANGLE,
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_RIGHT_SERVO_TIME,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_RIGHT_SERVO_RELEASE,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_RIGHT_SERVO_LOCK,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_READ_RIGHT_ANGLE,
        (548, 2048),
    ),
    "all": (
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_ALL_SERVO_ANGLE,
        adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_ALL_SERVO_TIME,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_ALL_SERVO_RELEASE,
        adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_ALL_SERVO_LOCK,
    ),
}


def clamp(value, lower, upper):
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


LIMIT_RANGE = {
    "up": (1365, 2458),  # 40-120度
    "down": (1638, 2458),  # 60-120度
    "left": (548, 2048),
    "right": (548, 2048),
}


class SerialServo(object):
    def __init__(self,
                 id,
                 limit=True,
                 limit_range=None,
                 port=PORT,
                 baudrate=BAUDRATE):
        super().__init__()
        if id not in list(_id_map):
            raise ValueError(f'id must be one of the {list(_id_map)}')

        self._id = id
        self._pos_addr = _id_map[id][0]
        self._time_addr = _id_map[id][1]
        self._release_bit = _id_map[id][2]
        self._lock_bit = _id_map[id][3]
        self.limit_range = limit_range
        if id != 'all':
            self._read_pos_bit = _id_map[id][4]
            if limit_range is None:
                self.limit_range = LIMIT_RANGE[id]
            else:
                self.limit_range = limit_range
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        self.read_position()
        self.limit = limit
        if id == "all":
            self.position = 0xffff
        atexit.register(self.release)

    def read_position(self):
        if self._id != "all":
            try:
                self._master.execute(MODBUS_SLAVE_ADDR,
                                     cst.WRITE_SINGLE_COIL,
                                     self._read_pos_bit,
                                     output_value=1)
                self._pos, = self._master.execute(MODBUS_SLAVE_ADDR,
                                                  cst.READ_HOLDING_REGISTERS,
                                                  self._pos_addr, 1)
            except:
                self._pos = 0xffff
        else:
            self._pos = 2000  # 随意定的
        return self._pos

    @property
    def angle(self):
        # angle:0--pos:819.5; angle:90--pos:2048
        return (self._pos - 819.5) / 1228.5 * 90

    @angle.setter
    def angle(self, value):
        value = float(value)
        value = clamp(value, 0, 180)
        self.position = value * 1228.5 / 90 + 819.5

    def set_angle(self, value, retry=5):
        value = float(value)
        self.set_pos(value * 1228.5 / 90 + 819.5, retry)

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, value):
        value = int(value)
        if self.limit and self.limit_range is not None:
            if value != 0xffff:
                value = clamp(value, self.limit_range[0], self.limit_range[1])
        self._pos = value
        try:
            self._master.execute(MODBUS_SLAVE_ADDR,
                                 cst.WRITE_SINGLE_REGISTER,
                                 self._pos_addr,
                                 output_value=self._pos)
        except:
            pass

    @property
    def run_time(self):
        try:
            ret, = self._master.execute(MODBUS_SLAVE_ADDR,
                                        cst.READ_HOLDING_REGISTERS,
                                        self._time_addr, 1)
        except:
            return
        return ret

    def set_pos(self, value, retry=0):
        value = int(value)
        if self.limit and self.limit_range is not None:
            if value != 0xffff:
                value = clamp(value, self.limit_range[0], self.limit_range[1])
        for _ in range(retry + 1):
            try:
                self._master.execute(MODBUS_SLAVE_ADDR,
                                     cst.WRITE_SINGLE_REGISTER,
                                     self._pos_addr,
                                     output_value=value)
            except:
                pass
            else:
                self._pos = value
                return True
        return False

    @run_time.setter
    def run_time(self, value):
        value = int(value)
        if value > 0xffff:
            value = 0xffff
        if value < 0:
            value = 0
        try:
            self._master.execute(MODBUS_SLAVE_ADDR,
                                 cst.WRITE_SINGLE_REGISTER,
                                 self._time_addr,
                                 output_value=value)
        except:
            pass

    def lock(self):
        try:
            self._master.execute(MODBUS_SLAVE_ADDR,
                                 cst.WRITE_SINGLE_COIL,
                                 self._lock_bit,
                                 output_value=1)
            return True
        except:
            return False

    def release(self, retry=5):
        for _ in range(retry + 1):
            try:
                self._master.execute(MODBUS_SLAVE_ADDR,
                                     cst.WRITE_SINGLE_COIL,
                                     self._release_bit,
                                     output_value=1)
            except:
                pass
            else:
                self.position = 0xffff
                return True
        return False

    def _set_id(self, new, old=0):
        new = int(new) & 0xff
        old = int(old) & 0xff
        if new == 0:
            raise ValueError('can not set id to 0')
        id_addr = adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_OLD_NEW_ID
        pdu = bytearray([MODBUS_SLAVE_ADDR, cst.WRITE_SINGLE_REGISTER]) + \
            bytearray([0, id_addr, old, new])
        cmd = pdu + get_crc(pdu)
        self._master._serial.write(cmd)
        id_bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_SERVO_SET_ID
        try:
            self._master.execute(MODBUS_SLAVE_ADDR,
                                 cst.WRITE_SINGLE_COIL,
                                 id_bit,
                                 output_value=1)
            return True
        except:
            return False

    def _auto_set_middle_offset(self):
        if self._id == 'all':
            return
        if self._id == 'up':
            id_bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_AUTO_SET_MID_UP_SERVO
        if self._id == 'down':
            id_bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_AUTO_SET_MID_DOWN_SERVO
        if self._id == 'left':
            id_bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_AUTO_SET_MID_LEFT_SERVO
        if self._id == 'right':
            id_bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_AUTO_SET_MID_RIGHT_SERVO
        try:
            self._master.execute(MODBUS_SLAVE_ADDR,
                                 cst.WRITE_SINGLE_COIL,
                                 id_bit,
                                 output_value=1)
            return True
        except:
            return False

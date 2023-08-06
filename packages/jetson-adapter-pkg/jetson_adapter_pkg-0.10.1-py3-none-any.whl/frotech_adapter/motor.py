import atexit
import traitlets
from .utils import get_crc, MODBUS_SLAVE_ADDR, PORT, BAUDRATE, Communicator, adapter_modbus_config_t
import modbus_tk.defines as cst
import logging


class Motor(object):
    """电机驱动

    Parameters
    ----------
    id : string
        只能为"left"或"right"，分别代表左右电机。

    Examples
    --------
    >>> left_motor = Motor("left") # 小车左侧电机
    >>> right_motor = Motor("right") # 小车右侧电机

    >>> left_motor.throttle = 4096 # 左电机正向转动，速度最大
    >>> right_motor.throttle = -4096 # 右电机反向转动，速度最大

    >>> left_motor.throttle = 0 # 左电机停止转动（自由停止）
    >>> right_motor.throttle = None # 右电机停止转动（紧急停止）
    """
    value = traitlets.Integer()

    def __init__(self, id, port=PORT, baudrate=BAUDRATE):
        if id not in ("left", "right"):
            raise ValueError('id must be "left" or "right"')
        if id == "left":
            id = adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LEFT_MOTOR_SPEED
        else:
            id = adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_RIGHT_MOTOR_SPEED
        self.__id = id
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        self.__speed = 0
        self.throttle = 0xffff
        atexit.register(self._release)

    @property
    def throttle(self):
        """
        int:
            电机速度，范围[-4096, 4096]，正数代表正向转动，
            负数代表反向转动，电机速度为0代表自由停止

        NoneType:
            当输入为None时，电机强制停止
        """
        return self.__speed

    @throttle.setter
    def throttle(self, value):
        if value is None:
            value = 0xffff
        value = int(value)
        if value != 0 and value != 0xffff:
            self.__speed = value
            pdu = bytearray([
                MODBUS_SLAVE_ADDR, cst.WRITE_SINGLE_REGISTER, 0, self.__id,
                (self.__speed >> 8) & 0xff, self.__speed & 0xff
            ])
            cmd = pdu + get_crc(pdu)
            self._master._serial.write(cmd)
        else:
            for _ in range(5):
                try:
                    self._master.execute(MODBUS_SLAVE_ADDR,
                                         cst.WRITE_SINGLE_REGISTER,
                                         self.__id,
                                         output_value=value)
                except:
                    pass
                else:
                    break

    def _release(self):
        self.throttle = 0

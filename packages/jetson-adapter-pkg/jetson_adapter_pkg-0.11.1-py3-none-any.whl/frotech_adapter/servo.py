from .utils import get_crc, MODBUS_SLAVE_ADDR, PORT, Communicator, Logger
import modbus_tk.defines as cst
from traitlets.config.configurable import SingletonConfigurable
import traitlets

SERVO_ON = 0
SERVO_UP_ANGLE = 1
SERVO_DOWN_ANGLE = 2
BAUDRATE = 460800


class Servo(Logger):
    """舵机驱动

    Attributes
    ----------
    limit: bool
        True: 开启角度限制；False: 关闭角度限制

    limit_range: tuple(int, int)
        记`limit_range`的值为(min,max)，且0<=min<=max<=180，则当传入的舵机角度angle<min时，angle=min；
        当传入的angle>max，angle=max。
        当`limit`为`False`时，该值无效。

    Parameters
    ----------
    id : int
        只能为整数1或2，1代表云台上面的舵机，2代表云台下面的舵机

    """

    def __init__(self,
                 id,
                 limit=True,
                 limit_range=None,
                 port=PORT,
                 baudrate=BAUDRATE):
        super().__init__()
        if id not in (1, 2):
            raise ValueError('id must be 1 or 2')
        self.__id = id
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        try:
            (self.__angle, ) = self._master.execute(MODBUS_SLAVE_ADDR,
                                                    cst.READ_HOLDING_REGISTERS,
                                                    id, 1)
        except:
            self.__angle = None
            self.logger.error(
                'Failed to read servo angle, please check your connection between host and adapter'
            )
        self.limit = limit
        if limit:
            if not limit_range:
                if id == 1:
                    self.limit_range = (0, 60)
                if id == 2:
                    self.limit_range = (50, 130)
            else:
                self.limit_range = limit_range
        else:
            self.limit_range = (0, 180)

    @property
    def angle(self):
        """
        int:
            舵机角度，取值范围[0,180]。实际角度会受 :py:attr:`limit` 和
            :py:attr:`limit_range` 影响。
            当 :py:attr:`limit` 为`True`，且 :py:attr:`limit_range` 范围小于[0,180]，
            则舵机实际输出角度会在 :py:attr:`limit_range` 范围内。

        """
        # 从转接板读取一次信息，约10ms，为提高运行速度，直接返回__angle
        return self.__angle

    @angle.setter
    def angle(self, value):
        value = int(value)

        if value > self.limit_range[1]:
            value = self.limit_range[1]
        if value < self.limit_range[0]:
            value = self.limit_range[0]
        self.__angle = value
        pdu = bytearray([MODBUS_SLAVE_ADDR, cst.WRITE_SINGLE_REGISTER]) + \
            bytearray([0, self.__id, 0, self.__angle])
        cmd = pdu + get_crc(pdu)
        try:
            self._master._serial.write(cmd)
        except:
            self.logger.error(
                'Failed to write servo angle, please check your connection between host and adapter'
            )

    @property
    def enable(self):
        (on_off, ) = self._master.execute(MODBUS_SLAVE_ADDR,
                                          cst.READ_HOLDING_REGISTERS, SERVO_ON,
                                          1)
        return on_off

    @enable.setter
    def enable(self, value):
        value = int(value)
        self._master.execute(MODBUS_SLAVE_ADDR,
                             cst.WRITE_SINGLE_REGISTER,
                             SERVO_ON,
                             output_value=value)


class PanTilt(SingletonConfigurable):

    up_servo = traitlets.Instance(Servo)
    down_servo = traitlets.Instance(Servo)

    def __init__(self, port=PORT, baudrate=BAUDRATE, **kwargs):
        super().__init__(**kwargs)
        self.up_servo = Servo(1, limit=False, port=port, baudrate=baudrate)
        self.down_servo = Servo(2, limit=False)
        self.up_servo.enable = 1

    def enable(self):
        self.up_servo.enable = 1

    def disable(self):
        self.up_servo.enable = 0

    def set_pos(self, v_pos=None, h_pos=None):
        """控制云台的舵机转到特定的角度

        Parameters
        ----------
        v_pos : float
            上舵机的角度，取值范围[0, 180]。

        h_pos : float
            下舵机的角度，取值范围[0, 180]。

        Note
        ----
        若设置的角度超出舵机的角度限制范围，则舵机只转到角度限制值。
        """
        if v_pos is not None:
            self.up_servo.angle = v_pos
        if h_pos is not None:
            self.down_servo.angle = h_pos

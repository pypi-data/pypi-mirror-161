from enum import Enum
from .utils import get_crc, MODBUS_SLAVE_ADDR, PORT, Communicator
import modbus_tk.defines as cst

PIE_LEFT_TIMEOUT = 3
PIE_RIGHT_TIMEOUT = 4
BAUDRATE = 460800


class Piece(object):

    def __init__(self, id, port=PORT, baudrate=BAUDRATE):
        if id not in (3, 4):
            raise ValueError('id must be 3 or 4')
        self.__id = id
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        self.__state = self.get_switch_state()
        (self.__timeout, ) = self._master.execute(MODBUS_SLAVE_ADDR,
                                                  cst.READ_HOLDING_REGISTERS,
                                                  id, 1)

    @property
    def state(self):
        self.__state = self.get_switch_state()
        return self.__state

    def act(self, value):
        if value == "auto":
            tmp = 3
        elif value == "block":
            tmp = 1
        elif value == "pass":
            tmp = 2
        else:
            raise ValueError('值只能为 "auto", "block" 或 "pass"')
        base = (self.__id - 3) * (self.__id - 2)
        pdu = bytearray([MODBUS_SLAVE_ADDR, cst.WRITE_MULTIPLE_COILS]) + \
            bytearray([0, base, 0, 2, 1, tmp])
        cmd = pdu + get_crc(pdu)
        self._master._serial.write(cmd)

    @property
    def timeout(self):
        (self.__timeout, ) = self._master.execute(MODBUS_SLAVE_ADDR,
                                                  cst.READ_HOLDING_REGISTERS,
                                                  self.__id, 1)
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        if value < 2000 or value > 10000:
            raise ValueError('timeout must between 2000~10000')
        self.__timeout = value
        self._master.execute(MODBUS_SLAVE_ADDR,
                             cst.WRITE_SINGLE_REGISTER,
                             self.__id,
                             output_value=self.__timeout)

    def get_switch_state(self):
        # 线圈4-8位依次代表左上，左下，右上，右下的限位开关状态
        unblock, block = self._master.execute(MODBUS_SLAVE_ADDR,
                                              cst.READ_COILS, (self.__id - 3) *
                                              (self.__id - 2) + 4, 2)
        return unblock, block


class BlockPiece():

    def __init__(self, port=PORT, baudrate=BAUDRATE) -> None:
        self.pf = Piece(3, port=port, baudrate=baudrate)
        self.pb = Piece(4)

    def act(self, action, piece='right'):
        """执行拨片动作

        Args:
            action (str): 可选的动作为: 
                "block" - 拨片打开；
                "pass" - 拨片收回；
                "auto" - 拨片自动打开，经过一段时间后自动拨回，该时间可通过 `set_timeout` 设置。
            piece (str, optional): 选择要执行动作的拨片。可选值为 "back"/"right" 和 "front"/"left"。
                 默认是 "right"。
        """
        if piece == 'back' or piece == 'right':
            self.pb.act(action)
        elif piece == 'front' or piece == 'left':
            self.pf.act(action)

    def set_timeout(self, timeout, piece='right'):
        """设置动作超时时间，该动作是指 `BlockPiece.act('auto')`。

        Args:
            timeout (int): 范围在2000-10000，单位 ms。
            piece (str, optional): 选择要设置超时的拨片。可选值为 "back"/"right" 和 "front"/"left"。
                 默认是 "right"。
        """
        if piece == 'back' or piece == 'right':
            self.pb.timeout = int(timeout)
        elif piece == 'front' or piece == 'left':
            self.pf.timeout = int(timeout)

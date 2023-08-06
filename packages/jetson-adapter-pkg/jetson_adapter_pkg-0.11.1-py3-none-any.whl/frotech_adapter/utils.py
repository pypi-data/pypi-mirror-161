from enum import IntEnum, auto
import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import crcmod
from traitlets.config.configurable import SingletonConfigurable
import logging

PORT = '/dev/ttyTHS1'
MODBUS_SLAVE_ADDR = 14
BAUDRATE = 230400


class Logger(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_logger(self, name='console', level='debug', record_format=None):
        if record_format is None:
            record_format = '[%(levelname)s] %(asctime)s - %(name)s - %(funcName)s - %(message)s'

        level = level.upper()
        if level not in [
                'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ]:
            raise ValueError(f'Unknow logging level: {level}')

        self.logger.setLevel(eval('logging.' + level))
        formatter = logging.Formatter(record_format)
        if name == 'console':
            ch = logging.StreamHandler()
        elif name == 'dummy':
            ch = logging.NullHandler()
        elif name[-4:] == '.log':
            ch = logging.FileHandler(name, encoding='utf-8')
        else:
            raise Exception(f"Unknown handler: {name}")
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        return self.logger


class Communicator(SingletonConfigurable, Logger):
    def __init__(self, port=PORT, baudrate=BAUDRATE, *args, **kwargs):
        super(Communicator, self).__init__(*args, **kwargs)
        try:
            self.master = modbus_rtu.RtuMaster(
                serial.Serial(port=port,
                              baudrate=baudrate,
                              bytesize=8,
                              parity='N',
                              stopbits=1,
                              xonxoff=0))
            self.master.set_timeout(1.0)
        except:
            self.master = None
            self.logger.error('create Communicator failed!')


crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xffff, xorOut=0x0000)


def get_crc(pdu):
    word_val = crc16(pdu)
    msb = (word_val >> 8) & 0xFF
    lsb = word_val & 0xFF
    return bytearray([lsb, msb])


class adapter_modbus_config_t(IntEnum):
    ADAPTER_MODBUS_CONFIG_LEFT_PIE_TIMEOUT = 0
    ADAPTER_MODBUS_CONFIG_RIGHT_PIE_TIMEOUT = auto()
    ADAPTER_MODBUS_CONFIG_LEFT_MOTOR_SPEED = auto()
    ADAPTER_MODBUS_CONFIG_RIGHT_MOTOR_SPEED = auto()
    ADAPTER_MODBUS_CONFIG_LED_MODE = auto()
    ADAPTER_MODBUS_CONFIG_LED1_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED1_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED2_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED2_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED3_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED3_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED4_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED4_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED5_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED5_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED6_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED6_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED7_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED7_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED8_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED8_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED9_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED9_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED10_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED10_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED11_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED11_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED12_COLOR_HIGH = auto()
    ADAPTER_MODBUS_CONFIG_LED12_COLOR_LOW = auto()
    ADAPTER_MODBUS_CONFIG_LED_ENABLE = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_MODE = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_PATTERN = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG1 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG2 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG3 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG4 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG5 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG6 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG7 = auto()
    ADAPTER_MODBUS_CONFIG_MATRIX_SEG8 = auto()
    ADAPTER_MODBUS_POWER_DETECT_BUF = auto()
    ADAPTER_MODBUS_CONFIG_ALL_SERVO_ANGLE = auto()
    ADAPTER_MODBUS_CONFIG_UP_SERVO_ANGLE = auto()
    ADAPTER_MODBUS_CONFIG_DOWN_SERVO_ANGLE = auto()
    ADAPTER_MODBUS_CONFIG_LEFT_SERVO_ANGLE = auto()
    ADAPTER_MODBUS_CONFIG_RIGHT_SERVO_ANGLE = auto()
    ADAPTER_MODBUS_CONFIG_ALL_SERVO_TIME = auto()
    ADAPTER_MODBUS_CONFIG_UP_SERVO_TIME = auto()
    ADAPTER_MODBUS_CONFIG_DOWN_SERVO_TIME = auto()
    ADAPTER_MODBUS_CONFIG_LEFT_SERVO_TIME = auto()
    ADAPTER_MODBUS_CONFIG_RIGHT_SERVO_TIME = auto()
    ADAPTER_MODBUS_CONFIG_OLD_NEW_ID = auto()
    ADAPTER_MODBUS_CONFIG_LIFT_TIMEOUT = auto()


class adapter_modbus_bit_t(IntEnum):
    ADAPTER_MODBUS_BIT_LEFT_BLOCK = 0  # combine block and pass bit, 10(block:1, pass:0): do block;
    ADAPTER_MODBUS_BIT_LEFT_PASS = auto()  # 01: do pass; 11: auto
    ADAPTER_MODBUS_BIT_RIGHT_BLOCK = auto()
    ADAPTER_MODBUS_BIT_RIGHT_PASS = auto()
    # /* 限位开关状态 */
    ADAPTER_MODBUS_BIT_LEFT_UP = auto()
    ADAPTER_MODBUS_BIT_LEFT_DOWN = auto()
    ADAPTER_MODBUS_BIT_RIGHT_UP = auto()
    ADAPTER_MODBUS_BIT_RIGHT_DOWN = auto()
    # /* LED标记 */
    ADAPTER_MODBUS_BIT_UPDATE_LED = auto()
    # /* 串口舵机释放/锁定标记 */
    ADAPTER_MODBUS_BIT_ALL_SERVO_RELEASE = auto()
    ADAPTER_MODBUS_BIT_ALL_SERVO_LOCK = auto()
    ADAPTER_MODBUS_BIT_UP_SERVO_RELEASE = auto()
    ADAPTER_MODBUS_BIT_UP_SERVO_LOCK = auto()
    ADAPTER_MODBUS_BIT_DOWN_SERVO_RELEASE = auto()
    ADAPTER_MODBUS_BIT_DOWN_SERVO_LOCK = auto()
    ADAPTER_MODBUS_BIT_LEFT_SERVO_RELEASE = auto()
    ADAPTER_MODBUS_BIT_LEFT_SERVO_LOCK = auto()
    ADAPTER_MODBUS_BIT_RIGHT_SERVO_RELEASE = auto()
    ADAPTER_MODBUS_BIT_RIGHT_SERVO_LOCK = auto()

    # /* 串口舵机读取标记 */
    ADAPTER_MODBUS_BIT_READ_UP_ANGLE = auto()
    ADAPTER_MODBUS_BIT_READ_DOWN_ANGLE = auto()
    ADAPTER_MODBUS_BIT_READ_LEFT_ANGLE = auto()
    ADAPTER_MODBUS_BIT_READ_RIGHT_ANGLE = auto()
    # /* serial servo set id */
    ADAPTER_MODBUS_BIT_SERVO_SET_ID = auto()
    # /* 升降电机动作 */
    ADAPTER_MODBUS_BIT_LIFT_UP = auto()
    ADAPTER_MODBUS_BIT_LIFT_DOWN = auto()
    ADAPTER_MODBUS_BIT_LIFT_STOP = auto()

    # /* 串口舵机自动设置中位置标记 */
    ADAPTER_MODBUS_BIT_AUTO_SET_MID_UP_SERVO = auto()
    ADAPTER_MODBUS_BIT_AUTO_SET_MID_DOWN_SERVO = auto()
    ADAPTER_MODBUS_BIT_AUTO_SET_MID_LEFT_SERVO = auto()
    ADAPTER_MODBUS_BIT_AUTO_SET_MID_RIGHT_SERVO = auto()

    # /* 串口舵机动作标记 */
    ADAPTER_MODBUS_BIT_SERVO_ACTION = auto()

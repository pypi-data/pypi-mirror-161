from .utils import adapter_modbus_config_t, adapter_modbus_bit_t, get_crc, MODBUS_SLAVE_ADDR, PORT, BAUDRATE, Communicator, Logger
import modbus_tk.defines as cst
import atexit

class Lift(object):
    def __init__(self, port=PORT, baudrate=BAUDRATE):
        super().__init__()
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        atexit.register(self.stop)

    def up(self, timeout=3000):
        timeout = int(timeout)
        to_addr = adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LIFT_TIMEOUT
        pdu = bytearray([MODBUS_SLAVE_ADDR, cst.WRITE_SINGLE_REGISTER]) + \
            bytearray([0, to_addr, (timeout>>8)&0xff, timeout&0xff])
        cmd = pdu + get_crc(pdu)
        self._master._serial.write(cmd)
        bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_LIFT_UP
        self._master.execute(MODBUS_SLAVE_ADDR,
                             cst.WRITE_SINGLE_COIL,
                             bit,
                             output_value=1)

    def down(self, timeout=3000):
        timeout = int(timeout)
        to_addr = adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LIFT_TIMEOUT
        pdu = bytearray([MODBUS_SLAVE_ADDR, cst.WRITE_SINGLE_REGISTER]) + \
            bytearray([0, to_addr, (timeout>>8)&0xff, timeout&0xff])
        cmd = pdu + get_crc(pdu)
        self._master._serial.write(cmd)
        bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_LIFT_DOWN
        self._master.execute(MODBUS_SLAVE_ADDR,
                             cst.WRITE_SINGLE_COIL,
                             bit,
                             output_value=1)

    def stop(self):
        bit = adapter_modbus_bit_t.ADAPTER_MODBUS_BIT_LIFT_STOP
        self._master.execute(MODBUS_SLAVE_ADDR,
                             cst.WRITE_SINGLE_COIL,
                             bit,
                             output_value=1)

from .utils import adapter_modbus_config_t, MODBUS_SLAVE_ADDR, PORT, BAUDRATE, Communicator
import modbus_tk.defines as cst


class PowerDetect(object):
    def __init__(self, port=PORT, baudrate=BAUDRATE):
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master

    def get_raw(self):
        try:
            (raw, ) = self._master.execute(
                MODBUS_SLAVE_ADDR, cst.READ_HOLDING_REGISTERS,
                adapter_modbus_config_t.ADAPTER_MODBUS_POWER_DETECT_BUF, 1)
        except:
            raw = -1
        return raw

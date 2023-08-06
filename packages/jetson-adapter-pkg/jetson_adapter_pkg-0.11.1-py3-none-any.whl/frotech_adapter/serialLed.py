from .utils import adapter_modbus_config_t, get_crc, MODBUS_SLAVE_ADDR, PORT, BAUDRATE, Communicator
import modbus_tk.defines as cst
import logging
import atexit

_MODE = {'bln': 1, 'custom': 2}


class SerialLed(object):
    """串行LED灯驱动

    在开始控制之前，需要先调用 :py:meth:`start` 方法。要关闭串行LED则调用 :py:meth:`stop` 方法。

    串行LED有两种工作模式，一种是呼吸灯模式，另一种是自定义模式。要更改工作模式可使用
    :py:meth:`mode` 方法。

    在自定义模式下，可以利用 :py:meth:`write` 方法，设置每个LED的颜色。

    Examples
    --------
    >>> from frotech_adapter import SerialLed

    >>> led = SerialLed()
    >>> led.start() # 开启车身氛围灯功能
    >>> led.mode('bln') # 设置为呼吸灯模式

    >>> led.mode('custom') # 设置为自定义模式
    >>> # 设置前4盏灯的颜色，分别是白色，红色，蓝色和绿色
    >>> colors = [0xffffff,0xff0000,0x00ff00,0x0000ff]
    >>> led.write(colors) # 设置车灯颜色，只有在自定义模式下才有效
    >>> led.stop() # 关闭车身氛围灯功能
    """

    BLN_MODE = 1
    DIY_MODE = 2

    def __init__(self, max_led_num=12, port=PORT, baudrate=BAUDRATE):
        self.__max_led_num = max_led_num
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        self._mode = self.BLN_MODE
        atexit.register(self.stop)

    def start(self):
        """开启串行LED功能
        """
        self.mode('bln')
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_SINGLE_REGISTER,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LED_ENABLE,
                output_value=1)
            return True
        except:
            return False

    def stop(self):
        """关闭串行LED功能
        """
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_SINGLE_REGISTER,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LED_ENABLE,
                output_value=0)
            return True
        except:
            return False

    def mode(self, led_mode):
        """设置串行LED工作模式

        Parameters
        ----------
        led_mode : str
            可取值为 'bln' 或 'custom'

            * 'bln': 呼吸灯模式
            * 'custom': 自定义模式
        """
        if led_mode not in _MODE:
            return False
        self._mode = _MODE[led_mode]
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_SINGLE_REGISTER,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LED_MODE,
                output_value=self._mode)
            return True
        except:
            return False

    def write(self, colors):
        """设置自定义颜色

        Parameters
        ----------
        colors : list[int]
            由int型组成的列表，索引号为0的int数据控制第一个的LED，
            索引号为1的int数据控制第二行的LED，以此类推。

            int数据中的bit7-bit0: 蓝色亮度；
            bit15-bit8: 绿色亮度；
            bit23-bit16: 红色亮度；

            亮度范围: 0-255

        Examples
        --------
        >>> led.mode('custom') # 设置为自定义模式
        >>> # 设置前4盏灯的颜色，分别是白色，红色，蓝色和绿色
        >>> colors = [0xffffff,0xff0000,0x00ff00,0x0000ff]
        >>> led.write(colors) # 设置车灯颜色，只有在自定义模式下才有效
        """
        if len(colors) > self.__max_led_num:
            colors = colors[:self.__max_led_num]
        grb = []
        for c in colors:
            r = (c >> 16) & 0xff
            g = (c >> 8) & 0xff
            b = c & 0xff
            grb.append(g)
            grb.append((r << 8) + b)
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_MULTIPLE_REGISTERS,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_LED1_COLOR_HIGH,
                output_value=grb)
            self._master.execute(MODBUS_SLAVE_ADDR,
                                 cst.WRITE_SINGLE_COIL,
                                 8,
                                 output_value=1)
            return True
        except:
            return False

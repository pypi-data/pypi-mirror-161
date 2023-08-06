from .utils import adapter_modbus_config_t, get_crc, MODBUS_SLAVE_ADDR, PORT, BAUDRATE, Communicator
import modbus_tk.defines as cst
import atexit

_mode = {'pattern': 1, 'custom': 2}


class LedMatrix(object):
    """LED点阵驱动

    控制LED点阵显示的内容

    在开始控制之前，需要先调用 :py:meth:`start` 方法。要关闭LED点阵功能，则调用 :py:meth:`stop` 方法

    Examples
    --------
    >>> dot_led = LedMatrix() # 创建LED点阵对象

    >>> dot_led.start() # 开启LED点阵功能

    >>> dot_led.mode('pattern') # 设置LED点阵进入图案模式，在该模式下只能显示特定的图案
    >>> dot_led.show(1) # 显示1号图案

    >>> dot_led.mode('custom') # 设置LED点阵进入自定义模式
    >>> patterns = [0xffff] # 准备自定义的图案数据
    >>> dot_led.write(patterns) # 第一行LED全亮

    >>> dot_led.stop() # 关闭LED点阵功能

    Todo
    ----
    初始化时自动进入图案模式
    """

    PATTERN_MODE = 1
    DIY_MODE = 2

    def __init__(self, mode=1, port=PORT, baudrate=BAUDRATE):
        self.__mode = mode
        self.__pattern = 0
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        atexit.register(self.stop)

    def start(self):
        """开启LED点阵功能"""
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_SINGLE_REGISTER,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_MATRIX_MODE,
                output_value=0x8000 + self.__mode)
            return True
        except:
            return False

    def stop(self):
        """关闭LED点阵功能"""
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_SINGLE_REGISTER,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_MATRIX_MODE,
                output_value=0x4000 + self.__mode)
            return True
        except:
            return False

    def mode(self, mode):
        """设置LED点阵工作模式

        Parameters
        ----------
        mode : str
            该值只能为 'pattern' 或 'custom'

            'pattern': 图案模式；进入该模式后，可以配合 :py:meth:`show`
            方法显示特定的图案。

            'custom': 自定义模式；进入该模式后，可以配合 :py:meth:`write`
            方法显示自定义图案。

        """
        if mode not in _mode:
            return False
        self.__mode = _mode[mode]
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_SINGLE_REGISTER,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_MATRIX_MODE,
                output_value=self.__mode)
            return True
        except:
            return False

    def show(self, num):
        """显示特定图案

        在使用该方法之前，需要利用 :py:meth:`mode` 将LED点阵设置为图案模式。

        Parameters
        ----------
        num : int
            图案索引号。索引号取值从0开始，最大索引号由转接板固件而定，当输入的索引号大于转接板设定
            的最大索引号，该次操作无效。

        Examples
        --------
        >>> dot_led.mode('pattern') # 设置LED点阵进入图案模式，在该模式下只能显示特定的图案
        >>> dot_led.show(2) # 显示2号图案
        """
        if self.__mode != self.PATTERN_MODE:
            return
        self.__pattern = num
        digs = [self.PATTERN_MODE, num]
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_MULTIPLE_REGISTERS,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_MATRIX_MODE,
                output_value=digs)
            return True
        except:
            return False

    def write(self, data):
        """写入自定义图案

        在使用该方法之前，需要利用 :py:meth:`mode` 将LED点阵设置为自定义模式。

        Parameters
        ----------
        data : list[int]
            由int型组成的列表，索引号为0的int数据控制第一行的LED，
            索引号为1的int数据控制第二行的LED，以此类推。

            int数据中的bit0控制最后一个LED，bit1控制倒数第二个LED，以此类推。

        Examples
        --------
        >>> dot_led.mode('custom') # 设置LED点阵进入自定义模式
        >>> # 准备自定义的图案数据
        >>> # 第一行全亮，第二行最后一个LED亮，第三行第一个LED亮
        >>> patterns = [0xffff, 0x01, 0x8000]
        >>> dot_led.write(patterns) # 显示自定义图案

        >>> # 第一行全灭，第二行全亮，其它行的数据保持不变
        >>> patterns = [0, 0xffff]
        >>> dot_led.write(patterns) # 显示自定义图案

        """
        if self.__mode != self.DIY_MODE:
            return
        if len(data) > 8:
            data = data[:8]

        if type(data[0]) == str:
            data = [int(d, 0) for d in data]  # 兼容 scratch 的列表

        tmp = [(d >> 8) + ((d & 0xff) << 8) for d in data]
        digs = [self.DIY_MODE, self.__pattern] + tmp
        try:
            self._master.execute(
                MODBUS_SLAVE_ADDR,
                cst.WRITE_MULTIPLE_REGISTERS,
                adapter_modbus_config_t.ADAPTER_MODBUS_CONFIG_MATRIX_MODE,
                output_value=digs)
            return True
        except:
            return False

    def generate_bitmap(self, data):
        """生成点阵图数据

        Parameters
        ----------
        data : str
            描述点阵状态的字符串，'1'代表亮，'0'代表灭

        Returns
        -------
        list
            由int型组成的列表，索引号为0的int数据控制第一行的LED，
            索引号为1的int数据控制第二行的LED，以此类推。

            int数据中的bit0控制最后一个LED，bit1控制倒数第二个LED，以此类推。

        Examples
        --------
        >>> bitmap = '''
        >>> 10000000 00000001
        >>> 01000000 00000010
        >>> 00100000 00000100
        >>> 00010000 00001000
        >>> 00001000 00010000
        >>> 00000100 00100000
        >>> 00000010 01000000
        >>> 00000001 10000000
        >>> '''
        >>> patterns = dot_led.generate_bitmap(bitmap)
        >>> dot_led.write(patterns) # 显示自定义图案
        """

        d = []
        for line in data.splitlines():
            byte = 0
            if len(line) == 0:
                continue
            for c in line:
                if c in '10':
                    byte <<= 1
                if c == '1':
                    byte |= 1
            d.append(byte)
        return d

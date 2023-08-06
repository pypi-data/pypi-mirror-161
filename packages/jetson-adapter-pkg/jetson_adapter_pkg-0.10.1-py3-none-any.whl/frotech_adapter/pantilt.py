from .utils import PORT, BAUDRATE, Communicator
import traitlets
from traitlets.config.configurable import SingletonConfigurable
import threading
from .serialServo import SerialServo
import time


class PanTilt(SingletonConfigurable):
    """云台控制驱动

    Examples
    --------
    >>> pan = PanTilt() # 创建云台对象
    >>> pan.down(10) # 云台往下转10度
    >>> pan.right(19) # 云台往右转19度
    >>> pan.up(20) # 云台往上转20度
    >>> pan.set_pos(40, 30) # 云台上面的舵机转到40度的位置，下面的舵机转到30度的位置
    >>> pan.set_pos(20, None) # 云台上面的舵机转到20度的位置，下面的舵机角度不变
    >>> pan.release() # 释放舵机
    """

    THRESHOLD = 0.1

    up_servo = traitlets.Instance(SerialServo)
    down_servo = traitlets.Instance(SerialServo)

    vertical = traitlets.Float()
    horizontal = traitlets.Float()

    def __init__(self, port=PORT, baudrate=BAUDRATE, *args, **kwargs):
        super(PanTilt, self).__init__(*args, **kwargs)
        self._rtu = Communicator.instance(port=port, baudrate=baudrate)
        self._master = self._rtu.master
        self.up_servo = SerialServo('up')
        self.down_servo = SerialServo('down')
        self._ENABLE_GAMEPAD_CONTROL = False
        self.up_servo.run_time = 0
        self.down_servo.run_time = 0
        self.gama = 5

    def lock(self):
        """锁定舵机
        """
        self.up_servo.lock()
        self.down_servo.lock()

    def release(self):
        """释放舵机
        """
        self.up_servo.release()
        self.down_servo.release()

    def _run(self):
        while True:
            try:
                if not self._ENABLE_GAMEPAD_CONTROL:
                    break
                up_angle = self.up_servo.angle
                down_angle = self.down_servo.angle

                if abs(self.vertical) > self.THRESHOLD:
                    up_angle += int(self.vertical * self.gama)
                    if up_angle > self.up_servo.limit_range[1]:
                        up_angle = self.up_servo.limit_range[1]
                    if up_angle < self.up_servo.limit_range[0]:
                        up_angle = self.up_servo.limit_range[0]
                    self.up_servo.angle = up_angle

                if abs(self.horizontal) > self.THRESHOLD:
                    down_angle += int(self.horizontal * self.gama)
                    if down_angle > self.down_servo.limit_range[1]:
                        down_angle = self.down_servo.limit_range[1]
                    if down_angle < self.down_servo.limit_range[0]:
                        down_angle = self.down_servo.limit_range[0]
                    self.down_servo.angle = down_angle

                time.sleep(0.03)
            except:
                self._ENABLE_GAMEPAD_CONTROL = False

    def gamepad_start(self):
        if not self._ENABLE_GAMEPAD_CONTROL:
            self._ENABLE_GAMEPAD_CONTROL = True
        if not hasattr(self, '_thread') or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

    def gamepad_stop(self):
        self._ENABLE_GAMEPAD_CONTROL = False
        if hasattr(self, '_thread'):
            self._thread.join()

    def left(self, value):
        """控制云台往左边转动一定角度

        Parameters
        ----------
        value : float
            角度，取值范围[-180, 180]。

        Note
        ----
        实际转动角度受舵机的角度限制影响。
        """
        self.down_servo.angle += value

    def right(self, value):
        """控制云台往右边转动一定角度

        Parameters
        ----------
        value : float
            角度，取值范围[-180, 180]。

        Note
        ----
        实际转动角度受舵机的角度限制影响。
        """
        self.down_servo.angle -= value

    def up(self, value):
        """控制云台往上边转动一定角度

        Parameters
        ----------
        value : float
            角度，取值范围[-180, 180]。

        Note
        ----
        实际转动角度受舵机的角度限制影响。
        """
        self.up_servo.angle += value

    def down(self, value):
        """控制云台往下边转动一定角度

        Parameters
        ----------
        value : float
            角度，取值范围[-180, 180]。

        Note
        ----
        实际转动角度受舵机的角度限制影响。
        """
        self.up_servo.angle -= value

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
            self.up_servo.set_angle(v_pos)
        if h_pos is not None:
            self.down_servo.set_angle(h_pos)

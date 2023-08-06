import traitlets
from traitlets.config.configurable import SingletonConfigurable
from .utils import PORT, BAUDRATE
import modbus_tk.defines as cst
import threading
import time
from .motor import Motor


class Car(SingletonConfigurable):
    """
    小车驱动

    控制小车的电机运动

    Examples
    --------
    >>> car = Car()

    >>> car.left(0.3) # 小车以30%的速度向左旋转
    >>> car.right(-0.3) # 小车以30%的速度向左旋转

    >>> car.set_motors(0.4, 0.8) # 设置小车左轮以40%的速度正向转动，右轮以80%速度正向转动

    >>> car.run(0.5) # 小车以50%的速度向前运行

    >>> car.run(-0.5) # 小车以50%的速度向后运行

    >>> car.stop() # 停止小车运动
    """

    LOWEST_SPEED = 0.2
    """float: 最小激活速度-当电机速度的绝对值低于该值，电机速度为0。默认该值为0.2。"""

    left_motor = traitlets.Instance(Motor)
    right_motor = traitlets.Instance(Motor)

    forward = traitlets.Float()
    backward = traitlets.Float()
    direction = traitlets.Float()
    alpha = traitlets.Float()

    def __init__(self, port=PORT, baudrate=BAUDRATE, *args, **kwargs):
        super(Car, self).__init__(*args, **kwargs)
        self.left_motor = Motor("left", port=port, baudrate=baudrate)
        self.right_motor = Motor("right")
        self.alpha = 0.8
        self._ENABLE_GAMEPAD_CONTROL = False

    def _run(self):
        while True:
            try:
                if not self._ENABLE_GAMEPAD_CONTROL:
                    break
                lspeed = self.forward - self.backward + self.direction * self.alpha
                rspeed = self.forward - self.backward - self.direction * self.alpha
                if abs(lspeed) < self.LOWEST_SPEED:
                    lspeed = 0
                if abs(rspeed) < self.LOWEST_SPEED:
                    rspeed = 0
                self.set_motors(lspeed, rspeed)
                time.sleep(0.02)
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
        self.stop()

    def set_motors(self, left_speed=None, right_speed=None):
        """
        设置小车左右两电机的转速

        Parameters
        ----------
        left_speed : float, optional
            左电机的速度，取值范围[-1,1]。正数代表向前转动，负数代表向后转动。
            值为None时，不改变速度。
        right_speed: float, optional
            右电机的速度，取值范围[-1,1]。正数代表向前转动，负数代表向后转动。
            值为None时，不改变速度。

        Examples
        --------
        >>> car.set_motors(0.5, 0.3) # 左电机以50%速度向前转动，右电机以30%速度向后转动
        """
        if left_speed is not None:
            left_speed = float(left_speed)
            self.left_motor.throttle = int(left_speed * 4096)
        if right_speed is not None:
            right_speed = float(right_speed)
            self.right_motor.throttle = int(right_speed * 4096)

    def run(self, speed=1.0):
        """
        设置小车向前或向后运动的速度

        Parameters
        ----------
        speed : float
            小车运行速度，取值范围[-1,1]。

            相当于`car.set_motors(speed, speed)`

        Examples
        --------
        >>> car.run(0.5) # 小车以50%的速度向前运动
        >>> car.run(-1) # 小车以100%的速度向后运动
        """
        self.left_motor.throttle = int(speed * 4096)
        self.right_motor.throttle = int(speed * 4096)

    def forward(self, speed=1.0):
        """设置小车向前运行

        Parameters
        ----------
        speed : float
            小车向前运行速度，取值范围[-1,1]。

            相当于`car.set_motors(speed, speed)`

        Examples
        --------
        >>> car.forward(0.5) # 小车以50%的速度向前运动
        """
        self.left_motor.throttle = int(speed * 4096)
        self.right_motor.throttle = int(speed * 4096)

    def backward(self, speed=1.0):
        """设置小车向后运行

        Parameters
        ----------
        speed : float
            小车运行速度，取值范围[-1,1]。

            相当于`car.set_motors(-speed, -speed)`

        Examples
        --------
        >>> car.backward(0.5) # 小车以50%的速度向后运动
        """
        self.left_motor.throttle = int(-speed * 4096)
        self.right_motor.throttle = int(-speed * 4096)

    def left(self, speed=1.0):
        """
        设置小车向左旋转运动的速度

        Parameters
        ----------
        speed : float
            小车向左旋转运动的速度，取值范围[-1,1]。

            相当于`car.set_motors(-speed, speed)`

        Examples
        --------
        >>> car.left(0.5) # 小车以50%的速度向左运动
        """
        self.left_motor.throttle = int(-speed * 4096)
        self.right_motor.throttle = int(speed * 4096)

    def right(self, speed=1.0):
        """
        设置小车向右旋转运动的速度

        Parameters
        ----------
        speed : float
            小车向右旋转运动的速度，取值范围[-1,1]。

            `car.right(speed)` 相当于 `car.set_motors(speed, -speed)`

        Examples
        --------
        >>> car.right(0.5) # 小车以50%的速度向右运动
        """
        self.left_motor.throttle = int(speed * 4096)
        self.right_motor.throttle = int(-speed * 4096)

    def stop(self):
        """
        停止小车运动

        """
        self.left_motor.throttle = None
        self.right_motor.throttle = None

    def _release(self):
        self.left_motor.throttle = 0
        self.right_motor.throttle = 0

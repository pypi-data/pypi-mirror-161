from .robotServo import ArmServo
import traitlets
from traitlets.config.configurable import SingletonConfigurable
import math
import numpy as np
import threading

L0 = 100
L1 = 100
L2 = 59.5
L3 = 63.5


def float_equal(x, y):
    return abs(x - y) < 1e-15


RAD2DEG = 180 / np.pi


class DummyArm(SingletonConfigurable):

    j0 = traitlets.Instance(ArmServo)
    j1 = traitlets.Instance(ArmServo)
    j2 = traitlets.Instance(ArmServo)
    j3 = traitlets.Instance(ArmServo)
    jall = traitlets.Instance(ArmServo)

    def __init__(self, l0=None, l1=None, l2=None, l3=None, gripper=None):
        self.j0 = ArmServo('j0')  # TODO: set limit range
        self.j1 = ArmServo('j1')
        self.j2 = ArmServo('j2')
        self.j3 = ArmServo('j3')
        self.jall = ArmServo('all')
        self._release_flag = True
        self.l0 = l0 if l0 is not None else L0
        self.l1 = l1 if l1 is not None else L1
        self.l2 = l2 if l2 is not None else L2
        self.l3 = l3 if l3 is not None else L3
        self._speed = 9 / 100  # deg/ms
        self.last_t0 = 90
        self.last_t1 = 90
        self.last_t2 = 90
        self.last_t3 = 90
        self.gripper = gripper
        self._user_x = -1
        self._user_y = -1
        self._user_z = -1
        self._rlock = threading.RLock()

    def homing(self):
        self.moveJ(90, 90, 90, 180)

    def moveJ(self, theta0, theta1, theta2, theta3):
        self._rlock.acquire()
        if self._release_flag:
            # 当前舵机释放过后，需要先读取一次位置才能正常调整位置
            # lock() 会读取舵机角度。
            self.lock()

        t = -1
        valid = True

        if theta0 > 185 or theta0 < -5:
            valid = False

        if theta1 > 186 or theta1 < 47:
            valid = False

        if theta2 > 130 or theta2 < -30:
            valid = False

        if theta3 > 185 or theta3 < -5:
            valid = False

        if valid:
            angles = [theta0, theta1, theta2, theta3]
            last_angles = [
                self.last_t0, self.last_t1, self.last_t2, self.last_t3
            ]
            max_angle = -1
            for a, b in zip(angles, last_angles):
                if abs(a - b) > max_angle:
                    max_angle = abs(a - b)
            t = max_angle / self._speed  # 单位 ms
            self.j0.run_time = int(t)
            self.j1.run_time = int(t)
            self.j2.run_time = int(t)
            self.j3.run_time = int(t)
            self.j0.set_angle(theta0)
            self.j1.set_angle(theta1)
            self.j2.set_angle(theta2)
            self.j3.set_angle(theta3)
            self.last_t0 = theta0
            self.last_t1 = theta1
            self.last_t2 = theta2
            self.last_t3 = theta3

            self.jall.action()
        self._rlock.release()
        return t

    def moveL(self, x, y, z):
        self._rlock.acquire()
        t = -1
        ret, a1, a2, a3, a4 = self.solveIK(x, y, z)
        if ret:
            t = self.moveJ(a1, a2, a3, a4)
            self._user_x = -x
            self._user_y = y
            self._user_z = z
        self._rlock.release()
        return t

    def release(self):
        self._rlock.acquire()
        self._release_flag = True
        self.jall.release()
        self._rlock.release()

    def lock(self):
        self._rlock.acquire()
        self._release_flag = False
        # 当前驱动板的固件在读取位置后，
        # 会执行一次设置位置的操作，从而实现 lock
        self.get_angle()
        self._rlock.release()

    def get_angle(self):
        self._rlock.acquire()
        pos0 = self.j0.read_position()
        pos1 = self.j1.read_position()
        pos2 = self.j2.read_position()
        pos3 = self.j3.read_position()

        def pos2angle(pos):
            return (pos - 819.5) / 1228.5 * 90

        self.last_t0 = pos2angle(pos0)
        self.last_t1 = pos2angle(pos1)
        self.last_t2 = pos2angle(pos2)
        self.last_t3 = pos2angle(pos3)
        self._rlock.release()
        return self.last_t0, self.last_t1, self.last_t2, self.last_t3

    def solveIK(self, x, y, z):
        """求解逆运动学，这里假设 {T} 的 Z坐标永远垂直向下

        Args:
            x (float): {B} 的 X坐标，单位mm
            y (float): {B} 的 Y坐标，单位mm
            z (float): {B} 的 Z坐标，单位mm

        Returns:
            Tuple: ret, a1, a2, a3, a4

            ret (bool): 有解时返回 True，否则返回 False

            a1~a4: 各舵机角度
        """
        l0 = self.l0
        l1 = self.l1
        l2 = self.l2
        l3 = self.l3

        x1 = -math.sqrt(x**2 + y**2) + l2
        z1 = z + l3
        c3 = (x1**2 + z1**2 - l1**2 - l0**2) / (2 * l1 * l0)
        if c3 > 1 or c3 < -1:
            return False, 0, 0, 0, 0

        a3 = math.acos(c3)  # 只需取正值

        beta = math.atan2(z1, x1)

        cpsi = (x1**2 + z1**2 + l0**2 - l1**2) / (2 * l0 *
                                                  math.sqrt(x1**2 + z1**2))
        if cpsi > 1 or cpsi < -1:
            return False, 0, 0, 0, 0

        psi = math.acos(cpsi)  # 只需取正值
        a2 = beta - psi  # 若 a3 取负值，则 = beta+psi
        if a2 < 0:
            a2 = 2 * np.pi + a2

        a4 = np.pi - a3 - a2

        a1 = math.atan2(-y, -x)

        a1 *= RAD2DEG
        a2 *= RAD2DEG
        a3 *= RAD2DEG
        a4 *= RAD2DEG

        a1 += 90
        a3 = -a3 + 90
        a4 += 90

        return True, a1, a2, a3, a4

    def solveFK(self, angles):
        """求解正运动学

        Args:
            angles (list): 各舵机的角度

        Returns:
            tuple: X, Y, Z, gamma, beta, alpha

            X, Y, Z 是 {T} 原点在 {B} 下的表示。
            
            gamma, beta, alpha 是 {T} 以 {B} 为参考系，
            并用 X-Y-Z 固定角方法描述的旋转角。
        """

        a1 = (angles[0] - 90) / RAD2DEG
        a2 = (angles[1]) / RAD2DEG
        a3 = -(angles[2] - 90) / RAD2DEG
        a4 = (angles[3] - 90) / RAD2DEG

        s1 = math.sin(a1)
        c1 = math.cos(a1)
        s2 = math.sin(a2)
        c2 = math.cos(a2)
        s23 = math.sin(a2 + a3)
        c23 = math.cos(a2 + a3)
        s234 = math.sin(a2 + a3 + a4)
        c234 = math.cos(a2 + a3 + a4)

        r11 = s1
        r12 = c1 * c234
        r13 = -c1 * s234
        r14 = c1 * (c234 * self.l2 - s234 * self.l3 + c23 * self.l1 +
                    c2 * self.l0)

        r21 = -c1
        r22 = s1 * c234
        r23 = -s1 * s234
        r24 = s1 * (c234 * self.l2 - s234 * self.l3 + c23 * self.l1 +
                    c2 * self.l0)

        r31 = 0
        r32 = s234
        r33 = c234
        r34 = s234 * self.l2 + c234 * self.l3 + s23 * self.l1 + s2 * self.l0

        T = np.array([[r11, r12, r13, r14], [r21, r22, r23, r24],
                      [r31, r32, r33, r34], [0, 0, 0, 1]])

        beta = math.atan2(-T[2][0], math.sqrt(T[0][0]**2 + T[1][0]**2))
        if float_equal(beta, np.pi / 2):
            alpha = 0
            gamma = math.atan2(T[0][1], T[1][1])
        elif float_equal(beta, -np.pi / 2):
            alpha = 0
            gamma = -math.atan2(T[0][1], T[1][1])
        else:
            alpha = math.atan2(T[1][0] / math.cos(beta),
                               T[0][0] / math.cos(beta))
            gamma = math.atan2(T[2][1] / math.cos(beta),
                               T[2][2] / math.cos(beta))
        X = float(np.around(T[0][3], 2))
        Y = float(np.around(T[1][3], 2))
        Z = float(np.around(T[2][3], 2))

        return X, Y, Z, gamma, beta, alpha

    def calibration_tool(self):
        """自动根据当前前3个舵机角度，推出第4个舵机角度
        """
        a1, a2, a3, _ = self.get_angle()
        a4 = 180 - a2 + a3
        x, y, z, _, _, _ = self.solveFK([a1, a2, a3, a4])

        t = self.moveJ(a1, a2, a3, a4)
        if t >= 0:
            self._user_x = -x
            self._user_y = y
            self._user_z = z
        else:
            self._user_x = -1
            self._user_y = -1
            self._user_z = -1

    def current_state(self):
        g_state = None
        if self.gripper is not None:
            g_state = self.gripper.get_state()
        return self._user_x, self._user_y, self._user_z, g_state

    def act(self, action):
        x = -action.get('x', -1)
        y = action.get('y', -1)
        z = action.get('z', -1)
        gs = action.get('gripper_state')
        self.moveL(x, y, z)
        if self.gripper is not None:
            self.gripper.act(gs)

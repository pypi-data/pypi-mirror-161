from .lobotServo import LobotServo
import traitlets
from traitlets.config.configurable import SingletonConfigurable
import math
import threading
from frotech_adapter.utils import PORT
import numpy as np
from loguru import logger


def float_equal(x, y):
    return abs(x - y) < 1e-15


L0 = 84.4 / 1000
L1 = 8.14 / 1000
L2 = 128.4 / 1000
L3 = 138.0 / 1000

RAD2DEG = 180 / math.pi
DEG2RAD = math.pi / 180
DOUBLE_PI = math.pi * 2


class LobotArm(SingletonConfigurable):

    j0 = traitlets.Instance(LobotServo)
    j1 = traitlets.Instance(LobotServo)
    j2 = traitlets.Instance(LobotServo)
    j3 = traitlets.Instance(LobotServo)
    jall = traitlets.Instance(LobotServo)

    def __init__(self,
                 l0=None,
                 l1=None,
                 l2=None,
                 l3=None,
                 gripper=None,
                 port=PORT):
        self.j1 = LobotServo('j1', port=port)
        self.j2 = LobotServo('j2')
        self.j3 = LobotServo('j3')
        self.jall = LobotServo('all')
        self._release_flag = True
        self.l0 = l0 if l0 is not None else L0
        self.l1 = l1 if l1 is not None else L1
        self.l2 = l2 if l2 is not None else L2
        self.l3 = l3 if l3 is not None else L3
        self._speed = 9 / 300  # deg/ms
        self.last_t1 = 90
        self.last_t2 = 90
        self.last_t3 = 90
        self.gripper = gripper
        self._user_x = -1
        self._user_y = -1
        self._user_z = -1
        self._rlock = threading.RLock()
        self.T_g2b = None

    def homing(self):
        self.moveL(0, -(L1 + L3), L0 + L2)

    def get_angle(self):
        self._rlock.acquire()

        pos1 = self.j1.read_position()
        pos2 = self.j2.read_position()
        pos3 = self.j3.read_position()

        def pos2angle(pos):
            return pos / 1000 * 240

        self.last_t1 = pos2angle(pos1)
        self.last_t2 = pos2angle(pos2)
        self.last_t3 = pos2angle(pos3)
        self._rlock.release()
        return self.last_t1, self.last_t2, self.last_t3

    def solveIK(self, x, y, z):
        r = math.sqrt(x**2 + y**2)
        if x == 0:
            theta1 = math.pi / 2 if y >= 0 else math.pi / 2 * 3  # pi/2 90deg, (pi * 3) / 2  270deg
        else:
            if y == 0:
                theta1 = 0 if x > 0 else math.pi
            else:
                theta1 = math.atan(y / x)  # θ=arctan(y/x) (x!=0)
                if x < 0:
                    theta1 += math.pi
                else:
                    if y < 0:
                        theta1 += math.pi * 2

        r = r - L1
        z = z - L0
        if math.sqrt(r**2 + z**2) > (L2 + L3):
            # raise ValueError('Unreachable position: x:{}, y:{}, z:{}'.format(
            #     x, y, z))
            return False, 0, 0, 0

        alpha = math.atan(z / r)
        beta = math.acos((L2**2 + L3**2 - (r**2 + z**2)) / (2 * L2 * L3))
        gamma = math.acos((L2**2 + (r**2 + z**2) - L3**2) /
                          (2 * L2 * math.sqrt(r**2 + z**2)))

        theta1 = theta1
        theta2 = math.pi - (alpha + gamma)
        theta3 = math.pi - (beta + alpha + gamma)

        theta1 = theta1 * RAD2DEG
        if 30 < theta1 < 150:  # The servo motion range is 240 deg. 150~360+0~30 = 240
            # raise ValueError('Unreachable position: x:{}, y:{}, z:{}'.format(
            #     x, y, z))
            return False, 0, 0, 0
        theta1 = theta1 + 360 if theta1 <= 30 else theta1  # 0~360 to 30~390
        theta1 = theta1 - 150
        theta2 *= RAD2DEG
        theta3 *= RAD2DEG
        theta2 = (theta2 - 210) * -1  # 210 ~ -30 map to 0 ~ 240
        theta3 += 120  # -120 ~ 120 map to 0 ~ 240
        return True, theta1, theta2, theta3 

    def solveFK(self, angles):
        alpha1, alpha2, alpha3 = [angle * DEG2RAD for angle in angles]
        alpha1 += 150 * DEG2RAD
        alpha1 = alpha1 - DOUBLE_PI if alpha1 > DOUBLE_PI else alpha1
        beta = alpha2 - alpha3
        side_beta = math.sqrt(L2**2 + L3**2 - 2 * L2 * L3 * math.cos(beta))
        cos_gamma = ((side_beta**2 + L2**2) - L3**2) / (2 * side_beta * L2)
        cos_gamma = cos_gamma if cos_gamma < 1 else 1
        gamma = math.acos(cos_gamma)
        alpha_gamma = math.pi - alpha2
        alpha = alpha_gamma - gamma
        z = side_beta * math.sin(alpha)
        r = math.sqrt(side_beta**2 - z**2)
        z = z + L0
        r = r + L1
        x = r * math.cos(alpha1)
        y = r * math.sin(alpha1)
        return x, y, z

    def get_T(self, angles=None):
        """获取变换矩阵

        Args:
            angles (float): LobotArm.solveIK() 返回的3个angle。
            当为 None 时，取执行 LobotArm.moveL()后自动计算的值。

        Returns:
            np.ndarray: 4x4 变换矩阵
        """
        if angles is None:
            return self.T_g2b

        # angle1: default 0 ~ 240
        # angle2: 0 ~ 240
        # angle3: 0 ~ 240
        angle1, angle2, angle3 = angles

        # angle2 = (angle2 - 210) * -1  # 210 ~ -30 map to 0 ~ 240
        angle3 -= 120  # 0 ~ 240 map to -120 ~ 120

        theta0 = angle1 + 150
        theta1 = angle2 - 30

        _alpha = 180 - theta1 - angle3
        theta2 = 180 + _alpha

        theta3 = angle3

        theta0 *= DEG2RAD
        theta1 *= DEG2RAD
        theta2 *= DEG2RAD
        theta3 *= DEG2RAD

        c0 = math.cos(theta0)
        s0 = math.sin(theta0)
        c1 = math.cos(theta1)
        s1 = math.sin(theta1)
        c2 = math.cos(theta2)
        s2 = math.sin(theta2)
        c3 = math.cos(theta3)
        s3 = math.sin(theta3)

        T1to0 = np.array([[c1, -s1, 0, L1], [0, 0, -1, 0], [s1, c1, 0, 0],
                          [0, 0, 0, 1]])
        T2to1 = np.array([[c2, -s2, 0, L2], [s2, c2, 0, 0], [0, 0, 1, 0],
                          [0, 0, 0, 1]])
        T3to2 = np.array([[c3, -s3, 0, L3], [s3, c3, 0, 0], [0, 0, 1, 0],
                          [0, 0, 0, 1]])
        T0tob = np.array([[c0, -s0, 0, 0], [s0, c0, 0, 0], [0, 0, 1, 0],
                          [0, 0, 0, 1]])

        T3tob = T0tob.dot(T1to0).dot(T2to1).dot(T3to2)

        return T3tob

    def moveJ(self, theta1, theta2, theta3):
        t = -1
        valid = True

        # theta2 = (theta2 - 210) * -1  # 210 ~ -30 map to 0 ~ 240
        # theta3 += 120  # -120 ~ 120 map to 0 ~ 240
        logger.debug(
            f"theta1 = {theta1:.1f}, theta2 = {theta2:.1f}, theta3 = {theta3:.1f}"
        )

        if theta3 < 118:
            valid = False

        if theta2 > 168:
            valid = False

        if valid:
            with self._rlock:
                angles = [theta1, theta2, theta3]
                last_angles = [self.last_t1, self.last_t2, self.last_t3]
                max_angle = -1
                for a, b in zip(angles, last_angles):
                    if abs(a - b) > max_angle:
                        max_angle = abs(a - b)
                t = max_angle / self._speed  # 单位 ms
                self.j1.run_time = int(t)
                self.j2.run_time = int(t)
                self.j3.run_time = int(t)
                self.j1.set_angle(theta1)
                self.j2.set_angle(theta2)
                self.j3.set_angle(theta3)
                self.last_t1 = theta1
                self.last_t2 = theta2
                self.last_t3 = theta3

                self.jall.action()

        return t

    def moveL(self, x, y, z):
        t = -1
        ret, a1, a2, a3 = self.solveIK(x, y, z)
        if ret:
            with self._rlock:
                t = self.moveJ(a1, a2, a3)
                self._user_x = x
                self._user_y = y
                self._user_z = z
                if t > 0:
                    a1 = int(a1)
                    a2 = int(a2)
                    a3 = int(a3)
                    self.T_g2b = self.get_T([a1, a2, a3])
        return t

    def release(self):
        with self._rlock:
            self._release_flag = True
            self.jall.release()

    def lock(self):
        with self._rlock:
            self._release_flag = False
            self.jall.lock()

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

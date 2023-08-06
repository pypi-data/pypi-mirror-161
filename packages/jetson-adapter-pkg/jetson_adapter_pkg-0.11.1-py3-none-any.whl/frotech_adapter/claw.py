from .utils import PORT, BAUDRATE
from .serialServo import SerialServo


def _clamp(value, max=1, min=0):
    if value is not None:
        if value > max:
            value = max
        elif value < min:
            value = min
    return value


class Claw(object):
    def __init__(self, port=PORT, baudrate=BAUDRATE, *args, **kwargs):
        super(Claw, self).__init__(*args, **kwargs)
        self._left_servo = SerialServo("left", port=port, baudrate=baudrate)
        self._right_servo = SerialServo("right")

    def do_grab(self, value=1., grab_time=2000):
        value = float(value)
        value = _clamp(value)
        upper = self._left_servo.limit_range[1]
        lower = self._left_servo.limit_range[0]
        pos = value * (upper - lower) + lower
        self._right_servo.run_time = grab_time
        self._left_servo.run_time = int(grab_time * 0.6)
        self._left_servo.set_pos(pos, retry=5)
        self._right_servo.set_pos(pos, retry=5)

    def do_release(self, value=1., release_time=1000):
        value = float(value)
        value = _clamp(value)
        upper = self._left_servo.limit_range[1]
        lower = self._left_servo.limit_range[0]
        pos = value * (lower - upper) + upper
        self._left_servo.run_time = release_time
        self._right_servo.run_time = release_time
        self._left_servo.set_pos(pos, retry=5)
        self._right_servo.set_pos(pos, retry=5)

    def set_position(self, left_pos=None, right_pos=None, runtime=1500):
        left_pos = _clamp(left_pos)
        right_pos = _clamp(right_pos)
        upper = self._left_servo.limit_range[1]
        lower = self._left_servo.limit_range[0]
        if left_pos is not None:
            left_pos = left_pos * (lower - upper) + upper
            self._left_servo.position = 0xffff
        else:
            left_pos = 0xffff

        if right_pos is not None:
            right_pos = right_pos * (lower - upper) + upper
            self._right_servo.position = 0xffff
        else:
            right_pos = 0xffff

        self._left_servo.run_time = runtime
        self._right_servo.run_time = runtime
        self._left_servo.set_pos(left_pos, retry=5)
        self._right_servo.set_pos(right_pos, retry=5)

    def release(self):
        self._right_servo.release()
        self._left_servo.release()

    def lock(self):
        self._right_servo.lock()
        self._left_servo.lock()

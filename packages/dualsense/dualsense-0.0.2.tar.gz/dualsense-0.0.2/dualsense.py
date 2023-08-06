import evdev
import asyncio

def deadband(val, dead):
    if val > dead:
        return val - dead
    elif val < -dead:
        return val + dead
    else:
        return 0

class DualSenseController:
    DEVICE_NAME = 'Wireless Controller'

    DEADBAND = 2

    # buttons
    BTN_CROSS = (1, 304)
    BTN_TRIANGLE = (1, 307)
    BTN_CIRCLE = (1, 305)
    BTN_SQUARE = (1, 308)
    BTN_TRIG_L = (1, 310)
    BTN_TRIG_R = (1, 311)
    BTN_CREATE = (1, 314)
    BTN_OPTIONS = (1, 315)
    BTN_PLAYSTATION = (1, 316)
    BTN_L_JOY = (1, 317)
    BTN_R_JOY = (1, 318)

    # arrows
    BTN_LR = (3, 16)
    BTN_UD = (3, 17)

    # joysticks
    JOY_L_X = (3, 0)
    JOY_L_Y = (3, 1)
    JOY_R_X = (3, 3)
    JOY_R_Y = (3, 4)

    # triggers
    TRIG_L2 = (3, 2)
    TRIG_R2 = (3, 5)

    INDEXES = [
        BTN_CROSS,
        BTN_TRIANGLE,
        BTN_CIRCLE,
        BTN_SQUARE,
        BTN_CREATE,
        BTN_OPTIONS,
        BTN_PLAYSTATION,
        BTN_L_JOY,
        BTN_R_JOY,
        BTN_LR,
        BTN_UD,
        JOY_L_X,
        JOY_L_Y,
        JOY_R_X,
        JOY_R_Y,
        TRIG_L2,
        TRIG_R2,
    ]

    def __init__(self, device: evdev.InputDevice) -> None:
        self.device: evdev.InputDevice = device
        self._state = {}

    @classmethod
    def find_controller(cls, desired_index: int = 0):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        current_index = 0
        for device in devices:
            # print(device.path, 
            if device.name == cls.DEVICE_NAME:
                if current_index == desired_index:
                    self = cls(device)
                    break
                else:
                    current_index += 1
        else:
            raise ValueError(f'unable to find dualsense controller with index {desired_index}')
        return self

    async def arun(self):
        async for ev in self.device.async_read_loop():
            assert isinstance(ev, evdev.InputEvent)
            index = (ev.type, ev.code)
            self._state[index] = ev.value

    @property
    def cross(self):
        return bool(self._state.get(self.BTN_CROSS, 0))

    @property
    def triangle(self):
        return bool(self._state.get(self.BTN_TRIANGLE, 0))

    @property
    def circle(self):
        return bool(self._state.get(self.BTN_CIRCLE, 0))

    @property
    def square(self):
        return bool(self._state.get(self.BTN_SQUARE, 0))

    @property
    def create(self):
        return bool(self._state.get(self.BTN_CREATE, 0))

    @property
    def options(self):
        return bool(self._state.get(self.BTN_OPTIONS, 0))

    @property
    def playstation(self):
        return bool(self._state.get(self.BTN_PLAYSTATION, 0))

    @property
    def btn_l_joy(self):
        return bool(self._state.get(self.BTN_L_JOY, 0))

    @property
    def btn_r_joy(self):
        return bool(self._state.get(self.BTN_R_JOY, 0))

    @property
    def btn_lr(self):
        center = 0
        return self._state.get(self.BTN_LR, center) - center

    @property
    def btn_ud(self):
        center = 0
        return self._state.get(self.BTN_UD, center) - center

    @property
    def joy_l_x(self):
        center = 127
        return deadband(self._state.get(self.JOY_L_X, center) - center, self.DEADBAND)

    @property
    def joy_l_y(self):
        center = 127
        return -deadband(self._state.get(self.JOY_L_Y, center) - center, self.DEADBAND)

    @property
    def joy_r_x(self):
        center = 127
        return deadband(self._state.get(self.JOY_R_X, center) - center, self.DEADBAND)

    @property
    def joy_r_y(self):
        center = 127
        return -deadband(self._state.get(self.JOY_R_Y, center) - center, self.DEADBAND)

    @property
    def trig_l2(self):
        center = 0
        return deadband(self._state.get(self.TRIG_L2, center) - center, self.DEADBAND)

    @property
    def trig_r2(self):
        center = 0
        return deadband(self._state.get(self.TRIG_R2, center) - center, self.DEADBAND)

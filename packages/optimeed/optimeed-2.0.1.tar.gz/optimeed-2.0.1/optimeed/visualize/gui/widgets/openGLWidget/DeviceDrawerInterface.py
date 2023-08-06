from abc import ABCMeta, abstractmethod


class DeviceDrawerInterface(metaclass=ABCMeta):
    @abstractmethod
    def draw(self, theDevice):
        pass

    @abstractmethod
    def get_init_camera(self, theDevice):
        pass

    def keyboard_push_action(self, theKey):
        pass

    def get_colour_scalebar(self):
        return [0.8, 0.84, 0.9]

    def get_colour_background(self):
        return [0.2, 0.2, 0.2]

    def get_opengl_options(self):
        pass

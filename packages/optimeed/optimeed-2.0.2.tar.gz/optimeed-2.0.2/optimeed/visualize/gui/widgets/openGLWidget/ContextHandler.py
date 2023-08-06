import math
import numpy as np
from OpenGL.GL import *

from . import quaternions


MODE_ZOOM = 0
MODE_ROTATION = 1
MODE_LIGHT = 2
NUMBER_OF_MODES = 3

CLIC_LEFT = 0
CLIC_RIGHT = 1


class SpecialButtonsMapping:
    def __init__(self):
        self.KEY_LEFT = None
        self.KEY_RIGHT = None
        self.KEY_UP = None
        self.KEY_DOWN = None
        self.KEY_TAB = None
        self.MOUSE_LEFT = None
        self.MOUSE_RIGHT = None


class MyText:
    def __init__(self, color, fontSize, theStr, windowPosition):
        self.color = color
        self.fontSize = fontSize
        self.position = windowPosition
        self.theStr = theStr


class ContextHandler:

    def __init__(self):
        self.rotation_accumulation = (1, 0, 0, 0)
        self.width = 200
        self.height = 200

        self.theDeviceDrawer = None
        self.theDeviceToDraw = None
        self.theSpecialButtonsMapping = None

        # Initial viewPoint and light
        self.__displayScale__ = False
        self.scaleLength = 5

        self.tipAngle, self.viewAngle, self.zoomLevel = 10, 10, 40

        self.must_rotate = True
        self.lightPosition = [-16100.0, 15900.0, 0.0, 1.0]

        self.backgroundColor = [0.3, 0.3, 0.3]

        self.centerPosition = [0, 0, 0]

        self.xMouseOnClic = 0
        self.yMouseOnClic = 0

        self.currentMode = MODE_ROTATION
        self.currentClic = CLIC_LEFT

        try:
            self.VP_MarginW
        except AttributeError:
            self.VP_MarginW = 0
            self.VP_MarginH = 0
            self.VP_W = self.width
            self.VP_H = self.height

    def set_specialButtonsMapping(self, theSpecialButtonsMapping):
        self.theSpecialButtonsMapping = theSpecialButtonsMapping

    def set_deviceDrawer(self, theDeviceDrawer):
        self.theDeviceDrawer = theDeviceDrawer

    def set_deviceToDraw(self, theDeviceToDraw):
        if self.theDeviceToDraw is None:
            self.theDeviceToDraw = theDeviceToDraw
            _, _, self.zoomLevel = self.theDeviceDrawer.get_init_camera(self.theDeviceToDraw)
        else:
            self.theDeviceToDraw = theDeviceToDraw

    def resizeWindowAction(self, new_width, new_height):
        ar_origin = self.width / self.height
        ar_new = new_width / new_height

        scale_w = new_width / self.width
        scale_h = new_height / self.height

        if ar_new > ar_origin:
            scale_w = scale_h
        else:
            scale_h = scale_w

        margin_x = (new_width - self.width * scale_w / ar_origin) / 2
        margin_y = (new_height - self.height * scale_h) / 2
        self.VP_H = int(self.height * scale_h)
        self.VP_W = int(self.width * scale_w / ar_origin)
        self.VP_MarginH = int(margin_y)
        self.VP_MarginW = int(margin_x)

    def mouseWheelAction(self, deltaAngle):
        self.zoomLevel += 0.1 * self.zoomLevel * deltaAngle

        # GLUT.glutPostRedisplay()

    def mouseClicAction(self, button, my_x, y):
        self.xMouseOnClic = my_x
        self.yMouseOnClic = y
        self.currentClic = button

    def mouseMotionAction(self, my_x, y):
        if self.currentClic == self.theSpecialButtonsMapping.MOUSE_LEFT:
            if self.currentMode == MODE_ROTATION:
                self.viewAngle = -(my_x - self.xMouseOnClic) * 0.8
                self.tipAngle = -(y - self.yMouseOnClic) * 0.8
                self.must_rotate = True
            elif self.currentMode == MODE_ZOOM:
                self.zoomLevel *= (1 - 0.005 * (y - self.yMouseOnClic))
            elif self.currentMode == MODE_LIGHT:
                self.lightPosition[0] += (my_x - self.xMouseOnClic) * 100
                self.lightPosition[1] += (y - self.yMouseOnClic) * 100
            else:
                pass
        elif self.currentClic == self.theSpecialButtonsMapping.MOUSE_RIGHT:
            self.centerPosition[0] += (my_x - self.xMouseOnClic) / 1000 * 3
            self.centerPosition[1] -= (y - self.yMouseOnClic) / 1000 * 3
        self.xMouseOnClic = my_x
        self.yMouseOnClic = y

        # GLUT.glutPostRedisplay()

    def keyboardPushAction(self, key):
        # print(chr(key))
        if key == ord(b'+'):
            self.zoomLevel += 0.1 * self.zoomLevel
        elif key == ord(b'-'):
            self.zoomLevel -= 0.1 * self.zoomLevel
        elif key == ord(b'M'):
            self.currentMode += 1
            if self.currentMode >= NUMBER_OF_MODES:
                self.currentMode -= NUMBER_OF_MODES
        # elif key == b'\x1b':
        #         self.stop = True
        # ScaleLength management
        elif key == ord(b'S'):
            self.__displayScale__ = not self.__displayScale__
        elif key == ord(b'>'):
            self.scaleLength += 1
        elif key == ord(b'<'):
            self.scaleLength -= 1
        # Rotation Management
        elif key == self.theSpecialButtonsMapping.KEY_LEFT:
            self.viewAngle = -2
            self.must_rotate = True
        elif key == self.theSpecialButtonsMapping.KEY_RIGHT:
            self.viewAngle = +2
            self.must_rotate = True
        elif key == self.theSpecialButtonsMapping.KEY_UP:
            self.tipAngle = +2
            self.must_rotate = True
        elif key == self.theSpecialButtonsMapping.KEY_DOWN:
            self.tipAngle = -2
            self.must_rotate = True
        elif key == ord(b'X'):
            self.tipAngle = 0
            self.viewAngle = 0
            self.rotation_accumulation = (1, 0, 0, 0)
            self.must_rotate = True
        elif key == ord(b'Y'):
            self.tipAngle = 0
            self.viewAngle = 90
            self.rotation_accumulation = (1, 0, 0, 0)
            self.must_rotate = True
        elif key == ord(b'Z'):
            self.tipAngle = 90
            self.viewAngle = 90
            self.rotation_accumulation = (1, 0, 0, 0)
            self.must_rotate = True
        elif key == ord(b'R'):
            self.__reset__()
        else:
            self.theDeviceDrawer.keyboard_push_action(key)

    def keyboardReleaseAction(self, key, my_x, y):
        pass

    def __draw_axis__(self):
        if self.__displayScale__:
            glColor3f(*self.theDeviceDrawer.get_colour_scalebar())

            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)

            relH = 0.0
            relW = 0.0
            glWindowPos2f(self.VP_MarginW + self.VP_W * (1 + relW) / 2 + 4, self.VP_MarginH + self.VP_H * (1 + relH) / 2 + 4)

            glTranslatef(relW, relH, 0)

            glLineWidth(2.5)
            glBegin(GL_LINES)
            glVertex2f(0.0, 0.0)
            glVertex2f(self.zoomLevel / 1000 * self.scaleLength, 0.0)
            glEnd()

            glLineWidth(1.5)
            glBegin(GL_LINES)
            glVertex2f(0.0, 0.0)
            glVertex2f(0.0, 0.02)
            glVertex2f(self.zoomLevel / 1000 * self.scaleLength, 0.0)
            glVertex2f(self.zoomLevel / 1000 * self.scaleLength, 0.02)
            glEnd()

            # theStr = str(self.scaleLength) + 'mm'
            # for char in theStr:
            #     GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord(char))
            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)

    def redraw(self):
        if self.theDeviceDrawer is not None:
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glViewport(self.VP_MarginW, self.VP_MarginH, self.VP_W, self.VP_H)

            # glClearDepth(1)  # just for completeness
            background_color = self.theDeviceDrawer.get_colour_background()
            glClearColor(background_color[0], background_color[1], background_color[2], 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glLightfv(GL_LIGHT0, GL_POSITION, self.lightPosition)

            translationMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [self.centerPosition[0], self.centerPosition[1], 0, 1]])
            scaleMatrix = np.array([[self.zoomLevel, 0, 0, 0], [0, self.zoomLevel, 0, 0], [0, 0, self.zoomLevel, 0], [0, 0, 0, 1]])
            # Operations on matrix
            if self.must_rotate:
                rot_y = quaternions.normalize(quaternions.axisangle_to_q((1.0, 0.0, 0.0), -self.tipAngle / 180 * math.pi))
                rot_x = quaternions.normalize(quaternions.axisangle_to_q((0.0, 1.0, 0.0), -self.viewAngle / 180 * math.pi))
                self.rotation_accumulation = quaternions.q_mult(self.rotation_accumulation, rot_x)
                self.rotation_accumulation = quaternions.q_mult(self.rotation_accumulation, rot_y)
                self.must_rotate = False

            rotationMatrix = quaternions.q_to_mat4(self.rotation_accumulation)
            transfo = np.matmul(scaleMatrix, np.matmul(rotationMatrix, translationMatrix))
            glLoadMatrixf(transfo)

            if self.theDeviceToDraw is not None:
                self.theDeviceDrawer.draw(self.theDeviceToDraw)
            glLoadIdentity()
            self.__draw_axis__()
            glFlush()

    def get_text_to_write(self):
        lineHeight = 20
        fontSize = 12
        textList = list()
        textList.append(MyText([0, 0, 0], fontSize, 'Press [ESC] to exit', [10, self.VP_H - lineHeight]))
        textList.append(MyText([0, 0, 0], fontSize, 'Reset: [R]', [10, self.VP_H - 2 * lineHeight]))

        textList.append(MyText([0, 0, 0], fontSize, 'Toggle/hide scale: [S], length control: [<] or [>]', [10, 1 * lineHeight]))
        textList.append(MyText([0, 0, 0], fontSize, 'Axis: [X], [Y], [Z]', [10, 2 * lineHeight]))
        return textList

    def __lightingInit__(self):
        glPushMatrix()
        glLoadIdentity()

        glClearColor(self.backgroundColor[0], self.backgroundColor[1], self.backgroundColor[2], 1)
        glShadeModel(GL_SMOOTH)

        glLightfv(GL_LIGHT0, GL_POSITION, self.lightPosition)

        glLightfv(GL_LIGHT0, GL_SPECULAR, [6, 6, 6])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [3, 3, 3])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.6])

        glLightfv(GL_LIGHT1, GL_POSITION, [22300.0, -55800.0, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.8, 0.8, 0.8])
        # glLightfv(GL_LIGHT1, GL_AMBIENT, [2, 2, 2])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.4, 0.4, 0.4])
        glLightfv(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glPopMatrix()

    def initialize(self):
        self.__lightingInit__()
        self.theDeviceDrawer.get_opengl_options()
        self.tipAngle, self.viewAngle, self.zoomLevel = self.theDeviceDrawer.get_init_camera(self.theDeviceToDraw)

    def __reset__(self):
        deviceDrawer = self.theDeviceDrawer
        deviceToDraw = self.theDeviceToDraw
        keymap = self.theSpecialButtonsMapping
        self.__init__()
        self.set_deviceDrawer(deviceDrawer)
        self.set_deviceToDraw(deviceToDraw)
        self.set_specialButtonsMapping(keymap)


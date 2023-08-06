import math

from OpenGL.GL import *
from OpenGL.GLU import *

from .TriangulatePolygon import meshPolygon


def draw_closedPolygon(xClockWise, yClockWise):
    theTriList = meshPolygon(xClockWise, yClockWise)

    glBegin(GL_TRIANGLES)
    for (p1, p2, p3) in theTriList:
        glVertex2f(p1[0], p1[1])
        glVertex2f(p2[0], p2[1])
        glVertex2f(p3[0], p3[1])
    glEnd()


def draw_extrudeZ(xList, yList, zExtrude):
    glBegin(GL_QUAD_STRIP)
    for i in range(len(xList)):
        glVertex3f(xList[i], yList[i], 0.0)
        glVertex3f(xList[i], yList[i], zExtrude)
    glEnd()


def draw_triList(theTriList):
    glBegin(GL_TRIANGLES)
    for (p1, p2, p3) in theTriList:
        glVertex2f(p1[0], p1[1])
        glVertex2f(p2[0], p2[1])
        glVertex2f(p3[0], p3[1])
    glEnd()


def draw_lines(x, z):
    if len(x) < 2:
        return
    glBegin(GL_LINE_STRIP)
    for i in range(len(x)):
        glVertex2f(x[i], z[i])
    glEnd()


def draw_spiralSheet(innerRadius, thickness, length, theAngle, n, reverseDirection=False):
    if reverseDirection:
        glFrontFace(GL_CW)

    a = innerRadius
    b = thickness / (2 * math.pi)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(n + 1):
        angle = i / n * theAngle
        radius = a + b * angle
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex(x, y, length)
        glVertex(x, y, 0)
        glNormal3f(x, y, 0)
    glEnd()

    glFrontFace(GL_CCW)


def draw_spiralFront(innerRadius, thicknessMaterial, thicknessSpiral, z0, theAngle, n, reverseDirection=False):
    a = innerRadius
    b = thicknessSpiral / (2 * math.pi)
    glBegin(GL_QUAD_STRIP)
    numberOfPoints = n
    rIn = innerRadius
    for i in range(numberOfPoints + 1):
        if reverseDirection:
            angle = (n - i) / n * theAngle
        else:
            angle = i / n * theAngle
        rIn = a + b * angle
        rOut = rIn + thicknessMaterial
        glVertex3f(rIn * math.cos(angle), rIn * math.sin(angle), z0)
        glVertex3f(rOut * math.cos(angle), rOut * math.sin(angle), z0)
        glNormal3f(0, 0, 1)
    glEnd()


def draw_spiralFull(innerRadius, outerRadius, thicknessMaterial, thicknessSpiral, length, n):
    if outerRadius - innerRadius < thicknessMaterial:
        return
    nTurns = ((outerRadius - thicknessMaterial) - innerRadius) / thicknessSpiral
    theta_tot = nTurns * 2 * math.pi
    draw_spiralSheet(innerRadius, thicknessSpiral, length, theta_tot, n)
    draw_spiralSheet(innerRadius + thicknessMaterial, thicknessSpiral, length, theta_tot, n)
    draw_spiralFront(innerRadius, thicknessMaterial, thicknessSpiral, 0, theta_tot, n)
    draw_spiralFront(innerRadius, thicknessMaterial, thicknessSpiral, length, theta_tot, n)


def draw_spiral(innerRadius, outerRadius, thicknessMaterial, thicknessSpiral, length, cutAngle, n):
    if outerRadius - innerRadius < thicknessMaterial:
        return

    glPushMatrix()
    glTranslate(0, 0, -length / 2)

    a = innerRadius
    b = thicknessSpiral / (2 * math.pi)

    nTurns = ((outerRadius - thicknessMaterial) - innerRadius) / thicknessSpiral
    theta_last = (nTurns - math.floor(nTurns)) * 2 * math.pi
    for i in range(int(math.floor(nTurns))):
        currentAngle = i * 2 * math.pi
        rIn = a + b * currentAngle
        currentAngle2 = i * 2 * math.pi + cutAngle
        rIn2 = a + b * currentAngle2

        draw_spiralSheet(rIn, thicknessSpiral, length, cutAngle, n, False)
        draw_spiralSheet(rIn + thicknessMaterial, thicknessSpiral, length, cutAngle, n, True)
        draw_spiralFront(rIn, thicknessMaterial, thicknessSpiral, 0, cutAngle, n, True)
        draw_spiralFront(rIn, thicknessMaterial, thicknessSpiral, length, cutAngle, n)
        draw_rectangle(rIn, length, thicknessMaterial, 0, True)
        draw_rectangle(rIn2, length, thicknessMaterial, cutAngle)

    if theta_last > 0:
        currentAngle = math.floor(nTurns) * 2 * math.pi
        rIn = a + b * currentAngle
        currentAngle2 = math.floor(nTurns) * 2 * math.pi + min(cutAngle, theta_last)
        rIn2 = a + b * currentAngle2

        angleToGo = min(cutAngle, theta_last)
        draw_spiralSheet(rIn, thicknessSpiral, length, angleToGo, n, True)
        draw_spiralSheet(rIn + thicknessMaterial, thicknessSpiral, length, angleToGo, n, False)
        draw_spiralFront(rIn, thicknessMaterial, thicknessSpiral, 0, angleToGo, n, True)
        draw_spiralFront(rIn, thicknessMaterial, thicknessSpiral, length, angleToGo, n)
        draw_rectangle(rIn, length, thicknessMaterial, 0, True)
        draw_rectangle(rIn2, length, thicknessMaterial, angleToGo)

    glPopMatrix()


def draw_simple_rectangle(width, height):
    glRectf(0, 0, width, height)


def draw_rectangle(rIn, length, thickness, angle, reverseDirection=False):
    if reverseDirection:
        glFrontFace(GL_CW)

    glPushMatrix()
    if reverseDirection:
        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
    else:
        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
    glRotatef(angle * 180 / math.pi, 1, 0, 0)
    glRectf(length, thickness + rIn, 0, rIn)
    glPopMatrix()

    glFrontFace(GL_CCW)


def draw_2Dring(innerRadius, outerRadius, z0, theAngle, n, reverseDirection=False):
    if 2 * math.pi * 0.95 < theAngle < 2 * math.pi * 1.05:
        draw_disk(innerRadius, outerRadius, n, z0)
    else:
        glBegin(GL_QUAD_STRIP)
        numberOfPoints = n
        rIn = innerRadius
        rOut = outerRadius
        for i in range(numberOfPoints + 1):
            if reverseDirection:
                angle = (n - i) / numberOfPoints * theAngle
            else:
                angle = i / numberOfPoints * theAngle
            glVertex3f(rIn * math.cos(angle), rIn * math.sin(angle), z0)
            glVertex3f(rOut * math.cos(angle), rOut * math.sin(angle), z0)
            glNormal3f(0, 0, 1)
        glEnd()


def draw_2Dring_diff_angle(innerRadius, outerRadius, angle_in, angle_out, n, reverseDirection=False):
    glBegin(GL_QUAD_STRIP)
    numberOfPoints = n
    rIn = innerRadius
    rOut = outerRadius
    for i in range(numberOfPoints + 1):
        if reverseDirection:
            angle1 = -angle_in/2 + (n - i) / numberOfPoints * angle_in
            angle2 = -angle_out/2 + (n - i) / numberOfPoints * angle_out
        else:
            angle1 = -angle_in/2 + i / numberOfPoints * angle_in
            angle2 = -angle_out/2 + i / numberOfPoints * angle_out
        glVertex3f(rIn * math.cos(angle1), rIn * math.sin(angle1), 0)
        glVertex3f(rOut * math.cos(angle2), rOut * math.sin(angle2), 0)
        glNormal3f(0, 0, 1)
    glEnd()


def draw_tubeSheet(radius, length, theAngle, n, reverseDirection=False):
    circle_pts = []
    for i in range(n + 1):
        if reverseDirection:
            angle = -theAngle/2 + theAngle * ((n - i) / n)
        else:
            angle = -theAngle/2 + theAngle * (i / n)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        pt = [x, y]
        circle_pts.append(pt)

    glBegin(GL_TRIANGLE_STRIP)
    for [x, y] in circle_pts:
        if reverseDirection:
            glVertex(x, y, length)
            glVertex(x, y, 0)

        else:
            glVertex(x, y, length)
            glVertex(x, y, 0)
        glNormal3f(x, y, 0)
    glEnd()


def draw_cylinder(innerRadius, outerRadius, length, n, translate=0):
    glPushMatrix()
    glTranslate(0, 0, translate)
    rIn = innerRadius
    rOut = outerRadius
    gluCylinder(gluNewQuadric(), rIn, rIn, length, n, n)  # Lightning ko but interface ok :x
    gluCylinder(gluNewQuadric(), rOut, rOut, length, n, n)
    gluDisk(gluNewQuadric(), rIn, rOut, n, n)
    glTranslate(0, 0, length)
    gluDisk(gluNewQuadric(), rIn, rOut, n, n)
    glPopMatrix()


# Angle in radians
def draw_part_cylinder(innerRadius, outerRadius, length, angle, n, translate=0, drawSides=True):
    if 2 * math.pi * 0.95 < angle < 2 * math.pi * 1.05:
        draw_cylinder(innerRadius, outerRadius, length, n, translate)
    else:
        glPushMatrix()
        glTranslate(0, 0, translate - length / 2)

        rIn = innerRadius
        rOut = outerRadius
        if drawSides:
            draw_tubeSheet(rIn, length, angle, n, True)
            draw_tubeSheet(rOut, length, angle, n, False)
        draw_2Dring(rIn, rOut, 0, angle, n, True)
        draw_2Dring(rIn, rOut, length, angle, n, False)
        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)

        glFrontFace(GL_CW)
        glRectf(length, outerRadius, 0, 0 + innerRadius)
        glFrontFace(GL_CCW)

        glRotatef(angle * 180 / math.pi, 1, 0, 0)
        glRectf(length, outerRadius, 0, 0 + innerRadius)
        glPopMatrix()


# Angle in radians
def draw_disk(innerRadius, outerRadius, n, translate=0):
    glPushMatrix()
    glTranslate(0, 0, translate)
    gluDisk(gluNewQuadric(), innerRadius, outerRadius, n, n)
    glPopMatrix()


# Angle in radians
def draw_part_disk(innerRadius, outerRadius, thickness, angle, n, translate=0):
    glPushMatrix()
    glTranslate(0, 0, translate)

    rIn = innerRadius
    rOut = outerRadius
    draw_tubeSheet(rIn, thickness, angle, n, True)
    draw_tubeSheet(rOut, thickness, angle, n, False)
    draw_2Dring(rIn, rOut, 0, angle, n, True)
    draw_2Dring(rIn, rOut, thickness, angle, n, False)
    glRotatef(-90, 0, 1, 0)
    glRotatef(-90, 1, 0, 0)

    glFrontFace(GL_CW)
    glRectf(thickness, rOut, 0, 0 + innerRadius)
    glFrontFace(GL_CCW)

    glRotatef(angle * 180 / math.pi, 1, 0, 0)
    glRectf(thickness, rOut, 0, 0 + innerRadius)
    glPopMatrix()


# Angle in radians
def draw_part_disk_diff_angles(innerRadius, outerRadius, thickness, angle_in, angle_out, n):
    rIn = innerRadius
    rOut = outerRadius
    draw_tubeSheet(rIn, thickness, angle_in, n, True)
    draw_tubeSheet(rOut, thickness, angle_out, n, False)

    draw_2Dring_diff_angle(innerRadius, outerRadius, angle_in, angle_out, n, True)

    glPushMatrix()
    glTranslate(0, 0, thickness)
    draw_2Dring_diff_angle(innerRadius, outerRadius, angle_in, angle_out, n, False)
    glPopMatrix()

    for dir_num, dir_angle in [(GL_CW, 1), (GL_CCW, -1)]:
        glFrontFace(dir_num)
        glBegin(GL_QUAD_STRIP)
        glVertex3f(rIn * math.cos(dir_angle*angle_in/2), rIn * math.sin(dir_angle*angle_in/2), 0)
        glVertex3f(rIn * math.cos(dir_angle*angle_in/2), rIn * math.sin(dir_angle*angle_in/2), thickness)
        glVertex3f(rOut * math.cos(dir_angle*angle_out/2), rOut * math.sin(dir_angle*angle_out/2), 0)
        glVertex3f(rOut * math.cos(dir_angle*angle_out/2), rOut * math.sin(dir_angle*angle_out/2), thickness)
        glEnd()


# Angle in radians
def draw_carved_disk(innerRadius, outerRadius, carvedRin, carvedRout, thickness, depth, angle, n, translate=0):
    glPushMatrix()
    glTranslate(0, 0, translate)

    rIn = innerRadius
    rOut = outerRadius
    rInOut = carvedRin
    rOutIn = carvedRout

    if depth > thickness:
        if rInOut > rIn:
            draw_tubeSheet(rIn, thickness, angle, n, True)
            draw_tubeSheet(rInOut, thickness, angle, n, False)
            draw_2Dring(rIn, rInOut, 0, angle, n, True)
            draw_2Dring(rIn, rInOut, thickness, angle, n, False)
        if rOut > rOutIn:
            draw_tubeSheet(rOutIn, thickness, angle, n, True)
            draw_tubeSheet(rOut, thickness, angle, n, False)
            draw_2Dring(rOutIn, rOut, 0, angle, n, True)
            draw_2Dring(rOutIn, rOut, thickness, angle, n, False)

        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)

        glFrontFace(GL_CW)
        if rOut > rOutIn:
            glRectf(thickness, rOut, 0, rOutIn)
        if rInOut > rIn:
            glRectf(thickness, rInOut, 0, rIn)
        glFrontFace(GL_CCW)

        glRotatef(angle * 180 / math.pi, 1, 0, 0)
        if rOut > rOutIn:
            glRectf(thickness, rOut, 0, rOutIn)
        if rInOut > rIn:
            glRectf(thickness, rInOut, 0, rIn)
        glPopMatrix()

    else:
        extremeIn = rInOut
        extremeOut = rOutIn

        if rInOut <= rIn:
            extremeIn = rIn
            draw_tubeSheet(rIn, thickness - depth, angle, n, True)
        else:
            draw_tubeSheet(rIn, thickness, angle, n, True)
            draw_tubeSheet(rInOut, thickness, angle, n, False)
            draw_2Dring(rIn, rInOut, thickness, angle, n, False)

        if rOutIn >= rOut:
            extremeIn = rOut
            draw_tubeSheet(rOut, thickness - depth, angle, n, False)
        else:
            draw_tubeSheet(rOut, thickness, angle, n, False)
            draw_tubeSheet(rOutIn, thickness, angle, n, True)
            draw_2Dring(rOutIn, rOut, thickness, angle, n, False)

        draw_2Dring(extremeIn, extremeOut, thickness - depth, angle, n, False)
        draw_2Dring(rIn, rOut, 0, angle, n, True)

        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)

        glFrontFace(GL_CW)
        glRectf(thickness - depth, extremeOut, 0, extremeIn)
        if rOut > extremeOut:
            glRectf(thickness, rOut, 0, extremeOut)
        if rIn < extremeIn:
            glRectf(thickness, extremeIn, 0, rIn)
        glFrontFace(GL_CCW)

        glRotatef(angle * 180 / math.pi, 1, 0, 0)
        glRectf(thickness - depth, extremeOut, 0, extremeIn)
        if rOut > extremeOut:
            glRectf(thickness, rOut, 0, extremeOut)
        if rIn < extremeIn:
            glRectf(thickness, extremeIn, 0, rIn)
        glPopMatrix()


def draw_part_cylinder_throat(rIn, rOut, rOutThroat, length, lengthThroat, angle, n, translate=0):
    glPushMatrix()
    glTranslate(0, 0, translate - length / 2)

    glPushMatrix()
    glTranslate(0, 0, (length + lengthThroat) / 2)
    draw_tubeSheet(rOut, (length - lengthThroat) / 2, angle, n, False)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0, 0, (length - lengthThroat) / 2)
    draw_tubeSheet(rOutThroat, lengthThroat, angle, n, False)
    glPopMatrix()

    draw_tubeSheet(rOut, (length - lengthThroat) / 2, angle, n, False)

    draw_tubeSheet(rIn, length, angle, n, True)

    draw_2Dring(rIn, rOut, length, angle, n, False)  # weird shadow :(
    draw_2Dring(rOutThroat, rOut, (length + lengthThroat) / 2, angle, n, True)
    draw_2Dring(rOutThroat, rOut, (length - lengthThroat) / 2, angle, n, False)
    draw_2Dring(rIn, rOut, 0, angle, n, True)

    draw_rectangle(rIn, (length - lengthThroat) / 2, rOut - rIn, 0, True)

    glPushMatrix()
    glTranslate(0, 0, (length - lengthThroat) / 2)
    draw_rectangle(rIn, lengthThroat, rOutThroat - rIn, 0, True)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0, 0, (length + lengthThroat) / 2)
    draw_rectangle(rIn, (length - lengthThroat) / 2, rOut - rIn, 0, True)
    glPopMatrix()

    draw_rectangle(rIn, (length - lengthThroat) / 2, rOut - rIn, angle, False)

    glPushMatrix()
    glTranslate(0, 0, (length - lengthThroat) / 2)
    draw_rectangle(rIn, lengthThroat, rOutThroat - rIn, angle, False)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0, 0, (length + lengthThroat) / 2)
    draw_rectangle(rIn, (length - lengthThroat) / 2, rOut - rIn, angle, False)
    glPopMatrix()

    glPopMatrix()


def drawWireTube(diameter, xa, ya, xb, yb, n=50, translateZ=0):
    glPushMatrix()
    glTranslate(0, 0, translateZ)
    glTranslate(xa, ya, 0)

    vec = xb - xa, yb - ya
    Norm = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
    vecN = vec[0] / Norm, vec[1] / Norm
    phi = math.acos(math.fabs(vecN[1]))

    if xb < xa:
        if yb > ya:
            Phi = phi
        else:
            Phi = math.pi - phi
    else:
        if yb > ya:
            Phi = - phi
        else:
            Phi = -math.pi + phi
    glRotatef(Phi * 180 / math.pi, 0, 0, 1)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), diameter / 2, diameter / 2, Norm, n, n)
    glPopMatrix()

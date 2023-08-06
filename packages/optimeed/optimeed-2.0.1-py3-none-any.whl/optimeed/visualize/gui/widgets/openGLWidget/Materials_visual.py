from OpenGL.GL import *


class MaterialRenderingProperties:
    __spec3__ = [0, 0, 0, 0]
    __dif3__ = [0, 0, 0, 0]
    __amb3__ = [0, 0, 0, 0]
    __shin__ = 0

    def __init__(self, amb3, dif3, spec3, shin):
        self.__spec3__ = spec3
        self.__dif3__ = dif3
        self.__amb3__ = amb3
        self.__shin__ = shin

    def getSpec3(self):
        return self.__spec3__

    def getDif3(self):
        return self.__dif3__

    def getAmb3(self):
        return self.__amb3__

    def getShin(self):
        return self.__shin__

    def activateMaterialProperties(self, alpha=1):
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.__spec3__ + [alpha])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.__dif3__ + [alpha])
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.__amb3__ + [alpha])
        glMaterialfv(GL_FRONT, GL_SHININESS, self.__shin__ * 128)


Emerald_material = MaterialRenderingProperties([0.0215, 0.1745, 0.0215], [0.0758, 0.61424, 0.0758], [0.633, 0.7278, 0.633], 0.6)
Yellow_Emerald_material = MaterialRenderingProperties([0.545, 0.4015, 0.1215], [0.0758, 0.61424, 0.0758], [0.633, 0.7278, 0.633], 0.6)
Brass_material = MaterialRenderingProperties([0.329412, 0.223529, 0.02745], [0.780392, 0.568627, 0.113725], [0.992157, 0.941176, 0.807843], 0.21794872)
Bronze_material = MaterialRenderingProperties([0.2125, 0.1275, 0.054], [0.714, 0.4284, 0.18144], [0.393548, 0.271906, 0.166721], 0.2)
Silver_material = MaterialRenderingProperties([0.19225, 0.19225, 0.19225], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.4)
Steel_material = MaterialRenderingProperties([0.1, 0.1, 0.1], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.4)

Copper_material = MaterialRenderingProperties([0.19125, 0.0735, 0.0225], [0.7038, 0.27048, 0.0828], [0.256777, 0.137622, 0.086014], 0.1)
Chrome_material = MaterialRenderingProperties([0.25, 0.25, 0.25], [0.4, 0.4, 0.4], [0.774597, 0.774597, 0.774597], 0.6)
Blue_material = MaterialRenderingProperties([0, 0, 0.1], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.9)
Red_material = MaterialRenderingProperties([0.1, 0, 0], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.9)
Green_material = MaterialRenderingProperties([0, 0.1, 0], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.9)
Cyan_material = MaterialRenderingProperties([0, 0.1, 0.1], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.9)
Pink_material = MaterialRenderingProperties([0.1, 0.0, 0.1], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.9)

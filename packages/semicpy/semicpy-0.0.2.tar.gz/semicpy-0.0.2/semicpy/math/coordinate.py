"""Coordinate System module
"""

import operator
import numpy as np

class Rectangular2D:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
    x = property(operator.attrgetter('_x'))

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if type(value) != int and type(value) != float:
            raise Exception("x value must be an integer or floating point!")
        self._x = value
    
    y = property(operator.attrgetter('_y'))

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if type(value) != int and type(value) != float:
            raise Exception("y value must be an integer or floating point!")
        self._y = value        

    def distance(self,point):
        return np.hypot(self.x - point.x,self.y - point.y)

    def to_polar(self,point,to_degrees=False):
        r = self.distance(point)
        phi = np.arctan2(point.y,point.x)
        if to_degrees == True:
            return (r,np.rad2deg(phi))
        else:
            return (r,phi)

class Polar:
    def __init__(self,r,phi):
        self.r = r
        self.phi = phi

    r = property(operator.attrgetter('_r'))

    @property
    def r(self):
        return self._r
    
    @r.setter
    def r(self,value):
        if type(value) != int and type(value) != float:
            raise Exception("radius value must be an integer or floating point!")
        if value < 0:
            raise Exception("radius value must be greater than or equal to 0!")
        self._r = value

    phi = property(operator.attrgetter('_phi'))

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self,value):
        if type(value) != int and type(value) != float:
            raise Exception("azimuth value must be an integer or floating point!")
        if (value < 0) or (value >= (2 * np.pi)):
            raise Exception("azimuth value must be within [0,2pi)!")
        self._phi = value

    def to_rectangular(self):
        x = self.r * np.cos(self.phi)
        y = self.r * np.sin(self.phi)
        return (x,y)

class Rectangular3D:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    
    x = property(operator.attrgetter('_x'))

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if type(value) != int and type(value) != float:
            raise Exception("x value must be an integer or floating point!")
        self._x = value
    
    y = property(operator.attrgetter('_y'))

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if type(value) != int and type(value) != float:
            raise Exception("y value must be an integer or floating point!")
        self._y = value        

    z = property(operator.attrgetter('_z'))

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self,value):
        if type(value) != int and type(value) != float:
            raise Exception("z value must be an integer or floating point!")
        self._z = value

    def distance(self,point):
        return np.sqrt(np.square(self.x - point.x) + np.square(self.y - point.y) + np.square(self.z - point.z))
    
    def to_spherical(self,point,to_degrees=False):
        r = self.distance(point)
        theta = np.arccos(point.z / r)
        phi = np.arctan2(point.y,point.x)

        if to_degrees == True:
            return (r,np.rad2deg(theta),np.rad2deg(phi))
        else:
            return (r,theta,phi)

class Spherical:
    def __init__(self,r,theta,phi):
        self.r = r
        self.theta = theta
        self.phi = phi
    
    r = property(operator.attrgetter('_r'))

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        if type(value) != int and type(value) != float:
            raise Exception("radius value must be an integer or floating point!")
        if value < 0:
            raise Exception("radius value must be 0 or greater!")
        self._r = value
    
    theta = property(operator.attrgetter('_theta'))

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value):
        if type(value) != int and type(value) != float:
            raise Exception("polar value must be an integer or floating point!")
        if (value < 0) or (value > np.pi):
            raise Exception("polar value must be within [0,pi]!")
        self._theta = value        

    phi = property(operator.attrgetter('_phi'))

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self,value):
        if type(value) != int and type(value) != float:
            raise Exception("azimuth value must be an integer or floating point!")
        if (value < 0) or (value >= (2 * np.pi)):
            raise Exception("azimuth value must be within [0,2pi)!")
        self._phi = value
    
    def to_rectangular(self):
        x = self.r * np.cos(self.phi) * np.sin(self.theta)
        y = self.r * np.sin(self.phi) * np.sin(self.theta)
        z = self.r * np.cos(self.theta)

        return (x,y,z)
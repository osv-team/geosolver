"""This module provides a Configuration class. 

A configuration is a set of named points with coordinates."""

import sys

# if sys.version_info[0] > 2:
#     py2 = False
# else:
#     py2 = True
#
# if py2 is True:
#     from sets import Set, ImmutableSet
# else:
#     pass
from geosolver.matfunc import Vec, matrix_factory
from geosolver.intersections import *
from geosolver.tolerance import *

from geosolver.vector import norm, vector, cross


def perp2D(v):
    w = Vec(v)
    w[0] = -v[1]
    w[1] = v[0]
    return w


class Configuration:
    """A set of named points with coordinates of a specified dimension. 
    
       Immutable. Defines equality and a hash function. 
    
       Attributes: 
       map - a dictionary mapping variable names to point values.
       dimension - the dimension of the space in which the configuration is embedded
       underconstrained - flag indicating an underconstrained merge (not a unique solution)
    """
    def __init__(self, map):
        """instantiate a Configuration"""
        self.map = dict(map)
        self.underconstrained = False
        self.dimension = self.checkdimension()
        if self.dimension == 0:
            raise Exception("could not determine dimension of configuration")
        elif self.dimension < 2 or self.dimension > 3:
            raise Exception("no support for "+str(self.dimension)+"-dimensional configurations")
        self.makehash()

    def copy(self):
        """returns a shallow copy"""
        new = Configuration(self.map)
        new.underconstrained = self.underconstrained
        return new

    def vars(self):
        """return list of variables"""
        return self.map.keys()

    def get(self, var):
        """return position of point var"""
        return self.map[var]

    def transform(self, t):
        """returns a new configuration, which is this one transformed by matrix t"""
        newmap = {}
        for v in self.map:
            p = self.map[v]
            ph = Vec(p)
            ph.append(1.0)
            ph = t.mmul(ph)
            p = vector(ph[0:-1]) / ph[-1]
            newmap[v] = p
        return Configuration(newmap)

    def add(self, c):
        """return a new configuration which is this configuration extended with all points in c not in this configuration"""
        newmap = {}
        for v in self.map:
            newmap[v] = self.map[v]
        for v in c.map:
            if v not in newmap:
                newmap[v] = c.map[v]
        return Configuration(newmap)

    def select(self, vars):
        """return a new configuration that is a subconfiguration of this configuration, containing only the selected variables"""
        newmap = {}
        for v in vars:
            newmap[v] = self.map[v]
        return Configuration(newmap)

    def merge(self, other):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""
        t = self.merge_transform(other)
        othertransformed = other.transform(t)
        result = self.add(othertransformed)
        result.underconstrained = t.underconstrained
        return result

    def merge_scale(self, other):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""
        t = self.merge_scale_transform(other)
        othertransformed = other.transform(t)
        result = self.add(othertransformed)
        result.underconstrained = t.underconstrained
        return result

    # NON-PUBLIC

    def merge_transform(self, other):
        if other.dimension != self.dimension:
            raise Exception("cannot merge configurations "
                            "of different dimensions")
        elif self.dimension == 2:
            return self._merge_transform_2D(other)
        else:
            return self._merge_transform_3D(other)

    def merge_scale_transform(self,other):
        if other.dimension != self.dimension:
            raise Exception("cannot merge configurations of different dimensions")
        elif self.dimension == 2:
            return self._merge_scale_transform_2D(other)
        else:
            return self._merge_scale_transform_3D(other)

    def _merge_transform_2D(self, other):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""
        shared = Set(self.vars()).intersection(other.vars())
        underconstrained = self.underconstrained or other.underconstrained
        if len(shared) == 0:
            underconstrained = True
            cs1 = make_hcs_2d(vector([0.0,0.0]), vector([1.0,0.0]))
            cs2 = make_hcs_2d(vector([0.0,0.0]), vector([1.0,0.0]))
        elif len(shared) == 1:
            if len(self.vars()) > 1 and len(other.vars()) > 1:
                underconstrained = True
            v1 = list(shared)[0]
            p11 = self.map[v1]
            p21 = other.map[v1]
            cs1 = make_hcs_2d(p11, p11+vector([1.0,0.0]))
            cs2 = make_hcs_2d(p21, p21+vector([1.0,0.0]))
        else:   # len(shared) >= 2:
            v1 = list(shared)[0]
            v2 = list(shared)[1]
            p11 = self.map[v1]
            p12 = self.map[v2]
            if tol_eq(norm(p12-p11), 0.0):
                underconstrained = True
                cs1 = make_hcs_2d(p11, p11+vector[1.0, 0.0])
            else:
                cs1 = make_hcs_2d(p11, p12)
            p21 = other.map[v1]
            p22 = other.map[v2]
            if tol_eq(norm(p22-p21),0.0):
                underconstrained = True
                cs2 = make_hcs_2d(p21, p21+vector[1.0,0.0])
            else:
                cs2 = make_hcs_2d(p21, p22)
        # in any case
        t = cs_transform_matrix(cs2, cs1)
        t.underconstrained = underconstrained
        return t

    def merge_scale_2D(self, other, vars=[]):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""
        if len(vars) == 0:
            shared = Set(self.vars()).intersection(other.vars())
        else:
            shared = vars
        underconstrained = self.underconstrained or other.underconstrained
        if len(shared) < 2:
            raise Exception("must have >=2 shared point vars")

        v1 = list(shared)[0]
        v2 = list(shared)[1]
        p11 = self.map[v1]
        p12 = self.map[v2]
        if tol_eq(norm(p12-p11),0.0):
            underconstrained = True
            cs1 = make_hcs_2d_scaled(p11, p11+vector[1.0,0.0])
        else:
            cs1 = make_hcs_2d_scaled(p11, p12)
        p21 = other.map[v1]
        p22 = other.map[v2]
        if tol_eq(norm(p22-p21),0.0):
            underconstrained = True
            cs2 = make_hcs_2d_scaled(p21, p21+vector[1.0,0.0])
        else:
            cs2 = make_hcs_2d_scaled(p21, p22)
        print("%s %s" % (cs1, cs2))
        t = cs_transform_matrix(cs2, cs1)
        othert = other.transform(t)
        result = self.add(othert)
        result.underconstrained = underconstrained
        return result

    def _merge_transform_3D(self, other):
        """returns a matrix for a rigid transformation 
           such that points in other are mapped onto points in self
        """
        shared = set(self.vars()).intersection(other.vars())
        underconstrained = self.underconstrained or other.underconstrained
        if len(shared) == 0:
            underconstrained = True
            cs1 = make_hcs_3d(vector([0.0, 0.0, 0.0]),
                              vector([0.0, 1.0, 0.0]),
                              vector([0.0, 0.0, 1.0]))
            cs2 = make_hcs_3d(vector([0.0, 0.0, 0.0]),
                              vector([0.0, 1.0, 0.0]),
                              vector([0.0, 0.0, 1.0]))
        elif len(shared) == 1:
            if len(self.vars()) > 1 and len(other.vars()) > 1:
                underconstrained = True
            v1 = list(shared)[0]
            p1s = self.map[v1]
            p1o = other.map[v1]
            cs1 = make_hcs_3d(p1s,
                              p1s+vector([1.0, 0.0, 0.0]),
                              p1s+vector([0.0, 1.0, 0.0]))
            cs2 = make_hcs_3d(p1o,
                              p1o+vector([1.0, 0.0, 0.0]),
                              p1o+vector([0.0, 1.0, 0.0]))
        elif len(shared) == 2:
            if len(self.vars()) > 2 and len(other.vars()) > 2:
                underconstrained = True
            v1 = list(shared)[0]
            p1s = self.map[v1]
            p1o = other.map[v1]
            v2 = list(shared)[1]
            p2s = self.map[v2]
            p2o = other.map[v2]
            p3s = p1s + cross(p2s-p1s, perp2D(p2s-p1s))
            p3o = p1o + cross(p2o-p1o, perp2D(p2s-p1s))
            if tol_eq(norm(p2s-p1s),0.0):
                underconstrained = True
            cs1 = make_hcs_3d(p1s, p2s, p3s)
            cs2 = make_hcs_3d(p1o, p2o, p3o)
        else:   # len(shared) >= 3:
            v1 = list(shared)[0]
            v2 = list(shared)[1]
            v3 = list(shared)[2]
            p1s = self.map[v1]
            p2s = self.map[v2]
            p3s = self.map[v3]
            cs1 = make_hcs_3d(p1s, p2s, p3s)
            if tol_eq(norm(p2s-p1s), 0.0):
                underconstrained = True
            if tol_eq(norm(p3s-p1s), 0.0):
                underconstrained = True
            if tol_eq(norm(p3s-p2s), 0.0):
                underconstrained = True
            p1o = other.map[v1]
            p2o = other.map[v2]
            p3o = other.map[v3]
            cs2 = make_hcs_3d(p1o, p2o, p3o)
            if tol_eq(norm(p2o-p1o), 0.0):
                underconstrained = True
            if tol_eq(norm(p3o-p1o), 0.0):
                underconstrained = True
            if tol_eq(norm(p3o-p2o), 0.0):
                underconstrained = True
        # in any case:
        t = cs_transform_matrix(cs2, cs1)
        t.underconstrained = underconstrained
        return t

    def _merge_scale_transform_3D(self, other):
        shared = set(self.vars()).intersection(other.vars())
        if len(shared) == 0:
            return self._merge_transform_3D(other)
        elif len(shared) == 1:
            return self._merge_transform_3D(other)
        elif len(shared) >= 2:
            v1 = list(shared)[0]
            p1s = self.map[v1]
            p1o = other.map[v1]
            v2 = list(shared)[1]
            p2s = self.map[v2]
            p2o = other.map[v2]
            scale = norm(p2s-p1s) / norm(p2o-p1o)
            scale_trans = pivot_scale_3D(p1o,scale)
            diag_print("scale_trans = "+str(scale_trans),
                       "Configuration.merge_scale_transform_3D")
            merge_trans = self._merge_transform_3D(other)
            diag_print("merge_trans = "+str(merge_trans),
                       "Configuration.merge_scale_transform_3D")
            # merge_scale_trans = scale_trans.mmul(merge_trans)
            merge_scale_trans = merge_trans.mmul(scale_trans)
            merge_scale_trans.underconstrained = merge_trans.underconstrained
            return merge_scale_trans

    def __eq__(self, other):
        """two configurations are equal if they map onto eachother modulo
        rotation and translation"""
        if hash(self) != hash(other):
            return False
        elif len(self.map) != len(other.map):
            return False
        else:
            if not isinstance(other, Configuration):
                return False
            for var in self.map:
                if var not in other.map:
                    return False
            # determine a rotation-translation transformation
            # to transform other onto self
            t = self.merge_transform(other)
            othertransformed = other.transform(t)
            # test if point map onto eachother (distance metric tolerance)
            for var in self.map:
                d = distance_2p(othertransformed.get(var), self.get(var))
                if tol_gt(d, 0.0):
                    return False
            return True

    def makehash(self):
        """the hash is based only on variable names (not values)"""
        val = 0
        for var in self.map:
            val = val + hash(var)
        self.hashvalue = hash(val)

    def checkdimension(self):
        """returns the dimension of the points, or zero if they are
        of different dimensions"""
        var = iter(self.vars()).__next__()
        dim = len(self.get(var))
        for var in self.map:
            if len(self.get(var)) != dim:
                dim = 0
                break
        return dim

    def __hash__(self):
        return self.hashvalue

    def __str__(self):
        return "Configuration("+str(self.map)+")"


def test():
    p1 = vector([0.0, 0.0, 0.0])
    p2 = vector([1.0, 0.0, 0.0])
    p3 = vector([0.0, 1.0, 0.0])
    c1 = Configuration({1: p1, 2: p2})
    q1 = vector([0.0, 0.0, 0.0])
    q2 = vector([1.0, 0.0, 0.0])
    q3 = vector([0.0, -1.0, 0.0])
    c2 = Configuration({1: q1, 2: q2})
    print(c1 == c2)

if __name__ == "__main__":
    test()

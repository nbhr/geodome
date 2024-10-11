import numpy as np
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull

from geodome import TriangleMesh


# based on https://stackoverflow.com/a/26127012
def fibonacci_sphere(samples):
    phi = np.pi * (np.sqrt(5.) - 1.)  # golden angle in radians

    i = np.arange(samples)
    y = 1 - (i / (samples - 1)) * 2  # y goes from 1 to -1
    radius = np.sqrt(1 - y**2)  # radius at y
    theta = phi * i  # golden angle increment
    x = np.cos(theta) * radius
    z = np.sin(theta) * radius

    return np.stack([z, x, y]).T


class FibonacciSphere(TriangleMesh):
    def __init__(self, samples):
        # compute the vertices
        self.v = fibonacci_sphere(samples)

        # triangulation by convex hull
        hull = ConvexHull(self.v)
        self.f = hull.simplices
        self.force_ccw()


if __name__ == "__main__":
    # Fibonacci Sphere of 1000 points
    f = FibonacciSphere(1000)

    # Check the number of vertices / faces
    print(f'num of vertices = {len(f.v)}, num of faces = {len(f.f)}')

    # Save as PLY
    f.save_as_ply('a.ply')

    # 3D plot
    f.plot3D()

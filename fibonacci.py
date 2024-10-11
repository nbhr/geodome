import numpy as np
from scipy.spatial import ConvexHull
from geodome import TriangleMesh


# This is based on https://stackoverflow.com/a/26127012
# if you need vertices only (no mesh triangles), you can
# simply copy-and-paste this function to your code.
def fibonacci_sphere(samples):
    phi = np.pi * (np.sqrt(5.) - 1.)  # golden angle in radians

    i = np.arange(samples)
    y = 1 - (i / (samples - 1)) * 2  # y goes from 1 to -1
    radius = np.sqrt(1 - y**2)  # radius at y
    theta = phi * i  # golden angle increment
    x = np.cos(theta) * radius
    z = np.sin(theta) * radius

    # make v[0] == (0,0,1) and v[-1] == (0,0,-1)
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
    # Fibonacci sphere of 1000 points
    f = FibonacciSphere(1000)

    # Check the number of vertices / faces
    print(f'num of vertices = {len(f.v)}, num of faces = {len(f.f)}')

    # Save as PLY
    f.save_as_ply('a.ply')

    # 3D plot
    f.plot3D()

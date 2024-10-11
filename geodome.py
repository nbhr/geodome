import numpy as np
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class TriangleMesh:
    def plot3D(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Create a list of 3D vertex arrays for each face
        faces = [self.v[face] for face in self.f]

        # Create the 3D polygon collection
        tri = Poly3DCollection(faces, edgecolor='k')

        # Add the collection to the 3D plot
        ax.add_collection3d(tri)

        # Set the axis limits
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_zlim(-2, 2)

        # Show the result
        plt.show()


    def save_as_ply(self, filename):
        with open(filename, 'w') as fp:
            fp.write('ply\n')
            fp.write('format ascii 1.0\n')
            fp.write(f'element vertex {len(self.v)}\n')
            fp.write('property float x\n')
            fp.write('property float y\n')
            fp.write('property float z\n')
            fp.write(f'element face {len(self.f)}\n')
            fp.write('property list uchar int vertex_indices\n')
            fp.write('end_header\n')
            np.savetxt(fp, self.v)
            f2 = np.hstack([(np.ones(len(self.f), dtype=np.int32) * 3).reshape((-1, 1)), self.f])
            np.savetxt(fp, f2, fmt='%d')

    def force_ccw(self):
        v = self.v[self.f]
        e01 = v[:,1] - v[:,0]
        e02 = v[:,2] - v[:,0]
        fn = np.cross(e01, e02)
        dir = np.einsum('ij,ij->i', fn, v[:,0])
        self.f[dir < 0, 0], self.f[dir < 0, 1] = self.f[dir < 0, 1], self.f[dir < 0, 0]

class GeodesicDome(TriangleMesh):
    """
    Geodesic Dome of Nv vertices and Nf faces.

    self.v: (Nv, 3) array. list of vertices.
    self.f: (Nf, 3) array. list of vertex indices to define faces.
    """
    def __init__(self):
        ## vertices ##
        p = (1 + np.sqrt(5)) / 2
        a = np.sqrt((3 + 4 * p) / 5) / 2
        b = np.sqrt(p / np.sqrt(5))
        c = np.sqrt(3 / 4 - a ** 2)
        d = np.sqrt(3 / 4 - (b - a)** 2)
        # icosahedron in (r, theta, z) == cylindrical coordinates
        self.v = np.array([
            [0, 0, (c + d / 2)],
            [b, 2*0*np.pi / 5, d / 2],
            [b, 2*1*np.pi / 5, d / 2],
            [b, 2*2*np.pi / 5, d / 2],
            [b, 2*3*np.pi / 5, d / 2],
            [b, 2*4*np.pi / 5, d / 2],
            [b, (2*0+1)*np.pi / 5, - d / 2],
            [b, (2*1+1)*np.pi / 5, - d / 2],
            [b, (2*2+1)*np.pi / 5, - d / 2],
            [b, (2*3+1)*np.pi / 5, - d / 2],
            [b, (2*4+1)*np.pi / 5, - d / 2],
            [0, 0, -(c + d / 2)],
        ])
        # icosahedron in (x, y, z) == Cartesian coordinates
        self.v = np.vstack([
            self.v[:, 0]*np.cos(self.v[:, 1]),
            self.v[:, 0]*np.sin(self.v[:, 1]),
            self.v[:, 2]
        ]).T
        # normalize the radius
        self.v *= (1 / self.v[0, 2])

        # fix super small values to zero
        self.tol = 1e-15
        self.v[np.abs(self.v) < self.tol] = 0

        ## faces ##
        self.f = np.array([
            [2, 0, 1],
            [3, 0, 2],
            [4, 0, 3],
            [5, 0, 4],
            [1, 0, 5],
            [2, 1, 6],
            [7, 2, 6],
            [3, 2, 7],
            [8, 3, 7],
            [4, 3, 8],
            [9, 4, 8],
            [5, 4, 9],
            [10, 5, 9],
            [6, 1, 10],
            [1, 5, 10],
            [6, 11, 7],
            [7, 11, 8],
            [8, 11, 9],
            [9, 11, 10],
            [10, 11, 6],
        ])

    def tessellate(self, iter=1):
        def newvert(v0, v1):
            v = v0 + v1
            v /= np.linalg.norm(v)
            return v

        for _ in range(iter):
            f = self.f
            v = self.v
            v2 = []
            vv2v = {}
            vid = len(v)
            for tri in self.f:
                for i, j in zip([0, 1, 2], [1, 2, 0]):
                    if tri[i] < tri[j]:
                        vv2v[tri[i], tri[j]] = vv2v[tri[j], tri[i]] = vid
                        vid += 1
                        v2.append(newvert(v[tri[i]], v[tri[j]]))
            v = np.vstack([v, np.array(v2)])

            f2 = []
            for tri in self.f:
                f2.append([tri[0], vv2v[tri[0], tri[1]], vv2v[tri[2], tri[0]]])
                f2.append([tri[1], vv2v[tri[1], tri[2]], vv2v[tri[0], tri[1]]])
                f2.append([tri[2], vv2v[tri[2], tri[0]], vv2v[tri[1], tri[2]]])
                f2.append([vv2v[tri[0], tri[1]], vv2v[tri[1], tri[2]], vv2v[tri[2], tri[0]]])

            self.v = v
            self.f = np.array(f2)

        self.v[np.abs(self.v) < self.tol] = 0
        return self

    def face_normal(self):
        """
        This function is not needed in most cases, since the vertex position is identical to its normal.
        """
        tri = self.v[self.f]
        n = np.cross(tri[:, 1,:] - tri[:, 0,:], tri[:, 2,:] - tri[:, 0,:])
        n /= np.linalg.norm(n, axis=0)
        return n


if __name__ == "__main__":
    # Icosahedron
    g = GeodesicDome()

    # Subdivide N times
    g.tessellate(3)

    # Check the number of vertices / faces
    print(f'num of vertices = {len(g.v)}, num of faces = {len(g.f)}')

    # Save as PLY
    g.save_as_ply('a.ply')

    # 3D plot
    g.plot3D()

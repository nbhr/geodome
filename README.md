# Usage

```
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
```

# Numbers of Vertices / Faces / Edges

* Level 0 == icosahedron has 12 vertices, 20 faces, and 30 edges (and satisfies Euler formula V + F - E = 2, of course).
* Level `n` has `10 * 4^n + 2` vertices, `20 * 4^n` faces, and `20 * 4^n * 3 / 2` edges.
  * Level 1: 42 vertices, 80 faces
  * Level 2: 162 vertices, 320 faces
  * Level 3: 642 vertices, 1280 faces

# Algorithm

## Level 0 == Icosahedron

As explained in [Wikipedia](https://en.wikipedia.org/wiki/Regular_icosahedron), a unit icosahedron can be defined as a circular permutations of `(0, +/-1, +/-φ)`, where `φ = (1 + sqrt(5)) / 2`.
This definition is simple, but not easy to use for some scenarios since none of the vertices are on an axis.

Instead, as explained in https://mae.ufl.edu/~uhk/PLATONIC-SOLIDS.pdf, we can define the vertices in cylindrical coordinates `(r, θ, z)` as follows.

1. Suppose the top and the bottom vertices of the icosahedron are on the Z axis. The rest of the vertices form two rings of pentagons orthogonal to the Z axis.
2. The distance `b` from a vertex on the pentagons to the Z axis is `b = 1 / (2 sin(π/5))`.
3. The distance `a` from the middle of one of the pentagon edges to the polar axis is `a = 1 / (2 tan(π/5))`.
4. The height `c` of the pentagonal pyramid (the distance from the pentagon to the top) is `c = sqrt(3/4 - a^2)`.
5. The distance `d` between the pentagons is `d = sqrt(3/4 - (b-a)^2)`.
6. The top/bottom vertices are `(0, 0, +/- (c + d/2))`.
7. The vertices of the upper pentagon are `(b, 2nπ/5, d/2)`, where `n=0,...4`.
8. The vertices of the lower pentagon are `(b, (2n+1)π/5, -d/2)`, where `n=0,...4`.

Finally we can convert the cylindrical coordinates to Cartesian by `(x, y, z) = (r cosθ, r sinΘ, z)` as usual.

## Level n == Tessellation of Level (n-1)

The tessellation is implemented by subdividing each triangle into four subtriangles.

* For each triangle,
  1. insert new vertices at the midpoints of its edges,
  2. move (push) the new vertices in the radial direction so as to be on the unit sphere,
  3. replace the triangle with the four subtriangles as follows.
  ```
  O-----------O        O-----x-----O
   \         /          \   / \   /
    \       /            \ /   \ /
     \     /     ==>      x-----x
      \   /                \   /
       \ /                  \ /
        O                    O
  ```

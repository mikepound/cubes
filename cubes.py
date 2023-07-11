import os
import sys
import math
import numpy as np
import argparse
from time import perf_counter

def all_rotations(polycube):
    """
    Calculates all rotations of a polycube.
  
    Adapted from https://stackoverflow.com/questions/33190042/how-to-calculate-all-24-rotations-of-3d-array.
    This function computes all 24 rotations around each of the axis x,y,z. It uses numpy operations to do this, to avoid unecessary copies.
    The function returns a generator, to avoid computing all rotations if they are not needed.
  
    Parameters:
    polycube (np.array): 3D Numpy byte array where 1 values indicate polycube positions

    Returns:
    generator(np.array): Yields new rotations of this cube about all axes
  
    """
    def single_axis_rotation(polycube, axes):
        """Yield four rotations of the given 3d array in the plane spanned by the given axes.
        For example, a rotation in axes (0,1) is a rotation around axis 2"""
        for i in range(4):
             yield np.rot90(polycube, i, axes)

    # 4 rotations about axis 0
    yield from single_axis_rotation(polycube, (1,2))

    # rotate 180 about axis 1, 4 rotations about axis 0
    yield from single_axis_rotation(np.rot90(polycube, 2, axes=(0,2)), (1,2))

    # rotate 90 or 270 about axis 1, 8 rotations about axis 2
    yield from single_axis_rotation(np.rot90(polycube, axes=(0,2)), (0,1))
    yield from single_axis_rotation(np.rot90(polycube, -1, axes=(0,2)), (0,1))

    # rotate about axis 2, 8 rotations about axis 1
    yield from single_axis_rotation(np.rot90(polycube, axes=(0,1)), (0,2))
    yield from single_axis_rotation(np.rot90(polycube, -1, axes=(0,1)), (0,2))

def crop_cube(cube):
    """
    Crops an np.array to have no all-zero padding around the edge.

    Given in https://stackoverflow.com/questions/39465812/how-to-crop-zero-edges-of-a-numpy-array
  
    Parameters:
    cube (np.array): 3D Numpy byte array where 1 values indicate polycube positions
  
    Returns:
    np.array: Cropped 3D Numpy byte array equivalent to cube, but with no zero padding
  
    """
    for i in range(cube.ndim):
        cube = np.swapaxes(cube, 0, i)  # send i-th axis to front
        while np.all( cube[0]==0 ):
            cube = cube[1:]
        while np.all( cube[-1]==0 ):
            cube = cube[:-1]
        cube = np.swapaxes(cube, 0, i)  # send i-th axis to its original position
    return cube

def expand_cube(cube):
    """
    Expands a polycube by adding single blocks at all valid locations.
  
    Calculates all valid new positions of a polycube by shifting the existing cube +1 and -1 in each dimension.
    New valid cubes are returned via a generator function, in case they are not all needed.
  
    Parameters:
    cube (np.array): 3D Numpy byte array where 1 values indicate polycube positions
  
    Returns:
    generator(np.array): Yields new polycubes that are extensions of cube
  
    """
    cube = np.pad(cube, 1, 'constant', constant_values=0)
    output_cube = np.array(cube)

    xs,ys,zs = cube.nonzero()
    output_cube[xs+1,ys,zs] = 1
    output_cube[xs-1,ys,zs] = 1
    output_cube[xs,ys+1,zs] = 1
    output_cube[xs,ys-1,zs] = 1
    output_cube[xs,ys,zs+1] = 1
    output_cube[xs,ys,zs-1] = 1

    exp = (output_cube ^ cube).nonzero()

    for (x,y,z) in zip(exp[0], exp[1], exp[2]):
        new_cube = np.array(cube)
        new_cube[x,y,z] = 1
        yield crop_cube(new_cube)

def generate_polycubes(n, use_cache=False):
    """
    Generates all polycubes of size n
  
    Generates a list of all possible configurations of n cubes, where all cubes are connected via at least one face.
    Builds each new polycube from the previous set of polycubes n-1.
    Uses an optional cache to save and load polycubes of size n-1 for efficiency.
  
    Parameters:
    n (int): The size of the polycubes to generate, e.g. all combinations of n=4 cubes.
  
    Returns:
    list(np.array): Returns a list of all polycubes of size n as numpy byte arrays
  
    """
    if n < 1:
        return []
    elif n == 1:
        return [np.ones((1,1,1), dtype=np.byte)]
    elif n == 2:
        return [np.ones((2,1,1), dtype=np.byte)]

    # Check cache
    cache_path = f"cubes_{n}.npy"
    if use_cache and os.path.exists(cache_path):
        print(f"\rLoading polycubes n={n} from cache: ", end = "")
        polycubes = np.load(cache_path, allow_pickle=True)
        print(f"{len(polycubes)} shapes")
        return polycubes

    # Empty list of new n-polycubes
    polycubes = []
    polycubes_rle = set()

    base_cubes = generate_polycubes(n-1, use_cache)

    for idx, base_cube in enumerate(base_cubes):
        # Iterate over possible expansion positions
        for new_cube in expand_cube(base_cube):
            if not cube_exists_rle(new_cube, polycubes_rle):
                polycubes.append(new_cube)
                polycubes_rle.add(rle(new_cube))

        if (idx % 100 == 0):               
            perc = round((idx / len(base_cubes)) * 100,2)
            print(f"\rGenerating polycubes n={n}: {perc}%", end="")

    print(f"\rGenerating polycubes n={n}: 100%   ")
    
    if use_cache:
        cache_path = f"cubes_{n}.npy"
        np.save(cache_path, np.array(polycubes, dtype=object), allow_pickle=True)

    return polycubes

def rle(polycube):
    """
    Computes a simple run-length encoding of a given polycube. This function allows cubes to be more quickly compared via hashing.
  
    Converts a {0,1} nd array into a tuple that encodes the same shape. The array is first flattened, and then the following algorithm is applied:

    1) The first three values in tuple contain the x,y,z dimension sizes of the array
    2) Each string of zeros of length n is replaced with a single value -n
    3) Each string of ones of length m is replaced with a single value +m
  
    Parameters:
    polycube (np.array): 3D Numpy byte array where 1 values indicate polycube positions
  
    Returns:
    tuple(int): Run length encoded polycube in the form (X, Y, Z, a, b, c, ...)

    """
    r = []
    r.extend(polycube.shape)
    current = None
    val = 0
    for x in polycube.flat:
        if current is None:
            current = x
            val = 1
            pass
        elif current == x:
            val += 1
        elif current != x:
            r.append(val if current == 1 else -val)
            current = x
            val = 1

    r.append(val if current == 1 else -val)

    return tuple(r)

def cube_exists_rle(polycube, polycubes_rle):
    """
    Determines if a polycube has already been seen.
  
    Considers all possible rotations of a cube against the existing cubes stored in memory.
    Returns True if the cube exists, or False if it is new.
  
    Parameters:
    polycube (np.array): 3D Numpy byte array where 1 values indicate polycube positions
  
    Returns:
    boolean: True if polycube is already present in the set of all cubes so far.
  
    """
    for cube_rotation in all_rotations(polycube):
        if rle(cube_rotation) in polycubes_rle:
            return True

    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Polycube Generator',
                    description='Generates all polycubes (combinations of cubes) of size n.')

    parser.add_argument('n', metavar='N', type=int,
                    help='The number of cubes within each polycube')
    
    #Requires python >=3.9
    parser.add_argument('--cache', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
   
    n = args.n
    use_cache = args.cache if args.cache is not None else True

    # Start the timer
    t1_start = perf_counter()

    all_cubes = list(generate_polycubes(n, use_cache=use_cache))

    # Stop the timer
    t1_stop = perf_counter()

    print (f"Found {len(all_cubes)} unique polycubes")
    print (f"Elapsed time: {round(t1_stop - t1_start,3)}s")


# Code for if you want to generate pictures of the sets of cubes. Will work up to about n=8, before there are simply too many!
# Could be adapted for larger cube sizes by splitting the dataset up into separate images.
# def render_shapes(shapes, path):
#     n = len(shapes)
#     dim = max(max(a.shape) for a in shapes)
#     i = math.isqrt(n) + 1
#     voxel_dim = dim * i
#     voxel_array = np.zeros((voxel_dim + i,voxel_dim + i,dim), dtype=np.byte)
#     pad = 1
#     for idx, shape in enumerate(shapes):
#         x = (idx % i) * dim + (idx % i)
#         y = (idx // i) * dim + (idx // i)
#         xpad = x * pad
#         ypad = y * pad
#         s = shape.shape
#         voxel_array[x:x + s[0], y:y + s[1] , 0 : s[2]] = shape

#     voxel_array = crop_cube(voxel_array)
#     colors = np.empty(voxel_array.shape, dtype=object)
#     colors[:] = '#FFD65DC0'

#     ax = plt.figure(figsize=(20,16), dpi=600).add_subplot(projection='3d')
#     ax.voxels(voxel_array, facecolors = colors, edgecolor='k', linewidth=0.1)
    
#     ax.set_xlim([0, voxel_array.shape[0]])
#     ax.set_ylim([0, voxel_array.shape[1]])
#     ax.set_zlim([0, voxel_array.shape[2]])
#     plt.axis("off")
#     ax.set_box_aspect((1, 1, voxel_array.shape[2] / voxel_array.shape[0]))
#     plt.savefig(path + ".png", bbox_inches='tight', pad_inches = 0)

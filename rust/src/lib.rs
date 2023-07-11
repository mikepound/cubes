mod cache;

use std::{collections::HashSet, path::Path};

use ndarray::{Array, ArrayBase, Dim, OwnedRepr};

use crate::cache::{get_cache, save_cache};

type Polycube = ArrayBase<OwnedRepr<u8>, Dim<[usize; 3]>>;
type Rle = Vec<isize>;

fn all_rotations(polycube: &Polycube) {
    todo!();
}

fn crop_cube(cube: &Polycube) -> Polycube {
    todo!();
}

fn expand_cube(cube: &Polycube) -> Vec<Polycube> {
    todo!();
}

/// Generates all polycubes of size n
///
/// Generates a list of all possible configurations of n cubes, where all cubes are connected via at least one face.
/// Builds each new polycube from the previous set of polycubes n-1.
/// Uses an optional cache to save and load polycubes of size n-1 for efficiency.
///
/// Parameters:
/// number (int): The size of the polycubes to generate, e.g. all combinations of n=4 cubes.
///
/// Returns:
/// Vec<u8>: Returns a list of all polycubes of size n
pub fn generate_polycubes(number: u8, use_cache: bool) -> Vec<Polycube> {
    if number < 1 {
        return vec![];
    } else if number == 1 {
        return vec![Array::<u8, _>::ones((1, 1, 1))];
    } else if number == 2 {
        return vec![Array::<u8, _>::ones((2, 1, 1))];
    }

    // Check cache
    let cache_path = format!("cubes_{}.bin", number);
    let cache_path = Path::new(&cache_path);
    if use_cache && cache_path.exists() {
        print!("Loading polycubes n={number} from cache: ");
        let polycubes = get_cache(cache_path).unwrap();
        println!("{} shapes", polycubes.len());
        return polycubes;
    }

    // Empty list of new n-polycubes
    let mut polycubes = Vec::new();
    let mut polycubes_rle: HashSet<Rle> = HashSet::new();

    let base_cubes = generate_polycubes(number - 1, use_cache);

    // TODO: Use Rayon
    for (idx, base_cube) in base_cubes.iter().enumerate() {
        // Iterate over possible expansion positions
        for new_cube in expand_cube(base_cube) {
            if !cube_exists_rle(&new_cube, &polycubes_rle) {
                polycubes_rle.insert(rle(&new_cube));
                polycubes.push(new_cube);
            }
        }

        if idx % 100 == 0 {
            let perc: f32 = (idx as f32) / (base_cubes.len() as f32) * 100f32;
            println!("Generating polycubes n={number}: {:.2}%", perc);
        }
    }

    println!("Generating polycubes n={number}: 100%   ");

    if use_cache {
        save_cache(cache_path, &polycubes).unwrap();
    }

    polycubes
}

/// Computes a simple run-length encoding of a given polycube. This function allows cubes to be more quickly compared via hashing.
///
/// Converts a {0,1} nd array into a tuple that encodes the same shape. The array is first flattened, and then the following algorithm is applied:
///
/// 1) The first three values in tuple contain the x,y,z dimension sizes of the array
/// 2) Each string of zeros of length n is replaced with a single value -n
/// 3) Each string of ones of length m is replaced with a single value +m
///
/// Parameters:
/// polycube (Polycube): 3D Numpy byte array where 1 values indicate polycube positions
///
/// Returns:
/// Rle: Run length encoded polycube in the form (X, Y, Z, a, b, c, ...)
fn rle(polycube: &Polycube) -> Rle {
    let mut r: Vec<isize> = polycube.shape().iter().map(|n| *n as isize).collect();
    let mut current = None;
    let mut val = 0isize;
    for x in polycube.iter() {
        match current {
            None => {
                current = Some(x);
                val = 1;
            }
            Some(c) if c == x => {
                val += 1;
            }
            Some(c) => {
                r.push(if c == &1u8 { val } else { -val });
                current = Some(x);
                val = 1;
            }
        }
    }

    r.push(match current {
        Some(current) if current == &1u8 => val,
        _ => -val,
    });

    r
}

#[test]
fn test_rle() {
    let ones = Array::<u8, _>::ones((3, 1, 1));
    assert_eq!(rle(&ones), vec![3, 1, 1, 3]);
}

/// Determines if a polycube has already been seen.
///
/// Considers all possible rotations of a cube against the existing cubes stored in memory.
/// Returns True if the cube exists, or False if it is new.
///
/// Parameters:
/// polycube (np.array): 3D Numpy byte array where 1 values indicate polycube positions
///
/// Returns:
/// boolean: True if polycube is already present in the set of all cubes so far.
fn cube_exists_rle(polycube: &Polycube, polycubes_rle: &HashSet<Rle>) -> bool {
    todo!();
}

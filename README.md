# Polycubes
This code is associated with the Computerphile video on generating polycubes. A polycube is a set of cubes in any configuration in which all cubes are orthogonally connected - share a face. This code calculates all the variations of 3D polycubes for any size (time permitting!). 

![5cubes](https://github.com/mikepound/cubes/assets/9349459/4fe60d01-c197-4cb3-b298-1dbae8517a74)


## How the code works
The code includes some doc strings to help you understand what it does, but in short it operates a bit like this (oversimplified!):

To generate all combinations of n cubes, we first calculate all possible n-1 shapes based on the same algorithm. We begin by taking all of the n-1 shape, and for each of these add new cubes in any possible free locations. For each of these potential new shapes, we test each rotation of this shape to see if it's been seen before. Entirely new shapes are added to a set of all shapes, to check future candidates.

In order to check slightly faster than simply comparing arrays, each shape is converted into a shortened run length encoding form, which allows hashes to be computed, so we can make use of the set datastructure.

## Running the code
With python installed, you can run the code like this:

`python cubes.py --cache n`

Where n is the number of cubes you'd like to calculate. If you specify `--cache` then the program will attempt to load .npy files that hold all the pre-computed cubes for n-1 and then n. If you specify `--no-cache` then everything is calcuated from scratch, and no cache files are stored.

## Pre-computed cache files
You can download the cache files for n=3 to n=11 from [here](https://drive.google.com/drive/folders/1Ls3gJCrNQ17yg1IhrIav70zLHl858Fl4?usp=drive_link). If you manage to calculate any more sets, please feel free to save them as an npy file and I'll upload them!

## Improving the code
This was just a bit of fun, and as soon as it broadly worked, I stopped! This code could be made a lot better, and actually the whole point of the video was to get people thinking and have a mess around yourselves. Some things you might think about:
- Another language like c or java would be substantially faster
- Other languages would also have better support for multi-threading, which would be a transformative speedup
- Calculating 24 rotations of a cube is slow, the only way to avoid this would be to come up with some rotationally invariant way of comparing cubes. I've not thought of one yet!

## Contributing!
Please do have a go makign the code better - the video has been up only a short while and we already have fantastic pull requests and issues / discussions. I won't merge anything immediately, because to be honest I have no idea what the best way to deal with the potential influx is! While I think about this (ideas welcome ;)) please do browse the issues and pull requests as there is some great stuff in here.

## References
- [Wikipedia article](https://en.wikipedia.org/wiki/Polycube)
- [This repository](https://github.com/noelle-crawfish/Enumerating-Polycubes) was a source of inspiration, and a great description of some possible ways to solve this.
- [There may be better ways](https://www.sciencedirect.com/science/article/pii/S0012365X0900082X) to count these, but I've not explored in much detail.
- [Kevin Gong's](http://kevingong.com/Polyominoes/Enumeration.html) webpage on enumerating all shapes up to n=16.

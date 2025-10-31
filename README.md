<p align="center">
  <img src="assets/images/1bend_01.png" alt="Screenshot 1" width="45%"/>
  <img src="assets/images/2bend_01.png" alt="Screenshot 2" width="45%"/>
</p>

<p align="center">
  <img src="assets/images/2bend_04.png" alt="Screenshot 3" width="45%"/>
  <img src="assets/images/2bend_03.png" alt="Screenshot 4" width="45%"/>
</p>


THIS PROJECT IS STILL UNFINISHED!

# How it works
The user gives two rectangles as an input, and the program tries to find different ways to connect those two rectangles in way, that is manufacturable. Solutions are generated in two ways. Either by finding the intersection of the two planes and connecting them, or by selecting 2 points from one rectangle and 1 point from the other, and creating an additional tab on that plane.

# How to run it
0. Open the main folder in an IDE or in the console
1. Create a virtual environment
   `python3 -m venv ./venv`
2. Activate the virtual environment
   `source venv/bin/activate`
3. Install dependencies (the . at the end is important)
   `pip install -e .`
4. Run the program
   `python -m gen_design_sheet_metal`


# How to use it

In user_input.py you can provide the input values you want.
In config.yaml you can configure what should get plotted.

# Explanation of Abbreviations

- BP = Bending Point
- CP = Corner Point
- FP = Flange Point

- _A  = Part of Tab A
- _AB = Connect Tab A and B

- _0 = Middle
- _1 = Side 1
- _2 = Side 2

# Development Goals

- [x] Generate solutions for 1 bend
- [x] Generate solutions for 2 bend
- [x] Improve flange visuals
- [ ] Filter solutions that are unsuitable
- [ ] Minimum distance from bend
- [ ] Introduce mounts
- [ ] Extend to multiple squares
- [ ] Generate solutions by separating surfaces

- [x] Extend installation guide
- [x] Explain function more precisely
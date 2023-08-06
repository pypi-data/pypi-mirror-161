# Cyclehunter

## Introduction

This package/repository is a organizational effort to manage a collection of Physics research projects associated
with the Center of Nonlinear Dynamics and Chaos at Georgia Tech and their collaborators. The sister Python package,
orbithunter, was mainly concerned with solving differential algebraic equations associated with finding spatiotemporal
solutions to partial differential equations. 

In this case, we are concerned with counting of prime cycles of discrete mappings such as Arnold's cat map, phi-k scalar
field theory, etc. where the systems are simple enough to enable analytic counting formulae and well founded symbolic
alphabets. Because of this, the overhead to find individual cycles is greatly diminished; the main hurdle is instead to
enumerate the entire set of prime cycles for usage in cycle expansion equations / dynamical zeta functions. "Prime"
denotes the set of cycles which remain after quotienting all symmetries, i.e. the unique cycles.

Therefore, the focus is much less on singular/individual cycles, rather, entire collections of prime cycles. Numerically
this is a different challenge and makes much more sense to solve the problem *en masse* because cycles of a specified 
length $n$ are easy to enumerate, can be solved for simultaneously and in parallel. The object oriented programming
which results from this is one in which the custom class objects will represent *all* cycles at once. 

You can install the python environment by downloading a python distribution (go to python.org).

I highly recommend you create a virtual environment as well; so do one of the following
in command line terminal


```
pip install -r requirements.txt
```

or

(note the periods; they are necessary)

Make a folder, copy the requirements.txt file into it, then type these commands; this
assumes your python.exe is in your terminal path. 

```
python -m venv .
cd Scripts
./activate
cd ..
pip install -r requirements.txt
```
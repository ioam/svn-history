#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 1:
  data = [(i+1)**2 for i in range(size)]
else:
  data = None

data = comm.scatter(data, root=1)
#assert data == (rank+1)**2
sys.stdout.write("rank: %d, data: %d\n" % (rank, data))
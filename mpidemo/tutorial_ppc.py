#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import os, sys
from mpi4py import MPI
import numpy

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
  data = numpy.arange(1000,dtype='i')
  comm.Send([data, MPI.INT], dest=1, tag=77)
  sys.stdout.write('sender\n')
elif rank == 1:
  data = numpy.empty(1000,dtype='i')
  comm.Recv([data, MPI.INT], source=0,tag=77)
  sys.stdout.write('receiver\n')

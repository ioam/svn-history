#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from mpi4py import MPI
import sys

numprocs = 2

comm = MPI.COMM_SELF.Spawn(sys.executable,args=['test_app_s.py'], maxprocs=numprocs)

hi = comm.recv(source = 1, tag=1)

print "master ", hi
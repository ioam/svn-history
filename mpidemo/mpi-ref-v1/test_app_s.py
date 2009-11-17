#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from mpi4py import MPI

comm = MPI.Comm.Get_parent()
comm2 = MPI.COMM_WORLD
rank = comm.Get_rank()
rank2 = comm2.Get_rank()

if rank == 0:
	hi = comm2.recv(source=1, tag=1)
	print "slave ", hi
if rank == 1:
	comm2.send("HI!!!", 0, 1)
	comm.send("HI!!!",0,1)
#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from mpi4py import MPI
import numpy

comm = MPI.Comm.Get_parent()
rank = comm.Get_rank()

data = numpy.array(comm.recv(source=0,tag=0))

result = []

for i in range(0,len(data[0])):
	result.append(numpy.dot(data[0][i].ravel(),data[1][i].ravel()))



comm.send(result,0,1)


comm.Disconnect()
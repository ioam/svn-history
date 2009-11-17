#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from mpi4py import MPI
import numpy

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank==0:
	m1 = numpy.array([[1,0,0],
					  [0,1,0],
					  [0,0,1]])
	m2 = numpy.array([[1,1,1],
					  [2,2,2],
					  [3,3,3]])
	m3 = numpy.array([[1,2,3],
					  [1,2,3],
					  [1,2,3]])
	m4 = numpy.array([[2,0,1],
					  [0,2,0],
					  [1,0,2]])
	m5 = numpy.array([[3,0,3],
					  [0,1,0],
					  [0,0,3]])
	A = numpy.array([m1,m2,m3,m4,m5,m1,m2,m3,m4,m5])
	B = numpy.array([m2,m3,m4,m5,m1,m5,m4,m3,m2,m1])

if rank==0: #sending data
	i = size
	i_from = 0
	i_to = 0
	to_send_num = len(A)
	while i>1:
		i_to = i_from + int(to_send_num/i)
		to_send_num = to_send_num - (i_to - i_from)
		comm.send([A[i_from:i_to],B[i_from:i_to]], i-1, 0)
		i_from = i_to
		i = i-1
	i_to = i_from + to_send_num	
	data_a = A[i_from:i_to]
	data_b = B[i_from:i_to]
	data = [data_a,data_b]
else: #receiving data
	data = comm.recv(0,0)
	data_a = data[0]
	data_b = data[1]
	
data = numpy.array(data)
print "rank: ", rank
print data
result = []
for i in range (0, len(data_a)):
	result.append(numpy.dot(data_a[i].ravel(),data_b[i].ravel()))

result = numpy.array(result)

print "DotProduct: ", result
#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# TODO: Try and figure out if it's possible to replace the send/recv mechanism
#		with Windows, cause it seems to be faster (at least the manual says so...)


from mpi4py import MPI
import numpy
import sys

# TODO: Need to find a way to determine the right number of nodes in a system

numprocs = 4 

comm = MPI.COMM_SELF.Spawn(sys.executable,args=['slave_dot.py'], maxprocs=numprocs)

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

A = numpy.array([m1,m2,m3,m4,m5])
B = numpy.array([m5,m4,m3,m2,m1])

result = []

i = numprocs
i_from = 0
i_to = 0
to_send_num = len(A)

while i>0:
	i_to = i_from + int(to_send_num/(i+1))
	to_send_num = to_send_num - (i_to - i_from)
	comm.send([A[i_from:i_to],B[i_from:i_to]], i-1, tag=0)
	print "sent to ", i-1
	i_from = i_to
	i = i-1

i_to = i_from + to_send_num	
data = numpy.array([A[i_from:i_to],B[i_from:i_to]])


result = []
for i in range(0,len(data[0])):
	result.append(numpy.dot(data[0][i].ravel(),data[1][i].ravel()))

numpy.array(result)

i=numprocs-1
all_results = []
while i>=0:
	print "received from ", i
	all_results.append(comm.recv(source=i,tag=1))
	i=i-1
	
all_results.append(result)	
		
for i in range(0,len(A)):
	print A[i]
	print "__ . __"
	print B[i]
	print all_results[i]
	print

comm.Disconnect()
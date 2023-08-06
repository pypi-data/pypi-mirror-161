import liblip as ll
import sys
import math
import random
import numpy as np
from  _liblip import ffi,lib as fm

# Trace function
def trace( str):
    print( '######')
    print( "## ", str)
    print( '######')
    
# test function, here just a product of sin(2x)sin(2y),...
def fun2( dat, dim):
    s = 1.0
    for j in range( dim): s *= math.sin( 2 * dat[j])
    return s

# generate data randomly
def generate_random_data( dim, npts):
    x, XData, YData = ll.init( dim, npts)
    for i in range( npts):
        for j in range( dim):
            x[j] = random.random() * 3.0
            XData[i * dim + j] = x[j]
        YData[i] = fun2( x, dim)
    return x, XData, YData

###
# Initial test with no wrapper    
# ###  
def initial_test():
    trace( 'initial test: start')
    dim = np.array([3])
    npts = np.array([1500])
    lip_const = np.array([10.0])
    K2 = 100
           
    x, XData, YData = generate_random_data( dim[0], npts[0])

    plip_const = ffi.cast("double *", lip_const.ctypes.data)
    fm.STCSetLipschitz( -1, plip_const)
    
    pXData = ffi.cast("double *", XData.ctypes.data)
    pYData = ffi.cast("double *", YData.ctypes.data)
    pnpts = ffi.cast("int *", npts.ctypes.data)
    pdim = ffi.cast("int *", dim.ctypes.data)
    fm.STCBuildLipInterpolant( -1, pdim, pnpts, pXData, pYData)

    err2 = 0
    err = 0
    for k in range( K2):
        x = np.random.rand( dim[0]) * 3.0 # randomly choose a test point
        px = ffi.cast("double *", x.ctypes.data)
        w = fm.STCValue( -1, px)
        w1 = fun2( x, dim[0]) # the true function
        w = abs( w - w1) # compute the error
        if( err < w): err = w
        err2 += w * w    
    err2 = math.sqrt( err2 / K2) # average error RMSE
    print( "Interpolation max error: ",err)
    print( "Average error: ", err2)
    trace( 'initial test: end')

print( "-- test no wrapper start --")
initial_test()
print( "-- test no wrapper end --")
import liblip as ll
import sys
import math
import random
import time

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
# Initial test    
# ###  
def initial_test():
    trace( 'initial test: start')
    dim = 3
    npts = 1500
    lip_const = 10.0
    K2 = 100
           
    x, XData, YData = generate_random_data( dim, npts)

    ll.STCSetLipschitz( lip_const)
    ll.STCBuildLipInterpolant( dim, npts, XData, YData)

    err2 = 0
    err = 0
    for k in range( K2):
        for j in range( dim): x[j] = random.random() * 3.0 # randomly choose a test point
        w = ll.STCValue( x)
        w1 = fun2( x, dim) # the true function
        w = abs( w - w1) # compute the error
        if( err < w): err = w
        err2 += w * w    
    err2 = math.sqrt( err2 / K2) # average error RMSE
    print( "Interpolation max error: ",err)
    print( "Average error: ", err2)

    # additional to user manual: start
    # STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y);
    res = ll.STCBuildLipInterpolantExplicit( dim, npts, XData, YData);
    print( "Result: ", res)
    # STCValueExplicit( double* x );
    res = ll.STCValueExplicit( XData)
    print( "Result: ", res)
    # STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y);
    res = ll.STCBuildLipInterpolantColumn( dim, npts, XData, YData)
    print( "Result: ", res)
    # STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y);
    res = ll.STCBuildLipInterpolantExplicitColumn( dim, npts, XData, YData)
    print( "Result: ", res)    
    # STCFreeMemory();
    ll.STCFreeMemory()
    # additional to user manual: end

    trace( 'initial test: end')


###
# Initial test class  
# ###  
def initial_test_class():
    trace( 'initial test class: start')
    dim = 3
    npts = 1500
    lip_const = 10.0
    K2 = 100
           
    x, XData, YData = generate_random_data( dim, npts)
    # initialize objects
    gl = ll.STCInterpolant()
    
    gl.SetLipschitz( lip_const)
    gl.BuildLipInterpolant( dim, npts, XData, YData)

    err2 = 0
    err = 0
    for k in range( K2):
        for j in range( dim): x[j] = random.random() * 3.0 # randomly choose a test point
        w = gl.Value( x)
        w1 = fun2( x, dim) # the true function
        w = abs( w - w1) # compute the error
        if( err < w): err = w
        err2 += w * w    
    err2 = math.sqrt( err2 / K2) # average error RMSE
    print( "Interpolation max error: ",err)
    print( "Average error: ", err2)
    trace( 'initial test class: end')

    # additional to user manual: start
    # STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y);
    res = gl.BuildLipInterpolantExplicit( dim, npts, XData, YData);
    print( "Result: ", res)

    # STCValueExplicit( double* x );
    res = gl.ValueExplicit( XData)
    print( "Result: ", res)
    # STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y);
    res = gl.BuildLipInterpolantColumn( dim, npts, XData, YData)
    print( "Result: ", res)

    # STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y);
    res = gl.BuildLipInterpolantExplicitColumn( dim, npts, XData, YData)
    print( "Result: ", res)    
    # STCFreeMemory();
    gl.FreeMemory()
    # additional to user manual: end


###
# example of usage of SLipInt
###
def test_slip_int():
    trace( 'example of usage of SLipInt: start')

    dim=4        # the dimension and size of the data set
    npts=1000
    LipConst=4
    x, XData, YData = generate_random_data( dim, npts)

    for j in range( dim): x[j]=random.random() * 3.0 # some random x
    # calculate the value
    index = [0] * npts
    w = ll.LipIntValue( dim,npts,x,XData, YData,LipConst,index)

    # estimate Lipschitz constant
    ll.LipIntComputeLipschitz(dim,npts,XData, YData)
    # uses the computed Lipschitz constant
    w = ll.LipIntValue(dim,npts,x,XData, YData,LipConst,index)
    print( "w: ", w)
    # the same using local Lipschitz constants  
    ll.LipIntComputeLocalLipschitz(dim,npts,XData, YData)
    # calculate the value
    w = ll.LipIntValueLocal(dim,npts,x,XData, YData)
    print( "w: ", w)
    trace( 'example of usage of SLipInt: end')

###
# example of usage of SLipInt class
###
def test_slip_int_class():
    trace( 'example of usage of SLipInt class: start')

    dim=4        # the dimension and size of the data set
    npts=1000
    LipConst=4
    x, XData, YData = generate_random_data( dim, npts)
    for j in range( dim): x[j]=random.random() * 3.0 # some random x

    # initialize objects
    sli = ll.SLipInt()
    
    # calculate the value
    index = [0] * npts
    w = sli.Value( dim,npts,x,XData, YData,LipConst,index)

    # estimate Lipschitz constant
    sli.ComputeLipschitz(dim,npts,XData, YData)
    # uses the computed Lipschitz constant
    w = sli.Value(dim,npts,x,XData, YData,LipConst,index)
    print( "w: ", w)
    # the same using local Lipschitz constants  
    sli.ComputeLocalLipschitz(dim,npts,XData, YData)
    # calculate the value
    w = sli.ValueLocal(dim,npts,x,XData, YData)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class: end')


###
# example of usage of SLipInt class for monotone interpolation
###
def test_slip_int_for_monotone_interpolation():
    trace( 'example of usage of SLipInt class for monotone interpolation: start')
    dim=4       # the dimension and size of the data set
    npts=50
    LipConst=4
    x, XData, YData = generate_random_data( dim, npts)    
    Region = [1.5] * dim
    # function monotone incr. wrt first variable
    # function monotone decr. wrt first variable
    # unrestricted wrt other variables
    Cons = [0, -1, 0 ,0]

    # calculate the value
    w = ll.LipIntValueCons(dim,npts,Cons,x,XData, YData,LipConst, None)
    # LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index);
    print( "w: ", w)
    
    # assume monotonicity for x<<Region only
    w = ll.LipIntValueConsLeftRegion(dim,npts,Cons,x,XData, YData, LipConst, Region, None)
    print( "w: ", w)
    ll.LipIntComputeLocalLipschitz(dim,npts,XData, YData)
    w = ll.LipIntValueLocalCons(dim,npts,Cons,x,XData, YData)
    print( "w: ", w)
    w = ll.LipIntValueLocalConsLeftRegion(dim,npts,Cons,x,XData, YData,Region)
    print( "w: ", w)
    # --  additional to user manual
    # LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index);
    w2 = ll.LipIntValueAuto( dim,npts,x,XData, YData, None)
    print( "w2: ", w2)
    w3 = ll.LipIntValueConsRightRegion(dim,npts,Cons,x,XData, YData, LipConst, Region, None)
    print( "w3: ", w3)
    # LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
    type = 0
    T = ll.LipIntComputeLipschitzCV( dim, npts, XData, YData, type, None, None, None);
    print( "T: ", T)
    sys.exit()

    # LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W);
    ratio = 0.5
    T = ll.LipIntComputeLipschitzSplit( dim, npts, XData, YData, ratio, type, Cons, Region, w);
    print( "T: ", T)
    lc = ll.LipIntGetLipConst()
    print( "LipConst: ", lc)
    # LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
    res = ll.LipIntComputeScaling( dim, npts, XData, YData);
    print( "Result: ", res)
    S = [0] * npts
    # LipIntGetScaling(double *S) ;
    ll.LipIntGetScaling( S) 
    print( "Scaling: ", S)
    
    # print( "XData: ", XData)
    # ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata);
    aux = ll.ConvertXDataAUX( dim, npts,  XData)
    print( "Converted AUX Data: ", aux)

    # ConvertXData(int *Dim, int* npts,  double* XData);
    X = ll.ConvertXData( dim, npts,  XData)
    print( "Converted XData: ", X)

    # LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps);
    lc = 4
    eps = 0.6
    res = ll.LipIntVerifyMonotonicity( dim, npts, Cons,  XData, YData, lc, eps);
    print( "Result: ", res)
    # LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    res = ll.LipIntVerifyMonotonicityLeftRegion(dim, npts, Cons,  XData, YData, Region, lc, eps);
    print( "Result: ", res)
    # LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    res = ll.LipIntVerifyMonotonicityRightRegion(dim, npts, Cons,  XData, YData, Region, lc, eps);
    print( "Result: ", res)

    trace( 'example of usage of SLipInt class for monotone interpolation: end')

###
# example of usage of SLipInt class for monotone interpolation class
###
def test_slip_int_for_monotone_interpolation_class():
    trace( 'example of usage of SLipInt class for monotone interpolation class: start')
    dim=4       # the dimension and size of the data set
    npts=50
    LipConst=4
    x, XData, YData = generate_random_data( dim, npts)    
    Region = [1.5] * dim
    # function monotone incr. wrt first variable
    # function monotone decr. wrt first variable
    # unrestricted wrt other variables
    Cons = [0, -1, 0 ,0]

    # initialize objects
    sli = ll.SLipInt()
   
    # calculate the value
    w = sli.ValueCons(dim,npts,Cons,x,XData, YData,LipConst, None)
    print( "w: ", w)
    # assume monotonicity for x<<Region only
    w = sli.ValueConsLeftRegion(dim,npts,Cons,x,XData, YData, LipConst, Region, None)
    print( "w: ", w)
    sli.ComputeLocalLipschitz(dim,npts,XData, YData)
    w = sli.ValueLocalCons(dim,npts,Cons,x,XData, YData)
    print( "w: ", w)
    w = sli.ValueLocalConsLeftRegion(dim,npts,Cons,x,XData, YData,Region)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class for monotone interpolation class: end')
    # --  additional to user manual
    # LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index);
    w2 = sli.ValueAuto( dim,npts,x,XData, YData, None)
    print( "w2: ", w2)
    w3 = sli.ValueConsRightRegion(dim,npts,Cons,x,XData, YData, LipConst, Region, None)
    print( "w3: ", w3)
    # LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
    type = 0
    T = sli.ComputeLipschitzCV( dim, npts, XData, YData, type, None, None, None);
    print( "T: ", T)
    # LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W);
    ratio = 0.5
    T = sli.ComputeLipschitzSplit( dim, npts, XData, YData, ratio, type, Cons, Region, w);
    print( "T: ", T)
    
    lc = sli.GetLipConst()
    print( "LipConst: ", lc)
    # LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
    res = sli.ComputeScaling( dim, npts, XData, YData);
    print( "Result: ", res)
    S = [0] * npts
    # LipIntGetScaling(double *S) ;
    S = sli.GetScaling( S) 
    print( "Scaling: ", S)
    
    # ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata);
    aux = sli.ConvertXDataAUX( dim, npts,  XData)
    print( "Converted AUX Data: ", aux)

    # ConvertXData(int *Dim, int* npts,  double* XData);
    X = sli.ConvertXData( dim, npts,  XData)
    print( "Converted XData: ", X)

    # LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps);
    lc = 4
    eps = 0.6
    res = sli.VerifyMonotonicity( dim, npts, Cons,  XData, YData, lc, eps);
    print( "Result: ", res)
    # LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    res = sli.VerifyMonotonicityLeftRegion(dim, npts, Cons,  XData, YData, Region, lc, eps);
    print( "Result: ", res)
    # LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    res = sli.VerifyMonotonicityRightRegion(dim, npts, Cons,  XData, YData, Region, lc, eps);
    print( "Result: ", res)




###
# example of usage of SLipInt class with extra bounds
###
def test_slip_int_with_extra_bounds():
    trace( 'example of usage of SLipInt class with extra bounds: start')
    dim=4        # the dimension and size of the data set
    npts=1000
    LipConst=4

    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)   
    # calculate the value
    w = ll.LipIntValue(dim,npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    # estimate Lipschitz constant
    ll.LipIntComputeLipschitz(dim,npts,XData, YData)
    # uses the computed Lipschitz constant
    w = ll.LipIntValue(dim,npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class with extra bounds: end')

###
# example of usage of SLipInt class with extra bounds class
###
def test_slip_int_with_extra_bounds_class():
    trace( 'example of usage of SLipInt class with extra bounds class: start')
    dim=4        # the dimension and size of the data set
    npts=1000
    LipConst=4

    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)   

    # initialize objects
    sli = ll.SLipInt()

    # calculate the value
    w = sli.Value(dim,npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    # estimate Lipschitz constant
    sli.ComputeLipschitz(dim,npts,XData, YData)
    # uses the computed Lipschitz constant
    w = sli.Value(dim,npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class with extra bounds class: end')


###
# example of usage of STCInterpolant class
###
def test_STCInterpolant():
    trace( 'example of usage of STCInterpolant: start')
    dim=4             # the dimension and size of the data set
    npts=1000

    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)  
    # supply the data and eliminate repeated values
    ll.LipIntSetData(dim,npts, XData,YData,1)
    LipConst = ll.LipIntDetermineLipschitz()
    ll.LipIntSetConstants()  # supply Lipschitz constant
    ll.LipIntConstruct()     # construct the interpolant
    x1 = [0] * 10  # reserve space for at least dim+1 components
    w=ll.LipIntValueDim(dim,x1) # calculate the value
    print( "w: ", w)
    # alternatively, pre-compute the slack variable
    s = 0
    for j in range( 0, dim): s += x1[j]
    x1[dim] = 1.0-s
    w=ll.LipIntValueDim(dim+1,x1)         # calculate the value
    print( "w: ", w)
    w=ll.LipIntValueExplicitDim(dim+1,x1) # same using explicit method
    print( "w: ", w)
    ll.LipIntFreeMemory()  # destroys the interpolant
    trace( 'example of usage of STCInterpolant: end')


###
# example of usage of STCInterpolant class
###
def test_STCInterpolant_class():
    trace( 'example of usage of STCInterpolant class: start')
    # dim=4             # the dimension and size of the data set
    # npts=1000
    # arrays to store the data
    dim = 4
    npts = 1000
    x, XData, YData = generate_random_data( dim, npts)  
    lipInt = []
    for i in range( 0, 10):
        print( "-- Instance: ", i, " dm: ", dim, " npts: ", npts)
        # supply the data and eliminate repeated values
        lipInt.append( ll.STCInterpolant())
        lipInt[i].SetData(dim,npts, XData,YData,1)
        lipConst = lipInt[i].DetermineLipschitz()
        lipInt[i].SetConstants()  # supply Lipschitz constant
        lipInt[i].Construct()     # construct the interpolant
        x1 = [0] * 10  # reserve space for at least dim+1 components
        w = lipInt[i].ValueDim(dim,x1) # calculate the value
        print( "w: ", w)
        # alternatively, pre-compute the slack variable
        s = 0
        for j in range( 0, dim): s += x1[j]
        x1[dim] = 1.0-s
        w =lipInt[i].ValueDim(dim+1,x1)         # calculate the value
        print( "w: ", w)
        w = lipInt[i].ValueExplicitDim(dim+1,x1) # same using explicit method
        print( "w: ", w)
        lipInt[i].FreeMemory()  # destroys the interpolant
    trace( 'example of usage of STCInterpolant class: end')



###
# example using procedural interface
###
def test_procedural_interface():
    trace( 'using procedural interface: start')
    dim=4             # the dimension and the data set
    npts=50

    # arrays to store the data
    LipConst = 10.0
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)

    # compute the Lipschitz constant in max-norm
    ll.LipIntInfComputeLipschitz( dim, npts, XData, YData)
    # calculate the value
    w=ll.LipIntInfValue( dim, npts,x,XData, YData, LipConst, None)
    print( "w: ", w)

    # additipnal to user manual - start 
    # LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index);
    res = ll.LipIntInfValueAuto( dim, npts, x, XData, YData, None)
    print( "Result: ", res)

    # LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double *ipconst, int* Index);
    lc = [4.0]
    Cons = [0, 0, 1, 0]
    res = ll.LipIntInfValueCons( dim, npts, Cons, x, XData, YData,  lc, None);
    print( "Result: ", res)

    Region = 1    
    # LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    res = ll.LipIntInfValueConsLeftRegion( dim, npts, Cons, x, XData, YData,  lc, Region, None)
    print( "Result: ", res)

    # LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    res = ll.LipIntInfValueConsRightRegion( dim, npts, Cons, x, XData, YData,  lc, Region, None)
    print( "Result: ", res)
    
    ll.LipIntInfComputeLocalLipschitz( dim, npts, XData, YData)
    # LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y);
    res = ll.LipIntInfValueLocal( dim, npts, x, XData, YData)  
    # print( "Result: ", res)
    
    # LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);
    res = ll.LipIntInfValueLocalCons( dim, npts, Cons, x, XData, YData)
    print( "Result: ", res)

    # LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    res = ll.LipIntInfValueLocalConsLeftRegion( dim, npts, Cons, x, XData, YData, Region)
    print( "Result: ", res)
    
    # LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    res = ll.LipIntInfValueLocalConsRightRegion( dim, npts, Cons, x, XData, YData, Region)
    print( "Result: ", res)

    # LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
    type = 0
    T = ll.LipIntInfComputeLipschitzCV( dim, npts, XData, YData, type, None, None, None)
    print( "T: ", T)

    # LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W);
    ratio = 0.5
    T = ll.LipIntInfComputeLipschitzSplit(dim, npts, XData, YData, ratio, type, None, None, None)
    print( "T: ", T)

    # LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
    Region = [1.5] * dim
    # function monotone incr. wrt first variable
    # function monotone decr. wrt first variable
    # unrestricted wrt other variables
    Cons = [0, -1, 0 ,0]
    fW = 1
    fC = 1
    fR = 1
    W = [1.0] * npts
    lc = ll.LipIntGetLipConst()
    T = ll.LipIntInfSmoothLipschitz(dim, npts, XData, YData, lc, fW, fC, fR, W, Cons, Region)
    print( "T: ", T)
    
    # LipIntInfGetLipConst() ;
    res = ll.LipIntInfGetLipConst()
    print( "Result: ", res) 
    
    # LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
    res = ll.LipIntInfComputeScaling(dim, npts, XData, YData);
    print( "Result: ", res) 

    # LipIntInfGetScaling(double *S)
    s = ll.LipIntInfGetScaling( dim)
    print( "Scaling: ", s)

    # LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep);
    eps = 0.5
    res = ll.LipIntInfVerifyMonotonicity( dim, npts, Cons, XData, YData, lc, eps)
    print( "Result: ", res) 
    
    # LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    Region = [1.5] * dim
    res = ll.LipIntInfVerifyMonotonicityLeftRegion( dim, npts, Cons, XData, YData, Region, lc, eps)
    print( "Result: ", res) 
    
    # LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    res = ll.LipIntInfVerifyMonotonicityRightRegion( dim, npts, Cons, XData, YData, Region, lc, eps)
    print( "Result: ", res) 

    # LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC);
    T = ll.LipIntInfSmoothLipschitzSimp(dim, npts, XData, YData, lc)
    print( "T: ", T)
    
    # LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W);
    T = ll.LipIntInfSmoothLipschitzSimpW(dim, npts, XData, YData, lc, w)
    print( "T: ", T)
    sys.exit()

    # additipnal to user manual - end
    # the same in Euclidean norm, but using local Lipschitz values
    ll.LipIntComputeLocalLipschitz( dim, npts, XData, YData)
    # calculate the value
    w=ll.LipIntValueLocal( dim, npts,x,XData, YData)
    print( "w: ", w)
    # now using fast method and simplicial distance
    ll.STCSetLipschitz( LipConst)  # supply Lipschitz constant
    # suppy the data
    ll.STCBuildLipInterpolant( dim, npts, XData, YData)
    w=ll.STCValue( x) # calculate the value
    print( "w: ", w)
    trace( 'using procedural interface: end')


###
# example using procedural interface class
###
def test_procedural_interface_class():
    trace( 'using procedural interface class: start')
    dim=4             # the dimension and the data set
    npts=50

    # arrays to store the data
    LipConst = 10.0
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)

    sli = ll.SLipIntInf()
    sli2 = ll.SLipIntInf()
    sli3 = ll.SLipIntInf()
    
    # compute the Lipschitz constant in max-norm
    # ll.LipIntInfComputeLipschitz( 0, dim, npts, XData, YData)
    sli.ComputeLipschitz( dim, npts, XData, YData)
    # calculate the value
    # w=ll.LipIntInfValue( 0, dim, npts,x,XData, YData, LipConst, None)
    w = sli.Value( dim, npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    # the same in Euclidean norm, but using local Lipschitz values
    sl = ll.SLipInt()
    # ll.LipIntComputeLocalLipschitz( dim, npts, XData, YData)
    sl.ComputeLocalLipschitz( dim, npts, XData, YData)
    # calculate the value
    # w=ll.LipIntValueLocal( dim, npts,x,XData, YData)
    w = sl.ValueLocal( dim, npts,x,XData, YData)
    print( "w: ", w)
    # now using fast method and simplicial distance
    lipInt = ll.STCInterpolant()
    # ll.STCSetLipschitz( LipConst)  # supply Lipschitz constant
    lipInt.SetLipschitz( LipConst)
    # suppy the data
    # ll.STCBuildLipInterpolant( dim, npts, XData, YData)
    lipInt.BuildLipInterpolant( dim, npts, XData, YData)
    # w=ll.STCValue( x) # calculate the value
    w = lipInt.Value( x)
    print( "w: ", w)
    # additipnal to user manual - start 
    # LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index);
    res = sli.ValueAuto( dim, npts, x, XData, YData, None)
    print( "Result: ", res)
    # LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double *ipconst, int* Index);
    lc = [4.0]
    Cons = [0, 0, 1, 0]
    res = sli.ValueCons( dim, npts, Cons, x, XData, YData,  lc, None);
    print( "Result: ", res)

    Region = 1    
    # LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    res = sli.ValueConsLeftRegion( dim, npts, Cons, x, XData, YData,  lc, Region, None)
    print( "Result: ", res)

    # LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    res = sli.ValueConsRightRegion( dim, npts, Cons, x, XData, YData,  lc, Region, None)
    print( "Result: ", res)
    
    sli.ComputeLocalLipschitz( dim, npts, XData, YData)
    # LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y);
    res = sli.ValueLocal( dim, npts, x, XData, YData)  
    # print( "Result: ", res)
    
    # LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);
    res = sli.ValueLocalCons( dim, npts, Cons, x, XData, YData)
    print( "Result: ", res)

    # LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    res = sli.ValueLocalConsLeftRegion( dim, npts, Cons, x, XData, YData, Region)
    print( "Result: ", res)
    
    # LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    res = sli.ValueLocalConsRightRegion( dim, npts, Cons, x, XData, YData, Region)
    print( "Result: ", res)

    # LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
    type = 0
    T = sli.ComputeLipschitzCV( dim, npts, XData, YData, type, None, None, None)
    print( "T: ", T)

    # LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W);
    ratio = 0.5
    T = sli.ComputeLipschitzSplit(dim, npts, XData, YData, ratio, type, None, None, None)
    print( "T: ", T)
  

    # LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
    Region = [1.5] * dim
    # function monotone incr. wrt first variable
    # function monotone decr. wrt first variable
    # unrestricted wrt other variables
    Cons = [0, -1, 0 ,0]
    fW = 1
    fC = 1
    fR = 1
    W = [1.0] * npts
    lc = ll.LipIntGetLipConst()
    T = sli.SmoothLipschitz(dim, npts, XData, YData, lc, fW, fC, fR, W, Cons, Region) 
    print( "T: ", T)

    # LipIntInfGetLipConst() ;
    res = sli.GetLipConst()
    print( "Result: ", res) 
    
    # LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
    res = sli.ComputeScaling(dim, npts, XData, YData);
    print( "Result: ", res) 

    # LipIntInfGetScaling(double *S)
    s = sli.GetScaling( dim)
    print( "Scaling: ", s)

    # LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep);
    eps = 0.5
    res = sli.VerifyMonotonicity( dim, npts, Cons, XData, YData, lc, eps)
    print( "Result: ", res) 
    
    # LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    Region = [1.5] * dim
    res = sli.VerifyMonotonicityLeftRegion( dim, npts, Cons, XData, YData, Region, lc, eps)
    print( "Result: ", res) 
    
    # LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    res = sli.VerifyMonotonicityRightRegion( dim, npts, Cons, XData, YData, Region, lc, eps)
    print( "Result: ", res) 

    # LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC);
    T = sli.SmoothLipschitzSimp(dim, npts, XData, YData, lc)
    print( "T: ", T)
    
    # LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W);
    T = sli.SmoothLipschitzSimpW(dim, npts, XData, YData, lc, w)
    print( "T: ", T)
    # additipnal to user manual - end

    trace( 'using procedural interface class: end')


###
# example for smoothing
###
def test_smoothing():
    trace( 'example for smoothing: start')
    dim=4        # the dimension and size of the data set
    npts=200
    LipConst=4.0
   
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)
    for i in range( 0, npts): 
        YData[i] = fun2( x, dim)+ 0.1 * ( random.random() - 1)  # noisy function values
    # LipIntSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region)
    fR = 1
    # weights
    # W = [1.0] * dim
    W = None
    Region = [1.5] * dim
    # function monotone incr. wrt first variable
    # function monotone decr. wrt first variable
    # unrestricted wrt other variables
    # Cons = [0, -1, 0 ,0] # array of size dim
    Cons = None
    T = ll.LipIntSmoothLipschitz(dim, npts,XData,YData, LipConst, fR,  W, Cons, Region)
    print( "T: ", T)
    sys.exit()

    # calculate the approximation at x
    w = ll.LipIntValue( dim,npts,x,XData, TData, LipConst, None)
    print( "w: ", w)
    # prepare data for the fast method using simplicial distance
    ll.LipIntInfSmoothLipschitzSimp( dim, npts,XData,YData,TData,LipConst)
    ll.LipIntSetData(dim,npts, XData,TData, 0)
    ll.STCSetLipschitz(LipConst)  # supply Lipschitz constant
    ll.LipIntConstruct()     # construct the interpolant
    x1 = [0.0] * 10  # reserve space for at least dim+1 components
    for j in range( 0, dim): x1[j] = random.random() * 3.0 # some random x
    w = ll.STCValue( x1) # calculate the value
    print( "w: ", w)
    trace( 'example for smoothing: end')


###
# example for smoothing using object wrapper
###
def test_smoothing_class():
    trace( 'example for smoothing class: start')
    dim=4        # the dimension and size of the data set
    npts=200
    LipConst=4.0
   
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)
    TData = [0.0] * npts
    for i in range( 0, npts): 
        YData[i] = fun2( x, dim)+ 0.1 * ( random.random() - 1)  # noisy function values
    # LipIntSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region)
    # ll.LipIntSmoothLipschitz(dim, npts,XData,YData,TData,LipConst, None, None, None, None, None, None)
    
    # initialize objects
    gl = ll.STCInterpolant()
    sli = ll.SLipInt()
    slii = ll.SLipIntInf()
    
    # calculate the approximation at x
    w = sli.Value( dim,npts,x,XData, TData, LipConst, None)
    print( "w: ", w)
    # prepare data for the fast method using simplicial distance
    slii.SmoothLipschitzSimp( dim, npts,XData,YData,TData,LipConst)
    gl.SetData(dim,npts, XData,TData, 0)
    gl.SetLipschitz(LipConst)  # supply Lipschitz constant
    gl.Construct()     # construct the interpolant
    x1 = [0.0] * 10  # reserve space for at least dim+1 components
    for j in range( 0, dim): x1[j] = random.random() * 3.0 # some random x
    w = gl.Value( x1) # calculate the value
    print( "w: ", w)
    trace( 'example for smoothing class: end')

###
# example of usage of STCInterpolant class and smoothened data
###
def test_STCInterpolant_smoothened_data():
    trace( 'example of usage of STCInterpolant class and smoothened data: start')
    dim=3             # the dimension and size of the data set
    npts=1000
    LipConst=2.5
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)
    TData = [0.0] * npts

    # smoothen the data
    ll.LipIntInfSmoothLipschitzSimp( dim,npts,XData,YData,TData,LipConst)
    # supply the smoothened data (TData, not YData)
    ll.LipIntSetData(dim,npts, XData,TData,0)
    ll.STCSetLipschitz(LipConst)  # supply Lipschitz constant
    ll.LipIntConstruct()          # construct the interpolant
    x1= [0.0] * 10  # reserve space for at least dim+1 components
    for j in range( 0, dim): x1[j] = random.random() * 3.0 # some random x
    w = ll.STCValue( x1) # calculate the value
    print( "w: ", w)
    # alternatively, pre-compute the slack variable
    s = 0
    for j in range( 0, dim): s += x1[j] 
    x1[dim] = 1.0 - s
    w = ll.STCValue( x1)         # calculate the value
    print( "w: ", w)
    ll.LipIntFreeMemory()  # destroys the interpolant
    trace( 'example of usage of STCInterpolant class and smoothened data: end')

###
# example of usage of STCInterpolant class and smoothened data using object wrapper
###
def test_STCInterpolant_smoothened_data_class():
    trace( 'example of usage of STCInterpolant class and smoothened data class: start')
    dim=3             # the dimension and size of the data set
    npts=1000
    LipConst=2.5
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)
    TData = [0.0] * npts

    # initialize objects
    gl = ll.STCInterpolant()
    sli = ll.SLipInt()
    slii = ll.SLipIntInf()

    # smoothen the data
    slii.SmoothLipschitzSimp( dim,npts,XData,YData,TData,LipConst)
    # supply the smoothened data (TData, not YData)
    sli.SetData(dim,npts, XData,TData,0)
    gl.SetLipschitz(LipConst)  # supply Lipschitz constant
    sli.Construct()          # construct the interpolant
    x1= [0.0] * 10  # reserve space for at least dim+1 components
    for j in range( 0, dim): x1[j] = random.random() * 3.0 # some random x
    w = gl.Value( x1) # calculate the value
    print( "w: ", w)
    # alternatively, pre-compute the slack variable
    s = 0
    for j in range( 0, dim): s += x1[j] 
    x1[dim] = 1.0 - s
    w = gl.Value( x1)         # calculate the value
    print( "w: ", w)
    sli.FreeMemory()  # destroys the interpolant
    trace( 'example of usage of STCInterpolant class and smoothened data class: end')


###
# Main test program
###
print( "-- test wrapper start --")

test_case = 2

if test_case == 1: initial_test() 
elif test_case == 2: initial_test_class() 
elif test_case == 3: test_slip_int()
elif test_case == 4: test_slip_int_class()
elif test_case == 5: test_slip_int_for_monotone_interpolation()
elif test_case == 6: test_slip_int_for_monotone_interpolation_class()
elif test_case == 7:  test_slip_int_with_extra_bounds()
elif test_case == 8:  test_slip_int_with_extra_bounds_class()
elif test_case == 9:  test_STCInterpolant()
elif test_case == 10:  test_STCInterpolant_class()
elif test_case == 11:  test_procedural_interface()
elif test_case == 12:  test_procedural_interface_class()
elif test_case == 13:  test_smoothing()
elif test_case == 14:  test_smoothing_class()
elif test_case == 15:  test_STCInterpolant_smoothened_data()
elif test_case == 16:  test_STCInterpolant_smoothened_data_class()
print( "-- test wrapper end --")
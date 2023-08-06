""" Python wrapper for liblip for multivariate scattered data interpolation. 

Simplifies the usage of liblip by handling all Numpy and CFFI calls
The Lipschitz interpolant possesses a number of desirable features, such
 as continuous dependence on the data, preservation of Lipschitz properties 
 and of the range of the data, uniform approximation and best error bounds. 
 On the practical side, construction and evaluation of the interpolant is 
 com- putationally stable. There is no accumulation of errors with the size 
 of the data set and dimension.
In addition to the Lipschitz constant, the user can provide information about 
other properties of f, such as monotonicity with respect to any subset of variables, 
upper and lower bounds (not necessarily constant bounds). If the data are given with errors, 
then it can be smoothened to satisfy the required properties. The Lipschitz constant, 
if unknown, can be estimated from the data using sample splitting and cross-validation techniques. 
The library also provides methods for approximation of locally Lipschitz functions.<br>

This file can also be imported as a module and contains the following
functions:
    * init - initializes package data
    * free - frees package data  
    * STCSetLipschitz
    * STCBuildLipInterpolant
    * STCValue
"""
import numpy as np
import math
from  _liblip import ffi, lib as fm

###
# Helper functions
###

# global variable to support trace-info while testing
isTest = True

# decorator to execute a function once
def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

# Trace function
def trace( str):
    if isTest == True: print( "-- ", str, " --")

@run_once
def trace_once( str):
    trace( str)
    
# use numpy to create an intc array with n zeros and cast to CFFI 
def create_intc_zeros_as_CFFI_int( n):
    x = np.zeros( n, np.intc)
    px = ffi.cast( "int *", x.ctypes.data)
    return x, px

# use numpy to create an float array with n zeros and cast to CFFI 
def create_float_zeros_as_CFFI_double( n):
    x = np.zeros( n, float)
    px = ffi.cast( "double *", x.ctypes.data)
    return x, px

def convert_py_float_to_cffi( x):
    if isinstance( x, np.ndarray) == True:
        px = x
    else:
        if x != None:
            px = np.array( x)
            if px.dtype != "float64": px = px.astype( float)
        else:
            # handle None
            px = np.array( 0.0)
            pxcffi = ffi.cast( "double *", 0.0)    
    pxcffi = ffi.cast( "double *", px.ctypes.data)
    return px, pxcffi


def convert_py_int_to_cffi( x):
    if x != None:
        x = np.intc( x)
        px = np.array( x)
        pxcffi = ffi.cast( "int *", px.ctypes.data)
    else: 
        # handle None
        px = np.array( 0)
        pxcffi = ffi.cast( "int *", 0)
    return px, pxcffi
   

###
# Python wrapper classes 
###
class STCInterpolant():
    def __init__( self):
        # constructor
        self.id = fm.STCInterpolantInit()
        trace( f"STCInterpolant Id: {self.id}")
    def Construct( self): 
        LipIntConstruct( self.id)
    def DetermineLipschitz( self):
        return LipIntDetermineLipschitz( self.id)
    def FreeMemory( self):
        STCFreeMemory( self.id)
    def SetConstants( self):
        LipIntSetConstants( self.id)
    def ValueExplicitDim( self, dim, x):
        return LipIntValueExplicitDim( dim, x, self.id)
    def ValueDim( self, dim, x):
        return LipIntValueDim( dim, x, self.id)
    def SetData( self, dim, K, x, y, test):
        LipIntSetData( dim, K, x, y, test, self.id)
    def SetLipschitz( self, LipConst):
        STCSetLipschitz( LipConst, self.id)
    def BuildLipInterpolant( self, dim, npts, XData, YData):
        STCBuildLipInterpolant( dim, npts, XData, YData, self.id)
    def Value( self, x):
        return STCValue( x, self.id)
    def BuildLipInterpolantExplicit( self, Dim, Ndata, x, y):
        return STCBuildLipInterpolantExplicit( Dim, Ndata, x, y, self.id)
    def BuildLipInterpolantColumn( self, Dim, Ndata, x, y):
        return STCBuildLipInterpolantColumn( Dim, Ndata, x, y, self.id)
    def BuildLipInterpolantExplicitColumn( self, Dim, Ndata, x, y):
        return STCBuildLipInterpolantExplicitColumn( Dim, Ndata, x, y, self.id)
    def ValueExplicit( self, x):
        return STCValueExplicit( x, self.id)

    def __del__( self):
        # destructor
        trace( f"STCInterpolant Del Id: {self.id}")
        fm.STCInterpolantDel( self.id)
        self.id = -1

class SLipInt():
    def __init__( self):
        # constructor
        self.id = fm.SLipIntInit()
        trace( f"SLipInt Id: {self.id}")
    def ComputeLocalLipschitz( self, dim, npts, XData, YData):
        LipIntComputeLocalLipschitz( dim, npts, XData, YData, self.id)
    def ValueLocal( self, dim, npts,x,XData, YData):
        return LipIntValueLocal( dim, npts,x,XData, YData, self.id)
    def Value( self, Dim, Ndata, x, Xd, y, Lipconst, Index):
        return LipIntValue( Dim, Ndata, x, Xd, y, Lipconst, Index, self.id)
    def ValueAuto( self,  Dim,  Ndata,  x, Xd,  y,  Index):
        LipIntValueAuto(  Dim,  Ndata,  x, Xd,  y,  Index, self.id)
    def ValueCons( self,  Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Index):
        LipIntValueCons(  Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Index, self.id)
    def ValueConsLeftRegion( self, Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index):
        LipIntValueConsLeftRegion(  Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index, self.id)
    def ValueConsRightRegion(  self, Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index):
        LipIntValueConsRightRegion(  Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index, self.id)
    def ValueLocalCons( self, Dim, Ndata, Cons, x, Xd, y):
        LipIntValueLocalCons(Dim, Ndata, Cons, x, Xd, y, self.id)
    def ValueLocalConsLeftRegion( self, Dim,  Ndata, Cons,  x,  Xd, y,  Region):
        LipIntValueLocalConsLeftRegion(  Dim,  Ndata, Cons,  x,  Xd, y,  Region, self.id)
    def ValueLocalConsRightRegion( self, Dim,  Ndata, Cons,  x,  Xd, y,  Region):
        LipIntValueLocalConsRightRegion(  Dim,  Ndata, Cons,  x,  Xd, y,  Region, self.id)
    def ComputeLipschitz( self, Dim,  Ndata,  x,  y):
        LipIntComputeLipschitz(  Dim,  Ndata,  x,  y, self.id)
    def ComputeLipschitzCV( self, Dim,  Ndata,  Xd,  y,  type,  Cons,  Region,  W):
        return LipIntComputeLipschitzCV(  Dim,  Ndata,  Xd,  y,  type,  Cons,  Region,  W, self.id)
    def ComputeLipschitzSplit( self, Dim,  Ndata,  Xd,  y,  ratio, type,  Cons,  Region,  W):
        return LipIntComputeLipschitzSplit(  Dim,  Ndata,  Xd,  y,  ratio, type,  Cons,  Region,  W, self.id)
    def SmoothLipschitz( self, Dim,  Ndata,   Xd,  y,  LC, fR,  W,  Cons,  Region):
        return LipIntSmoothLipschitz(  Dim,  Ndata,   Xd,  y,  LC,  fR,  W,  Cons,  Region, self.id)
    def GetLipConst( self):
        LipIntGetLipConst(  self.id)
    def GetScaling( self, S):
        LipIntGetScaling(  S, self.id)
    def ComputeScaling( self, Dim,  Ndata,  XData,  YData):
        LipIntComputeScaling(  Dim,  Ndata,  XData,  YData, self.id)
    def ConvertXData( self, Dim,  npts,   XData):
        return ConvertXData(  Dim,  npts,   XData, self.id)
    def ConvertXDataAUX( self, Dim,  npts,   XData):
        return ConvertXDataAUX(  Dim,  npts,   XData, self.id)
    def	VerifyMonotonicity( self, Dim,  npts,  Cons,   XData,  YData,  LC,  eps):
        LipIntVerifyMonotonicity(  Dim,  npts,  Cons,   XData,  YData,  LC,  eps, self.id)
    def	VerifyMonotonicityLeftRegion( self, Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps):
        LipIntVerifyMonotonicityLeftRegion(  Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps, self.id)
    def	VerifyMonotonicityRightRegion( self, Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps):
        LipIntVerifyMonotonicityRightRegion(  Dim,  npts, Cons,   XData,  YData,  Region,  LC,  eps, self.id)
    def Construct( self):
        LipIntConstruct(  self.id)
    def DetermineLipschitz( self):
        LipIntDetermineLipschitz( self.id)
    def FreeMemory( self):
        LipIntFreeMemory( self.id)
    def SetConstants( self):
        LipIntSetConstants(  self.id)
    def ValueExplicitDim( self, dim,  x):
        LipIntValueExplicitDim(  dim,  x, self.id)
    def ValueDim( self, dim,  x):
        LipIntValueDim(  dim,  x, self.id)
    def SetData( self, dim,  K,  x,  y,  test):
        LipIntSetData(  dim,  K,  x,  y,  test, self.id)    
    def __del__( self):
        # destructor
        trace( f"SLipInt Del Id: {self.id}")
        fm.SLipIntDel( self.id)
        self.id = -1

class SLipIntInf():
    def __init__( self):
        # constructor
        self.id = fm.SLipIntInfInit()
        trace( f"SLipIntInf Id: {self.id}")
    def ComputeLipschitz( self, dim, npts, XData, YData):
        LipIntInfComputeLipschitz( dim, npts, XData, YData, self.id)
    def Value( self, dim, npts,x,XData, YData, LipConst, Index):
        return LipIntInfValue( dim, npts,x,XData, YData, LipConst, Index, self.id)
    def SmoothLipschitzSimp( self, Dim, npts, XData, YData, LC):
        return LipIntInfSmoothLipschitzSimp(Dim, npts, XData, YData, LC, self.id)
    def ValueAuto( self, Dim,  Ndata,  x, Xd,  y,  Index):
        return LipIntInfValueAuto( Dim,  Ndata,  x, Xd,  y,  Index, self.id)
    def ValueCons(  self, Dim,  Ndata,  Cons,  x,  Xd, y,  Lipconst,  Index):
        return LipIntInfValueCons(  Dim,  Ndata,  Cons,  x,  Xd, y,  Lipconst,  Index, self.id)
    def ValueConsLeftRegion( self, Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index):
        return LipIntInfValueConsLeftRegion( Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index, self.id)
    def ValueConsRightRegion( self, Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index):
        return LipIntInfValueConsRightRegion(  Dim,  Ndata,  Cons,  x,  Xd, y,   Lipconst,  Region,  Index, self.id)
    def ValueLocal( self, Dim,  Ndata,  x,  Xd, y):
        return LipIntInfValueLocal(  Dim,  Ndata,  x,  Xd, y, self.id)
    def ValueLocalCons( self, Dim,  Ndata, Cons,  x,  Xd, y):
        return LipIntInfValueLocalCons(  Dim,  Ndata, Cons,  x,  Xd, y, self.id)
    def ValueLocalConsLeftRegion( self, Dim,  Ndata, Cons,  x,  Xd, y,  Region):
        return LipIntInfValueLocalConsLeftRegion(  Dim,  Ndata, Cons,  x,  Xd, y,  Region, self.id)
    def ValueLocalConsRightRegion( self, Dim,  Ndata, Cons,  x,  Xd, y,  Region):
        return LipIntInfValueLocalConsRightRegion( Dim,  Ndata, Cons,  x,  Xd, y,  Region, self.id)
    def ComputeLocalLipschitz( self, Dim,  Ndata,  x,  y):
        LipIntInfComputeLocalLipschitz(  Dim,  Ndata,  x,  y, self.id)
    def ComputeLipschitzCV( self, Dim,  Ndata,  Xd,  y,  type,  Cons,  Region, W):
        return LipIntInfComputeLipschitzCV(  Dim,  Ndata,  Xd,  y,   type,  Cons,  Region, W, self.id)
    def ComputeLipschitzSplit( self, Dim,  Ndata,  Xd,  y,  ratio,  type,  Cons,  Region, W):
        return LipIntInfComputeLipschitzSplit(  Dim,  Ndata,  Xd,  y,  ratio,  type,  Cons,  Region, W, self.id)
    def SmoothLipschitz( self, Dim,  Ndata,   Xd,  y,  LC,  fW,  fC,  fR,  W,  Cons,  Region):
        return LipIntInfSmoothLipschitz(  Dim,  Ndata,   Xd,  y, LC,   fW,  fC,  fR,  W,  Cons,  Region, self.id)
    def GetLipConst( self):       
        return LipIntInfGetLipConst(  self.id)
    def GetScaling( self, dim): 
        return LipIntInfGetScaling( dim, self.id) 
    def ComputeScaling( self, Dim,  Ndata,  XData,  YData):
        return LipIntInfComputeScaling( Dim,  Ndata,  XData,  YData, self.id)
    def VerifyMonotonicity( self, Dim,  npts,  Cons,   XData,  YData, LC, ep):
        return LipIntInfVerifyMonotonicity( Dim,  npts,  Cons,   XData,  YData, LC, ep, self.id)
    def VerifyMonotonicityLeftRegion( self, Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps):
        return LipIntInfVerifyMonotonicityLeftRegion(  Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps, self.id)
    def VerifyMonotonicityRightRegion( self, Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps):
        return LipIntInfVerifyMonotonicityRightRegion(  Dim,  npts,  Cons,   XData,  YData,  Region,  LC,  eps, self.id)
    def SmoothLipschitzSimpW( self, Dim,  npts,   XData,  YData,  LC,  W):
        return LipIntInfSmoothLipschitzSimpW(  Dim,  npts,   XData,  YData,  LC,  W, self.id)

    def __del__( self):
        # destructor
        trace( f"SLipIntInf Del Id: {self.id}")
        fm.SLipIntInfDel( self.id)
        self.id = -1

class SlipintLp():
    def __init__( self):
        # constructor
        self.id = fm.SlipintLpInit()
        trace( f"SlipintLp Id: {self.id}")

    def __del__( self):
        # destructor
        trace( f"SlipintLp Del Id: {self.id}")
        fm.SlipintLpDel( self.id)
        self.id = -1

###
# The python minimum wrapper 
###

def init( dim, npts):
    """Initializes the package data

    Args:
        dim (int): The number of dimensions
        npts (int): The number of points per dimension
        y (target function: Function to initialize YData. (default is NaN)

    Returns:
        x, XData, YData (float arrays): Data initialised with 0
    """
    trace( "init")        
    x = np.zeros( dim + 1, float)
    XData = np.zeros( dim * npts, float) 
    YData = np.zeros( npts, float)
    
    return x, XData, YData

def free():
    """Frees the package data

    Args:
        no arguments
    Returns:
        0: no error 
    """
    trace( "free")        
    return 0   

# Python wrapper for:
#    void STCSetLipschitz(double* x)
def STCSetLipschitz( lip_const, id = 0):
    """Supplies the Lipschitz constant

    Args:
        lip_cost (float): Lipschitz constant

    Returns:
        no return value
    """
    trace( "void STCSetLipschitz(double* x)")
    plip_constnp, plip_const = convert_py_float_to_cffi( lip_const)
    fm.STCSetLipschitz( id, plip_const)    


# Python wrapper for:
#    int STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolant( Dim, Ndata, x, y, id = 0):
    """Builds Lipschitz interpolant using the simplicial distance for 
    subsequent fast evaluation. 

    Args:
    Dim (int): dimension of the data set 
    Ndata (int): the size of the data set
    x (float array): abscissae of the data, stored rowwise
    y (float array): values to be interpolated
    Returns:
        Lipschitz interpolant
    """
    trace( "int STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)

    return fm.STCBuildLipInterpolant( id, pDim, pNdata, px, py)


# Python wrapper for:
#    double STCValue( double* x );
def STCValue( x, id = 0):
    """Computes the value of the interpolant at any given point x, using fast method.
    Must be called after STCBuildLipInterpolant() procedure.

    Args:
        x (float array): point

    Returns:
        (foat): interpolant
    """
    trace_once( "double STCValue( double* x );")
    pxnp, px = convert_py_float_to_cffi( x)
    
    return fm.STCValue( id, px)

###
# Remaining wrapper functions 
###

# Python wrapper for:
#    double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntValue(Dim, Ndata, x, Xd, y, Lipconst, Index, id = 0):
    """LipIntValue

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)

    yy = fm.LipIntValue( id, pDim, pNdata, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)
def LipIntValueAuto(Dim, Ndata, x, Xd, y, Index, id = 0):
    """LipIntValueAuto

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueAuto( id, pDim, pNdata, px, pXd, py, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index, id = 0):
    """LipIntValueCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueCons( id, pDim, pNdata, pCons, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index, id = 0):
    """LipIntValueConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueConsLeftRegion( id, pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index, id = 0):
    """LipIntValueConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueConsRightRegion( id, pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
def LipIntValueLocal(Dim, Ndata, x, Xd, y, id = 0):
    """LipIntValueLocal

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntValueLocal( id, pDim, pNdata, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
def LipIntValueLocalCons(Dim, Ndata, Cons, x, Xd, y, id = 0):
    """LipIntValueLocalCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntValueLocalCons( id, pDim, pNdata, pCons, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region, id = 0):
    """LipIntValueLocalConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntValueLocalConsLeftRegion( id, pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region, id = 0):
    """LipIntValueLocalConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntValueLocalConsRightRegion( id, pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntComputeLipschitz(Dim, Ndata, x, y, id = 0):
    """LipIntComputeLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntComputeLipschitz( id, pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void 	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntComputeLocalLipschitz(Dim, Ndata, x, y, id = 0):
    """LipIntComputeLocalLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void 	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntComputeLocalLipschitz( id, pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
def LipIntComputeLipschitzCV(Dim, Ndata, Xd, y, type, Cons, Region, W, id = 0):
    """LipIntComputeLipschitzCV

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    T = [0.0] * Ndata
    pTnp, pT = convert_py_float_to_cffi( T)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntComputeLipschitzCV( id, pDim, pNdata, pXd, py, pT, ptype, pCons, pRegion, pW)
    return pTnp


# Python wrapper for:
#    void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W)
def LipIntComputeLipschitzSplit(Dim, Ndata, Xd, y, ratio, type, Cons, Region, W, id = 0):
    """LipIntComputeLipschitzSplit

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        ratio (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    T = [0.0] * Ndata
    pTnp, pT = convert_py_float_to_cffi( T)
    prationp, pratio = convert_py_float_to_cffi( ratio)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntComputeLipschitzSplit( id, pDim, pNdata, pXd, py, pT, pratio, ptype, pCons, pRegion, pW)
    return pTnp


# Python wrapper for:
#    void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
def LipIntSmoothLipschitz(Dim, Ndata, Xd, y, LC, fR, W, Cons, Region, id = 0):
    """LipIntSmoothLipschitz

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        LC (float):
        fW (int):
        fC (int):
        fR (int):
        W (float):
        Cons (int):
        Region (float):

    Returns:
        <none>
    """
    trace( "void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    T = [0.0] * Ndata
    pTnp, pT = convert_py_float_to_cffi( T)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    if W is None:
        fW = [0.0]
    else:
        fW = [1.0]
    if Cons is None:
        fC = [0.0]
    else:
        fC = [1.0]
    pfWnp, pfW = convert_py_int_to_cffi( fW)
    pfCnp, pfC = convert_py_int_to_cffi( fC)
    pfRnp, pfR = convert_py_int_to_cffi( fR)
    pWnp, pW = convert_py_float_to_cffi( W)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    fm.LipIntSmoothLipschitz( id, pDim, pNdata, pXd, py, pT, pLC, pfW, pfC, pfR, pW, pCons, pRegion)
    return pTnp


# Python wrapper for:
#    double	LipIntGetLipConst() 
def LipIntGetLipConst(id = 0):
    """LipIntGetLipConst

    Args:

    Returns:
        (double):
    """
    trace( "double	LipIntGetLipConst() ")
    yy = fm.LipIntGetLipConst( id)
    return yy


# Python wrapper for:
#    void		LipIntGetScaling(double *S) 
def LipIntGetScaling(S, id = 0):
    """LipIntGetScaling

    Args:
        S (float):

    Returns:
        <none>
    """
    trace( "void		LipIntGetScaling(double *S) ")
    pSnp, pS = convert_py_float_to_cffi( S)
    fm.LipIntGetScaling( id, pS)
    return 


# Python wrapper for:
#    int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
def LipIntComputeScaling(Dim, Ndata, XData, YData, id = 0):
    """LipIntComputeScaling

    Args:
        Dim (int):
        Ndata (int):
        XData (float):
        YData (float):

    Returns:
        (int):
    """
    trace( "int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    yy = fm.LipIntComputeScaling( id, pDim, pNdata, pXData, pYData)
    return yy


# Python wrapper for:
#    void	ConvertXData(int *Dim, int* npts,  double* XData)
def ConvertXData(Dim, npts, XData, id = 0):
    """ConvertXData

    Args:
        Dim (int):
        npts (int):
        XData (float):

    Returns:
        <none>
    """
    trace( "void	ConvertXData(int *Dim, int* npts,  double* XData)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    fm.ConvertXData( id, pDim, pnpts, pXData)
    return pXDatanp


# Python wrapper for:
#    void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata)
def ConvertXDataAUX(Dim, npts, XData, id = 0):
    """ConvertXDataAUX

    Args:
        Dim (int):
        npts (int):
        XData (float):
        auxdata (float):

    Returns:
        <none>
    """
    trace( "void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    auxdata = [0.0] * npts
    pauxdatanp, pauxdata = convert_py_float_to_cffi( auxdata)
    fm.ConvertXDataAUX( id, pDim, pnpts, pXData, pauxdata)
    return pauxdatanp


# Python wrapper for:
#    int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)
def LipIntVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, eps, id = 0):
    """LipIntVerifyMonotonicity

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntVerifyMonotonicity( id, pDim, pnpts, pCons, pXData, pYData, pLC, peps)
    return yy


# Python wrapper for:
#    int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps, id = 0):
    """LipIntVerifyMonotonicityLeftRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntVerifyMonotonicityLeftRegion( id, pDim, pnpts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps, id = 0):
    """LipIntVerifyMonotonicityRightRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntVerifyMonotonicityRightRegion( id, pDim, pnpts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntInfValue( Dim, Ndata, x, Xd, y, Lipconst, Index, id = 0):
    """LipIntInfValue

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValue( id, pDim, pNdata, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)
def LipIntInfValueAuto(Dim, Ndata, x, Xd, y, Index, id = 0):
    """LipIntInfValueAuto

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueAuto( id, pDim, pNdata, px, pXd, py, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double Lipconst, int* Index)
def LipIntInfValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index, id = 0):
    """LipIntInfValueCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double *Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    yy = fm.LipIntInfValueCons( id, pDim, pNdata, pCons, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntInfValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index, id = 0):
    """LipIntInfValueConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueConsLeftRegion( id, pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntInfValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index, id = 0):
    """LipIntInfValueConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueConsRightRegion( id, pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
def LipIntInfValueLocal(Dim, Ndata, x, Xd, y, id = 0):
    """LipIntInfValueLocal

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntInfValueLocal( id, pDim, pNdata, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
def LipIntInfValueLocalCons(Dim, Ndata, Cons, x, Xd, y, id = 0):
    """LipIntInfValueLocalCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntInfValueLocalCons( id, pDim, pNdata, pCons, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntInfValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region, id = 0):
    """LipIntInfValueLocalConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntInfValueLocalConsLeftRegion( id, pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntInfValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region, id = 0):
    """LipIntInfValueLocalConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntInfValueLocalConsRightRegion( id, pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntInfComputeLipschitz(Dim, Ndata, x, y, id = 0):
    """LipIntInfComputeLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    print( "Id: ", id)
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntInfComputeLipschitz( id, pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntInfComputeLocalLipschitz(Dim, Ndata, x, y, id = 0):
    """LipIntInfComputeLocalLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntInfComputeLocalLipschitz( id, pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
def LipIntInfComputeLipschitzCV(Dim, Ndata, Xd, y, type, Cons, Region, W, id = 0):
    """LipIntInfComputeLipschitzCV

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    T = [0.0] * Ndata
    pTnp, pT = convert_py_float_to_cffi( T)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntInfComputeLipschitzCV( id, pDim, pNdata, pXd, py, pT, ptype, pCons, pRegion, pW)
    return pTnp


# Python wrapper for:
#    void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W)
def LipIntInfComputeLipschitzSplit(Dim, Ndata, Xd, y, ratio, type, Cons, Region, W, id = 0):
    """LipIntInfComputeLipschitzSplit

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        ratio (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    T = [0.0] * Ndata
    pTnp, pT = convert_py_float_to_cffi( T)
    prationp, pratio = convert_py_float_to_cffi( ratio)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntInfComputeLipschitzSplit( id, pDim, pNdata, pXd, py, pT, pratio, ptype, pCons, pRegion, pW)
    return pTnp


# Python wrapper for:
#    void LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
def LipIntInfSmoothLipschitz(Dim, Ndata, Xd, y, LC, fW, fC, fR, W, Cons, Region, id = 0):
    """LipIntInfSmoothLipschitz

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        LC (float):
        fW (int):
        fC (int):
        fR (int):
        W (float):
        Cons (int):
        Region (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    T = [0.0] * Ndata 
    pTnp, pT = convert_py_float_to_cffi( T)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pfWnp, pfW = convert_py_int_to_cffi( fW)
    pfCnp, pfC = convert_py_int_to_cffi( fC)
    pfRnp, pfR = convert_py_int_to_cffi( fR)
    pWnp, pW = convert_py_float_to_cffi( W)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    fm.LipIntInfSmoothLipschitz( id, pDim, pNdata, pXd, py, pT, pLC, pfW, pfC, pfR, pW, pCons, pRegion)
    return pTnp


# Python wrapper for:
#    double	LipIntInfGetLipConst() 
def LipIntInfGetLipConst( id = 0):
    """LipIntInfGetLipConst

    Args:

    Returns:
        (double):
    """
    trace( "double	LipIntInfGetLipConst() ")
    yy = fm.LipIntInfGetLipConst( id)
    return yy


# Python wrapper for:
#    void	LipIntInfGetScaling(double *S) 
def LipIntInfGetScaling( dim, id = 0):
    """LipIntInfGetScaling

    Args:
        S (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfGetScaling(double *S) ")
    S = [0.0] * dim
    pSnp, pS = convert_py_float_to_cffi( S)
    fm.LipIntInfGetScaling( id, pS)
    return pSnp


# Python wrapper for:
#    int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
def LipIntInfComputeScaling(Dim, Ndata, XData, YData, id = 0):
    """LipIntInfComputeScaling

    Args:
        Dim (int):
        Ndata (int):
        XData (float):
        YData (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    yy = fm.LipIntInfComputeScaling( id, pDim, pNdata, pXData, pYData)
    return yy


# Python wrapper for:
#    int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep)
def LipIntInfVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, ep, id = 0):
    """LipIntInfVerifyMonotonicity

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        LC (float):
        ep (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    yy = fm.LipIntInfVerifyMonotonicity( id, pDim, pnpts, pCons, pXData, pYData, LC, ep)
    return yy


# Python wrapper for:
#    int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntInfVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps, id = 0):
    """LipIntInfVerifyMonotonicityLeftRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int *npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntInfVerifyMonotonicityLeftRegion( id, pDim, pnpts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int *npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntInfVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps, id = 0):
    """LipIntInfVerifyMonotonicityRightRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntInfVerifyMonotonicityRightRegion( id, pDim, pnpts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)
def LipIntInfSmoothLipschitzSimp(Dim, npts, XData, YData, LC, id = 0):
    """LipIntInfSmoothLipschitzSimp

    Args:
        Dim (int):
        npts (int):
        XData (float):
        YData (float):
        TData (float):
        LC (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    TData = [0.0] * npts
    pTDatanp, pTData = convert_py_float_to_cffi( TData)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    fm.LipIntInfSmoothLipschitzSimp( id, pDim, pnpts, pXData, pYData, pTData, pLC)
    return pTDatanp


# Python wrapper for:
#    void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W)
def LipIntInfSmoothLipschitzSimpW(Dim, npts, XData, YData, LC, W, id = 0):
    """LipIntInfSmoothLipschitzSimpW

    Args:
        Dim (int):
        npts (int):
        XData (float):
        YData (float):
        TData (float):
        LC (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    TData = [0.0] * npts
    pTDatanp, pTData = convert_py_float_to_cffi( TData)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntInfSmoothLipschitzSimpW( id, pDim, pnpts, pXData, pYData, pTData, pLC, pW)
    return pTDatanp


# Python wrapper for:
#    int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolantExplicit(Dim, Ndata, x, y, id = 0):
    """STCBuildLipInterpolantExplicit

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        (int):
    """
    trace( "int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.STCBuildLipInterpolantExplicit( id, pDim, pNdata, px, py)
    return yy


# Python wrapper for:
#    int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolantColumn(Dim, Ndata, x, y, id = 0):
    """STCBuildLipInterpolantColumn

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        (int):
    """
    trace( "int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.STCBuildLipInterpolantColumn( id, pDim, pNdata, px, py)
    return yy


# Python wrapper for:
#    int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolantExplicitColumn(Dim, Ndata, x, y, id = 0):
    """STCBuildLipInterpolantExplicitColumn

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        (int):
    """
    trace( "int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.STCBuildLipInterpolantExplicitColumn( id, pDim, pNdata, px, py)
    return yy


# Python wrapper for:
#    double	STCValueExplicit( double* x )
def STCValueExplicit(x, id = 0):
    """STCValueExplicit

    Args:
        x (float):

    Returns:
        (double):
    """
    trace( "double	STCValueExplicit( double* x )")
    pxnp, px = convert_py_float_to_cffi( x)
    yy = fm.STCValueExplicit( id, px)
    return yy


# Python wrapper for:
#    void	STCFreeMemory()
def STCFreeMemory( id = 0):
    """STCFreeMemory

    Args:

    Returns:
        <none>
    """
    trace( "void	STCFreeMemory()")
    fm.STCFreeMemory( id)
    return 

###
# wrapper for additional functions
###

# Python wrapper for:
#    void LipIntConstruct()
def LipIntConstruct( id = 0):
    """LipIntConstruct

    Args:

    Returns:
        <none>
    """
    trace( "void LipIntConstruct()")
    fm.LipIntConstruct( id)
    return 


# Python wrapper for:
#    double LipIntDetermineLipschitz()
def LipIntDetermineLipschitz( id = 0):
    """LipIntDetermineLipschitz

    Args:

    Returns:
        (double):
    """
    trace( "double LipIntDetermineLipschitz()")
    yy = fm.LipIntDetermineLipschitz( id)
    return yy


# Python wrapper for:
#    void LipIntFreeMemory()
def LipIntFreeMemory( id = 0):
    """LipIntFreeMemory

    Args:

    Returns:
        <none>
    """
    trace( "void LipIntFreeMemory()")
    fm.LipIntFreeMemory( id)
    return 


# Python wrapper for:
#    void LipIntSetConstants()
def LipIntSetConstants( id = 0):
    """LipIntSetConstants

    Args:

    Returns:
        <none>
    """
    trace( "void LipIntSetConstants()")
    fm.LipIntSetConstants( id)
    return 


# Python wrapper for:
#    double LipIntValueExplicitDim( int dim, double* x)
def LipIntValueExplicitDim( dim, x, id = 0):
    """LipIntValueExplicitDim

    Args:
        dim (int):
        x (float):

    Returns:
        (double):
    """
    trace( "double LipIntValueExplicitDim( int dim, double* x)")
    pxnp, px = convert_py_float_to_cffi( x)
    yy = fm.LipIntValueExplicitDim( id, dim, px)
    return yy


# Python wrapper for:
#    double LipIntValueDim( int dim, double* x)
def LipIntValueDim( dim, x, id = 0):
    """LipIntValueDim

    Args:
        dim (int):
        x (float):

    Returns:
        (double):
    """
    trace( "double LipIntValueDim( int dim, double* x)")
    pxnp, px = convert_py_float_to_cffi( x)
    yy = fm.LipIntValueDim( id, dim, px)
    return yy


# Python wrapper for:
#    void LipIntSetData( int dim, int K, double* x, double* y, int test)
def LipIntSetData( dim, K, x, y, test, id = 0):
    """LipIntSetData

    Args:
        dim (int):
        K (int):
        x (float):
        y (float):
        test (int):

    Returns:
        <none>
    """
    trace( "void LipIntSetData( int dim, int K, double* x, double* y, int test)")
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntSetData( id, dim, K, px, py, test)
    return 

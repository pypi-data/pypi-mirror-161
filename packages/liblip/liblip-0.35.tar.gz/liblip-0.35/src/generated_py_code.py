# Python wrapper for:
#    void LipIntConstruct()
def LipIntConstruct():
    """LipIntConstruct

    Args:

    Returns:
        <none>
    """
    trace( "void LipIntConstruct()")
    fm.LipIntConstruct( )
    return 


# Python wrapper for:
#    double LipIntDetermineLipschitz()
def LipIntDetermineLipschitz():
    """LipIntDetermineLipschitz

    Args:

    Returns:
        (double):
    """
    trace( "double LipIntDetermineLipschitz()")
    yy = fm.LipIntDetermineLipschitz( )
    return yy


# Python wrapper for:
#    void LipIntFreeMemory()
def LipIntFreeMemory():
    """LipIntFreeMemory

    Args:

    Returns:
        <none>
    """
    trace( "void LipIntFreeMemory()")
    fm.LipIntFreeMemory( )
    return 


# Python wrapper for:
#    void LipIntSetConstants()
def LipIntSetConstants():
    """LipIntSetConstants

    Args:

    Returns:
        <none>
    """
    trace( "void LipIntSetConstants()")
    fm.LipIntSetConstants( )
    return 


# Python wrapper for:
#    double LipIntValueExplicitDim( int dim, double* x)
def LipIntValueExplicitDim(dim, x):
    """LipIntValueExplicitDim

    Args:
        dim (int):
        x (float):

    Returns:
        (double):
    """
    trace( "double LipIntValueExplicitDim( int dim, double* x)")
    pxnp, px = convert_py_float_to_cffi( x)
    yy = fm.LipIntValueExplicitDim( dim, px)
    return yy


# Python wrapper for:
#    double LipIntValueShort( int dim, double* x)
def LipIntValueShort(dim, x):
    """LipIntValueShort

    Args:
        dim (int):
        x (float):

    Returns:
        (double):
    """
    trace( "double LipIntValueShort( int dim, double* x)")
    pxnp, px = convert_py_float_to_cffi( x)
    yy = fm.LipIntValueShort( dim, px)
    return yy


# Python wrapper for:
#    void LipIntSetData( int dim, int K, double* x, double* y, int test)
def LipIntSetData(dim, K, x, y, test):
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
    fm.LipIntSetData( dim, K, px, py, test)
    return 


# Test wrapper for:
#    void LipIntConstruct()
# ll.LipIntConstruct()


# Test wrapper for:
#    double LipIntDetermineLipschitz()
# ll.LipIntDetermineLipschitz()


# Test wrapper for:
#    void LipIntFreeMemory()
# ll.LipIntFreeMemory()


# Test wrapper for:
#    void LipIntSetConstants()
# ll.LipIntSetConstants()


# Test wrapper for:
#    double LipIntValueExplicitDim( int dim, double* x)
# ll.LipIntValueExplicitDim(dim, x)


# Test wrapper for:
#    double LipIntValueShort( int dim, double* x)
# ll.LipIntValueShort(dim, x)


# Test wrapper for:
#    void LipIntSetData( int dim, int K, double* x, double* y, int test)
# ll.LipIntSetData(dim, K, x, y, test)



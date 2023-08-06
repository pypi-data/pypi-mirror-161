/**************************************************************************
Procedural intervace to the methods of Lipschitz interpolant classes
 ***************************************************************************/
#pragma once
//#ifdef __cplusplus
//extern "C" {
//#endif

//#define NULL 0
#define LIBEXP extern

/* interface to the members of SLipInt class ===================== */
LIBEXP double	LipIntValue( int id, int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index);
LIBEXP double	LipIntValueAuto( int id, int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index);
LIBEXP double	LipIntValueCons( int id, int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index);
LIBEXP double	LipIntValueConsLeftRegion( int id, int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
LIBEXP double	LipIntValueConsRightRegion( int id, int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
LIBEXP double	LipIntValueLocal( int id, int *Dim, int *Ndata, double* x, double* Xd,double* y);
LIBEXP double	LipIntValueLocalCons( int id, int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);
LIBEXP double	LipIntValueLocalConsLeftRegion( int id, int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
LIBEXP double	LipIntValueLocalConsRightRegion( int id, int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
LIBEXP  void	LipIntComputeLipschitz( int id, int *Dim, int *Ndata, double* x, double* y);
LIBEXP  void 	LipIntComputeLocalLipschitz( int id, int *Dim, int *Ndata, double* x, double* y);
LIBEXP  void	LipIntComputeLipschitzCV( int id, int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
LIBEXP  void	LipIntComputeLipschitzSplit( int id, int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W);
LIBEXP void	LipIntSmoothLipschitz( int id, int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
 // fR is 0, 1-left, 2-right
LIBEXP double	LipIntGetLipConst( int id) ;
LIBEXP void		LipIntGetScaling( int id, double *S) ;
LIBEXP int		LipIntComputeScaling( int id, int *Dim, int *Ndata, double* XData, double* YData);
LIBEXP void	ConvertXData( int id, int *Dim, int* npts,  double* XData);
LIBEXP void	ConvertXDataAUX( int id, int *Dim, int* npts,  double* XData, double *auxdata);
LIBEXP int		LipIntVerifyMonotonicity( int id, int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps);
LIBEXP int		LipIntVerifyMonotonicityLeftRegion( int id, int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
LIBEXP int		LipIntVerifyMonotonicityRightRegion( int id, int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);

/* interface to the members of SLipIntInf class ====================================== */
LIBEXP double	LipIntInfValue( int id, int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index);
LIBEXP double	LipIntInfValueAuto( int id, int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index);
LIBEXP double	LipIntInfValueCons( int id, int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double *LipIntInfVerifyMonotonicityLeftRegionLipconst, int* Index);
LIBEXP double	LipIntInfValueConsLeftRegion( int id, int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
LIBEXP double	LipIntInfValueConsRightRegion( int id, int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
LIBEXP double	LipIntInfValueLocal( int id, int *Dim, int *Ndata, double* x, double* Xd,double* y);
LIBEXP double	LipIntInfValueLocalCons( int id, int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);
LIBEXP double	LipIntInfValueLocalConsLeftRegion( int id, int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
LIBEXP double	LipIntInfValueLocalConsRightRegion( int id, int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
LIBEXP void	LipIntInfComputeLipschitz( int id, int *Dim, int *Ndata, double* x, double* y);
LIBEXP void	LipIntInfComputeLocalLipschitz( int id, int *Dim, int *Ndata, double* x, double* y);
LIBEXP void	LipIntInfComputeLipschitzCV( int id, int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
LIBEXP void	LipIntInfComputeLipschitzSplit( int id, int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W);
LIBEXP void	LipIntInfSmoothLipschitz( int id, int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
 // fR is 0, 1-left, 2-right
LIBEXP double	LipIntInfGetLipConst( int id) ;
LIBEXP void	LipIntInfGetScaling( int id, double *S) ;
LIBEXP int		LipIntInfComputeScaling( int id, int *Dim, int *Ndata, double* XData, double* YData);
LIBEXP int		LipIntInfVerifyMonotonicity( int id, int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep);
LIBEXP int		LipIntInfVerifyMonotonicityLeftRegion( int id, int *Dim, int *npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
LIBEXP int		LipIntInfVerifyMonotonicityRightRegion( int id, int *Dim, int *npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
LIBEXP void	LipIntInfSmoothLipschitzSimp( int id, int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC);
LIBEXP void	LipIntInfSmoothLipschitzSimpW( int id, int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W);

/* interface to the members of STCInterpolant class ====================================== */
// supplies the data to Interpolant and constructs the interpolant
// assuming a given Lipschitz constant, supplied by SetLipschitz
// if LipConstant was not supplied, tries to find it from the data
// assumes that all data are different. 
LIBEXP int	STCBuildLipInterpolant( int id, int *Dim, int *Ndata, double* x, double* y);
// as above, but for explicit evaluation, needs no preprocessing, but may be slower
LIBEXP int	STCBuildLipInterpolantExplicit( int id, int *Dim, int *Ndata, double* x, double* y);
// in the methods above, the coordinates of the data points in x are stored in rows
// the following methods store data in columns (like in fortran or Matlab)
// they use the transposed of the matrix x 
LIBEXP  int	STCBuildLipInterpolantColumn( int id, int *Dim, int *Ndata, double* x, double* y);
// as above, but for explicit evaluation, needs no preprocessing, but may be slower
LIBEXP  int	STCBuildLipInterpolantExplicitColumn( int id, int *Dim, int *Ndata, double* x, double* y);
// specify the Lipschitz constant for your function
LIBEXP void	STCSetLipschitz( int id, double* x);
// computes the value of the interpolant at any given point x
LIBEXP  double	STCValue( int id, double* x );
// same but using explicit evaluation with no preprocessing
LIBEXP  double	STCValueExplicit( int id, double* x );
LIBEXP void	STCFreeMemory( int id);
// additional functions
LIBEXP void LipIntConstruct( int id);
LIBEXP double LipIntDetermineLipschitz( int id);
LIBEXP void LipIntFreeMemory( int id);
LIBEXP void LipIntSetConstants( int id);
LIBEXP double LipIntValueExplicitDim( int id, int dim, double* x);
LIBEXP double LipIntValueDim( int id, int dim, double* x);
LIBEXP void LipIntSetData( int id, int dim, int K, double* x, double* y, int test);
LIBEXP int	STCInterpolantInit();
LIBEXP void	STCInterpolantDel( int id);
LIBEXP int SLipIntInit();
LIBEXP void SLipIntDel( int id);
LIBEXP int SLipIntInfInit();
LIBEXP void SLipIntInfDel( int id);
LIBEXP int SLipIntLpInit();
LIBEXP void SLipIntLpDel( int id);
// #ifdef __cplusplus
// }
// #endif

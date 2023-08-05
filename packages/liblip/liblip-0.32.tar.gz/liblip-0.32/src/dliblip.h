
// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the LIPDLL_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// LIPDLL_API functions as being imported from a DLL, wheras this DLL sees symbols
// defined with this macro as being exported.
#ifdef LIBLIP2_EXPORTS
#define DLIBLIP_EXPORTS
#endif
#ifdef DLIBLIP_EXPORTS
#define LIPDLL_API __declspec(dllexport)
#else
#define LIPDLL_API __declspec(dllimport)
#endif

#define MATH_UTILS_H

/**************************************************************************

 ***************************************************************************/

#if !defined(LIPNTERPOLANT)
#define LIPNTERPOLANT

#include <cstdlib>
#include <cmath>


#define DUAL

//#define LPSOLVE
#ifdef LPSOLVE
#include "../lp_solve/lp_lib.h"
#else
extern "C" {
//#include <glpk.h>
#include "glpk/include/glpk.h"
}
#endif

struct LPX;
#define SLIPINTERPOL1


class LIPDLL_API SLipIntBasic {
public:
	double*   LipConst, MaxLipConst;  // an array of Lipschitz constants and the largest Lipschitz constant
// computed automatically in ComputeLipschitz

	int		*neighbors, *pneighbors;

	float	*GridR, *GridVal;
	int	*GridLim;

	double* Scaling;
	int	UseOtherBounds;

// diagnistics
	int		m_lasterror;
	int		m_number_constraints; 
	double  m_minvalue; 

	double OptimalPenalty;


	SLipIntBasic() {
		LipConst=0;
		MaxLipConst=0;
		Dim=0;
		NPTS=0;
		Scaling=0;
		m_lasterror=0;
		KeepCVProblem=0;
		UseOtherBounds=0;

		Indexsize=IndexsizeComp=ND=0;
		Index=NULL; IndexComp=NULL;
		LocalXData=LocalYData=LocalTData=YH=NULL; // pointers
		type=0;
		LocalCons=NULL;
		LocalRegion=NULL; LocalW=NULL;
		pneighbors=neighbors=NULL;

		GridR=GridVal=NULL;
		GridLim=NULL;
	}

	~SLipIntBasic() { 
		free(LipConst); 
		if(Scaling!=NULL) free(Scaling);
		if(pneighbors!=NULL) free(pneighbors);
		if(neighbors!=NULL) free(neighbors);
		if(GridR!=NULL) free(GridR);
		if(GridVal!=NULL) free(GridVal);
		if(GridLim!=NULL) free(GridLim);
	}

//************* MUST be implemented in the derived class ***********
// Computes the smallest Lipschitz constant, compatible with the data
	virtual	void	ComputeLipschitz(int dim, int npts, double* XData, double* YData)=0;

	virtual double dist(int dim,  double* x, double* xk, double* param=NULL) {return 0;};
	virtual double dist(int dim,  double* x, double* xk, int* Cons, double* param=NULL){return 0;}; // constrained
	virtual double distLeftRegion(int dim,  double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL){return 0;};
	virtual double distRightRegion(int dim,  double* x, double* xk, int* Cons, double* RightRegion, double* param=NULL){return 0;};
	virtual double distAll(int dim,  int type, double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL) {return 0;};
//************* MUST be implemented in the derived class ***********


// entry points
// type: 0 - usual interpolation, 1-constrained, 2- constrained Left , 3 - constrained right region
	void	ComputeLipschitzSplit(int dim, int npts, double* XData, double* YData, double* TData,  double ratio=0.5,
			int type=0, int* Cons=NULL, double* Region=NULL, double *W=NULL);

	void	ComputeLipschitzCV(int dim, int npts, double* XData, double* YData, double* TData, 
			int type=0, int* Cons=NULL, double* Region=NULL, double *W=NULL);

// Computes the local Lipschitz constants in any norm, compatible with the data
	void	ComputeLocalLipschitz(int dim, int npts, double* XData, double* YData);
	void	ComputeLocalLipschitzCons(int dim, int npts, int _type, int* Cons, double* XData, double* YData, double* Region=NULL);



// Returns the value of the interpolant 
	double	Value(int dim, int npts,   double* x, double* XData, double* YData,   double LipConst, int* index=NULL);

// Returns the value of the interpolant, with the Lipschitz constant
// computed from the data. Can be used after ComputeLipschitz
	double	Value(int dim, int npts,   double* x, double* XData, double* YData, int* index=NULL);

// Returns the value of the interpolant, with the local Lipschitz constants
// computed from the data. Can be used after ComputeLocalLipschitz
	double	ValueLocal(int dim, int npts,   double* x, double* XData, double* YData);

	int	FindVoronoi(int dim, int npts,   double* x, double* XData, double &d);

	int	ComputeScaling(int dim, int npts, double* XData, double* YData);

// *** methods below refer to Monotone interpolation **

// returns 1 if x >> y wrt Cons
	int		Dominates(int dim, double* x, double * y, int* Cons);

// Returns the value of the monotone interpolant 
	double	ValueCons(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   double LipConst, int* index=NULL);

// Returns the value of the monotone interpolant, with the Lipschitz constant
// computed from the data. Can be used after ComputeLipschitz
	double	ValueCons(int dim, int npts, int* Cons,  double* x, double* XData, double* YData);

// Returns the value of the interpolant , assuming it is monotone for x<< LeftRegion
	double	ValueConsLeftRegion(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   
													  double LipConst, double* LeftRegion, int* index=NULL);
// Returns the value of the interpolant in l_2 norm,  assuming it is monotone for x>> RightRegion
	double	ValueConsRightRegion(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   
													  double LipConst, double* RightRegion, int* index=NULL);


// Returns the value of the monotone interpolant, with the local Lipschitz constants
// computed from the data. Can be used after ComputeLocalLipschitz
	double	ValueLocalCons(int dim, int npts, int* Cons, double* x, double* XData, double* YData);
// same but monotonicity is for x<< LeftRegion or x>>RightRegion
	double	ValueLocalConsLeftRegion(int dim, int npts, int* Cons,  double* x, double* XData, double* YData, double* Region);
	double	ValueLocalConsRightRegion(int dim, int npts, int* Cons,  double* x, double* XData, double* YData, double* Region);

// Verifies the data is monotone wrt specified variables
	int		VerifyMonotonicity(int dim, int npts, int* Cons,  double* XData, double* YData, double LC=10e20, double eps=1e-7);

// Verifies the data is monotone wrt specified variables in the region On x<< LeftBoundary 
	int		VerifyMonotonicityLeftRegion (int dim, int npts, int* Cons,  double* XData, double* YData, 
															 double* LeftRegion, double LC=10e20,double eps=1e-7);
// Verifies the data is monotone wrt specified variables in the region On x >> Rightboundary 
	int		VerifyMonotonicityRightRegion (int dim, int npts, int* Cons,  double* XData, double* YData, 
															  double* RightRegion, double LC=10e20,double eps=1e-7);

// the working horses
	double	ValueLocal2Consinternal(int dim, int npts, int* Cons,  double* x, double* XData, double* YData, int reg, double* Region);

	void	SmoothLipschitz2internal(int dim, int npts,  double* XData, double* YData, double* TData, int LCf, int Wf,int Cf,
											double* LC, double* W, int* Cons, int region=0, double* Region=NULL, int* index=NULL);
	void	SmoothLipschitz2internalUpdate(int dim, int npts,  double* XData, double* YData, double* TData, int LCf, int Wf,int Cf,
											double* LC, double* W, int* Cons, int region=0, double* Region=NULL, int* index=NULL);



// Assumes the data in XData are stored columnwise, as in Fortran.
// Used for compatibility of this library with other packages, e.g.,Matlab, R, which
// may use column format. 
	void	ConvertXData(int dim, int npts,  double* XData);
	void	ConvertXData(int dim, int npts,  double* XData, double* auxStorage);


// implement the methods for sample splitting and CV. used internally
	virtual int		ComputeSmoothenedSplit();
	virtual int		ComputeLipschitzFinal();
	virtual int		ComputeFitLipschitzCV(int excluded);

	virtual double  ExtraUpperBound(int dim, double* x, double * param) {return 10e20;};  // derived classes may overwrite these
	virtual double  ExtraLowerBound(int dim, double* x, double * param) {return -10e20;};

	virtual double	Fun(double x); // for golden section algorithm
	double MinFuncSplit(double x);
	double MinFuncCV(double x);
	double MinFuncLocalSplit(double x);

	virtual double value(int dim, int npts,   double* x, double* XData, double* YData,   double LipConst, int* index=NULL,
		 int type=0, int* Cons=NULL, double* Region=NULL	);
// various parameters
// interpretation depends on the derived class. In this class:
// type: 0 - usual interpolation, 1-constrained, 2- constrained Left , 3 - constrained right region
	double valuelocal(int dim, int npts,   double* x, double* XData, double* YData, int type, int* Cons, double* Region);


// called internally
	double	ComputeFitIndexCV();
	double	ComputeFitIndex();
	void	PrepareLipschitzSplit(double SplitP);
	void	PrepareLipschitzCV();
	double	golden(double A, double B); 

	int BinSearch(double r, float* Arr, int le, int ri);

//these are private, but need to be inherited, so declared as public
	double	M; // temp value of the LipConst
	double g1,g2,d1,d2,d3;
	int i,j,i1;
	int Dim,NPTS; 
	int	TotalNeighbors;

// these vars are for the cross-validation/ sample splitting
	int		Indexsize,IndexsizeComp,ND;
	int		*Index, *IndexComp;
	double	*LocalXData, *LocalYData, *LocalTData; // pointers
	double  *YH;
// parameters to be passed to value() method and other CV and splitting routines
	int		type;
	int		*LocalCons;
	double	*LocalRegion, *LocalW;
	double  *AuxXData; 

	int		TypeLipEstimate; //0 sample splitting, 1 CV
	int		KeepCVProblem;

//	double Gamma;

#ifdef LPSOLVE
	lprec		*MyLP; 
#else
	LPX			*MyLP; 
#endif

};


class LIPDLL_API SLipInt:public SLipIntBasic {
public:

// In the methods below, XData contain the abscissae of data points x^k (arranged
// in rows (C-convention)) and YData contain y^k. x is the point at which g(x) is needed.

// Computes the smallest Lipschitz constant in l_2 norm, compatible with the data
	virtual void	ComputeLipschitz(int dim, int npts, double* XData, double* YData);



// Methods below refer to Lipschitz smoothing **************************

// Smooth the data subject to given Lipschitz constant in Euclidean norm
	void	SmoothLipschitz(int dim, int npts,  double* XData, double* YData, double* TData, double LC);
// Smooth the data subject to given Lipschitz constant in Euclidean norm, subject to weightings
	void	SmoothLipschitzW(int dim, int npts,  double* XData, double* YData, double* TData, double LC, double* W);


// same, subject to monotonicity constraints
	void	SmoothLipschitzCons(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double LC);
	void	SmoothLipschitzWCons(int dim, int npts,  int* Cons, double* XData, double* YData, double* TData, double LC, double* W);
	void	SmoothLipschitzConsLeftRegion(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double LC, double* LeftRegion);
	void	SmoothLipschitzConsRightRegion(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double LC, double* RightRegion);
	void	SmoothLipschitzWConsLeftRegion(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double LC, double* W, double* LeftRegion);
	void	SmoothLipschitzWConsRightRegion(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double LC, double* W, double* RightRegion);



	virtual double dist(int dim,  double* x, double* xk, double* param=NULL);
	virtual double dist(int dim,  double* x, double* xk, int* Cons, double* param=NULL); // constrained
	virtual double distLeftRegion(int dim,  double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL);
	virtual double distRightRegion(int dim,  double* x, double* xk, int* Cons, double* RightRegion, double* param=NULL);
	virtual double distInf1(int dim,  double* x, double* xk, int* dir);
	virtual double distAll(int dim,  int type, double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL);

private:


// Computes the smallest Lipschitz constant in l_inf norm, compatible with the data, used internally for scaling
	void	ComputeLipschitzInf(int dim, int npts, double* XData, double* YData);
};



// Same as SLipInt, but uses l_infty rather than Euclidean norm


class LIPDLL_API SLipIntInf:public SLipIntBasic {
public:

// In the methods below, XData contain the abscissae of data points x^k (arranged
// in rows (C-convention)) and YData contain y^k. x is the point at which g(x) is needed.

// Computes the smallest Lipschitz constant in l_inf norm, compatible with the data
	virtual void	ComputeLipschitz(int dim, int npts, double* XData, double* YData);


// Same, but uses an array of Lipschitz constants wrt each variable
	double	ValueDir(int dim, int npts, double* x, double* XData, double* YData,   double* LipConst, int* index=NULL);

// Returns the value of the interpolant, with the Lipschitz constant
// computed from the data. Can be used after ComputeLipschitz
	double	ValueDir(int dim, int npts, double* x, double* XData, double* YData);


// Returns the value of the interpolant , with the Lipschitz constant
// computed from the data. Can be used after ComputeLipschitz
	double	ValueConsDir(int dim, int npts, int* Cons, double* x, double* XData, double* YData);



// Methods below refer to Lipschitz smoothing

// Smooth the data subject to given Lipschitz constant in l-infy norm
	void	SmoothLipschitz(int dim, int npts,  double* XData, double* YData, double* TData, double LC);
// Smooth the data subject to given Lipschitz constant in l-infy norm, subject to weightings
	void	SmoothLipschitzW(int dim, int npts,  double* XData, double* YData, double* TData, double LC, double* W);

// same, subject to monotonicity constraints
	void	SmoothLipschitzCons(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double LC);
	void	SmoothLipschitzWCons(int dim, int npts,  int* Cons, double* XData, double* YData, double* TData, double LC, double* W);


// Same in simplicial distance
	void	SmoothLipschitzSimp(int dim, int npts,  double* XData, double* YData, double* TData, double LC);
// Same in simplicial distance, subject to weightings
	void	SmoothLipschitzSimpW(int dim, int npts,  double* XData, double* YData, double* TData, double LC, double* W);

	virtual double dist(int dim,  double* x, double* xk, double* param=NULL);
	virtual double dist(int dim,  double* x, double* xk, int* Cons, double* param=NULL); // constrained
	virtual double distLeftRegion(int dim,  double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL);
	virtual double distRightRegion(int dim,  double* x, double* xk, int* Cons, double* RightRegion, double* param=NULL);

	virtual double distDir(int dim, double* x, double* xk, int* dir); // if we need the direction (just the coord)
	virtual double distInfDir(int dim,  double* x, double* xk, int* dir); // if we need the direction + left/right

	virtual double distSimp(int dim,  double* x, double* xk, int* dir);
	virtual double distAll(int dim,  int type, double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL);


	virtual int		ComputeSmoothenedSplit();
	virtual int		ComputeLipschitzFinal();
	virtual int		ComputeFitLipschitzCV(int excluded);

private:
// the working horses
	void	SmoothLipschitzInfinternal(int dim, int npts,  double* XData, double* YData, double* TData, int LCf, int Wf,
											double* LC, double* W, int* index=NULL);
	void	SmoothLipschitzSimpinternal(int dim, int npts,  double* XData, double* YData, double* TData,  int Wf,
											 double LC, double* W, int* index=NULL);
};



class LIPDLL_API SLipIntLp:public SLipInt {
public:
	double m_P, m_P1;

	SLipIntLp(): SLipInt() { m_P=m_P1=1;}

	void      SetP(double p) {m_P=p; if(m_P<= 1.001) m_P=1.0; m_P1=1.0/m_P; };
	double    GetP() {return m_P;};

	virtual double dist(int dim,  double* x, double* xk, double* param=NULL);
	virtual double dist(int dim,  double* x, double* xk, int* Cons, double* param=NULL); // constrained
	virtual double distLeftRegion(int dim,  double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL);
	virtual double distRightRegion(int dim,  double* x, double* xk, int* Cons, double* RightRegion, double* param=NULL);
	virtual double distAll(int dim,  int type, double* x, double* xk, int* Cons, double* LeftRegion, double* param=NULL);

};




// not documented
// a classifier based on Lipschitz interpolation
class LIPDLL_API SLipClass: public SLipInt {

public:
	double	Penalty, SmoothingParam;

	SLipClass(): SLipInt() {
		SmoothingParam=0;
		Penalty=1;
	}
	
	// Returns the value of the Classifier 
	int		ValueClass(int dim, int npts, double* x, double* XData, double* YData,   double LipConst);
	int		ValueConsClass(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   double LipConst);
	int		ValueConsLeftRegionClass(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   
													  double LipConst, double* LeftRegion);
	int		ValueConsRightRegionClass(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   
													  double LipConst, double* RightRegion);

	int		ValueLocalClass(int dim, int npts, double* x, double* XData, double* YData);
	int		ValueLocalConsClass(int dim, int npts,  int* Cons, double* x, double* XData, double* YData);
	int		ValueLocalConsLeftRegionClass(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   
													   double* LeftRegion);
	int		ValueLocalConsRightRegionClass(int dim, int npts,  int* Cons, double* x, double* XData, double* YData,   
													  double* RightRegion);

// performs large margin classifier smoothing of the data
	void	SmoothLipschitzClass(int dim, int npts,  double* XData, double* YData, double* TData, double *LC);
	void	SmoothLipschitzWClass(int dim, int npts,  double* XData, double* YData, double* TData, double *LC, double* W);
	void	SmoothLipschitzConsClass(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double *LC);
	void	SmoothLipschitzWConsClass(int dim, int npts,  int* Cons, double* XData, double* YData, double* TData, double *LC, double* W);
	void	SmoothLipschitzConsLeftRegionClass(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double *LC, double* LeftRegion);
	void	SmoothLipschitzConsRightRegionClass(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double *LC, double* RightRegion);
	void	SmoothLipschitzWConsLeftRegionClass(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double *LC, double* W, double* LeftRegion);
	void	SmoothLipschitzWConsRightRegionClass(int dim, int npts, int* Cons, double* XData, double* YData, double* TData,  double *LC, double* W, double* RightRegion);

// the working horse
	void	SmoothLipschitz2Classinternal(int dim, int npts,  double* XData, double* YData, double* TData, int LCf, int Wf,int Cf,
											double* LC, double* W, int* Cons, int region=0, double* Region=NULL, int* index=NULL);


};





#if !defined(STCINTERPOLANT)
#define STCINTERPOLANT

/*******************************************************************
	Class STCInterpolant

	Computes the value of the piecewise linear interpolant to the 
	multivariate scattered data using 2 methods:
	1) fast method requiring preprocessing
	2) slower direct method (no preprocessing)

********************************************************************/

/* Interpolant is a worker class, and is not part of API */
class Interpolant;




class LIPDLL_API STCInterpolant {

public:
	int				Dim;				// dimension +1 (slack variable)

private:
	Interpolant		*m_lower, *m_upper;	// the upper and lower interpolants

	double			LipschitzConst;		// LipschitzConstant of the function
	double			Lo,Up;				// lower and upper interpolant values
	int				m_lasterr;
	double			*aux, *Lip1, *Lip2;		// to compute Lipschitz constant of the data set
	double			*m_Constants;		// here Lipschitz constants live

public:
	STCInterpolant();  // creates instances of m_lower and m_upper
	~STCInterpolant(); // deletes instances of m_lower and m_upper

// to set the Lipschitz constant of the function
	void	SetConstants(double newconst);			
	void	SetConstants();							// use computed lipschitz constants
	void	SetConstants(double newconst, int dim); // internal routine

// received the data set of dimension dim, of K data points
// test indicates the necessity to test whether all data are different (may be slow)
	void	SetData(int dim, int K, double* x, double* y, int test=0);

// the same as above, but uses fortran conventions for storing matrices (in columns)
	void	SetDataColumn(int dim, int K, double* x, double* y, int test=0);

// compute from the data set (KxKxdim operations)
	double	DetermineLipschitz();

// construct the interpolant (for small dimension <6)
	void	Construct();

// does not create the tree of local minima, just preproceses support vectors for
// subsequent explicit evaluation of the value
	void	ConstructExplicit();
	
// computes the value of the interpolant.
// if dim=Dim,	assumes that x already contains the slack variable
// otherwise computes the slack variable
	double	Value(int dim, double* x);
// as above, explicit evaluation, does not require preprocessing
	double	ValueExplicit(int dim, double* x);

// computes the slack variable and stores it in Lip1
	void	ComputeSlack(double* x);

	int		LastError() {return m_lasterr;};

// this method is called when the interpolant is no longer needed, but is not automatically destroyed
// within the scope of its definition. Since the memory occupied can be fairly large, the user may wish
// to free the memory before the destructor does it. No other members can be called subsequently.
	void	FreeMemory();
};


#endif


#ifdef __cplusplus
extern "C" {
#endif

extern LIPDLL_API STCInterpolant gl;
extern LIPDLL_API SLipInt sli;
extern LIPDLL_API SLipIntInf slii;
//extern LIPDLL_API SLipClass slc;




/**************************************************************************

 ***************************************************************************/




#define NULL 0

/* interface to the members of SLipInt class ===================== */
LIPDLL_API double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index);

LIPDLL_API double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index);

LIPDLL_API double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index);

LIPDLL_API double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, 
								  double* Region, int* Index);

LIPDLL_API double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, 
								   double* Region, int* Index);


LIPDLL_API double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y);

LIPDLL_API double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);

LIPDLL_API double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);

LIPDLL_API double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);


LIPDLL_API void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y);

LIPDLL_API void	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y);

LIPDLL_API void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T,
			int* type, int* Cons, double* Region, double *W);

LIPDLL_API void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,
			int* type, int* Cons, double* Region, double *W);


LIPDLL_API void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, 
							  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
 // fR is 0, 1-left, 2-right

LIPDLL_API double	LipIntGetLipConst() ;
LIPDLL_API void	LipIntGetScaling(double *S) ;
LIPDLL_API int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
LIPDLL_API void	ConvertXData(int *Dim, int* npts,  double* XData);
LIPDLL_API void	ConvertXDataAux(int *Dim, int* npts,  double* XData, double *auxdata);

LIPDLL_API int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps);
LIPDLL_API int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, 
										   double* LC, double* eps);
LIPDLL_API int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, 
											double* LC, double* eps);


/* interface to the members of SLipIntInf class ====================================== */

LIPDLL_API double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index);

LIPDLL_API double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index);

LIPDLL_API double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index);

LIPDLL_API double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, 
								  double* Region, int* Index);

LIPDLL_API double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, 
								   double* Region, int* Index);


LIPDLL_API double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y);

LIPDLL_API double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);

LIPDLL_API double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);

LIPDLL_API double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);


LIPDLL_API void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y);

LIPDLL_API void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y);

LIPDLL_API void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T,
			int* type, int* Cons, double* Region, double *W);

LIPDLL_API void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,
			int* type, int* Cons, double* Region, double *W);


LIPDLL_API void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, 
							  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
 // fR is 0, 1-left, 2-right

LIPDLL_API double	LipIntInfGetLipConst() ;
LIPDLL_API void	LipIntInfGetScaling(double *S) ;
LIPDLL_API int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);

LIPDLL_API int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps);
LIPDLL_API int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, 
										   double* LC, double* eps);
LIPDLL_API int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, 
											double* LC, double* eps);


LIPDLL_API void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC);
LIPDLL_API void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W);




/* interface to the members of STCInterpolant class ====================================== */

// supplies the data to Interpolant and constructs the interpolant
// assuming a given Lipschitz constant, supplied by SetLipschitz
// if LipConstant was not supplied, tries to find it from the data
// assumes that all data are different. 

LIPDLL_API  int	STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y);

// as above, but for explicit evaluation, needs no preprocessing, but may be slower
LIPDLL_API  int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y);

// in the methods above, the coordinates of the data points in x are stored in rows

// the following methods store data in columns (like in fortran or Matlab)
// they use the transposed of the matrix x 
LIPDLL_API  int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y);

// as above, but for explicit evaluation, needs no preprocessing, but may be slower
LIPDLL_API  int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y);


// specify the Lipschitz constant for your function
LIPDLL_API  void	STCSetLipschitz(double* x);

// computes the value of the interpolant at any given point x
LIPDLL_API  double	STCValue( double* x );

// same but using explicit evaluation with no preprocessing
LIPDLL_API  double	STCValueExplicit( double* x );

LIPDLL_API  void	STCFreeMemory();




#ifdef __cplusplus
}
#endif


#endif 

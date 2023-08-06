# liblip    
Liblip is a library for multivariate scattered data interpolation<br>
The Lipschitz interpolant possesses a number of desirable features, such as continuous dependence on the data, preservation of Lipschitz properties and of the range of the data, uniform approximation and best error bounds. On the practical side, construction and evaluation of the interpolant is com- putationally stable. There is no accumulation of errors with the size of the data set and dimension.<br>
In addition to the Lipschitz constant, the user can provide information about other properties of f, such as monotonicity with respect to any subset of variables, upper and lower bounds (not necessarily constant bounds). If the data are given with errors, then it can be smoothened to satisfy the required properties. The Lipschitz constant, if unknown, can be estimated from the data using sample splitting and cross-validation techniques. The library also provides methods for approximation of locally Lipschitz functions.<br>
There are two alternative ways to compute the interpolant: fast and explicit.<br>
The fast method involves a preprocessing step after which the speed of evaluation is proportional to the logarithm of the size of the data set.<br>
The second alternative is to use the explicit evaluation method, which does not require any preprocessing. We recommend this method for most applications, as it provides more flexibility with smoothing and incorporating other properties of f.<br>
## Documentation
[User Manual](http://gbfiles.epizy.com/liblip2.pdf)

## Installation
To install type:
```python
$ pip install liblip
```
## Usage of the library 

```python
import liblip as ll
```
Follow these steps in your Python code to use the library:<br>
- Initialize resources<br>
- Use library function(s)<br>
- Free resources<br>
### Example how to initialize resources
```python
dim = 3<br>
npts = 1500<br>
x, XData, YData = ll.init( dim, npts)<br>
```

### Example how to free resources
```python
ll.free()<br>
```

### Usage of library functions
To use a library function follow these steps:
1. Initialize input arrays.
2. Initialize input parameters.
3. Call liblip function.
4. Evaluate output parameters. 
### Example
```python
import liblip as ll

dim = 3
npts = 1500
x, XData, YData = ll.init( dim, npts)

# to be continued 

ll.free()
```

### Parameters
#### Input parameters:
See input parameter list in user manual
#### Output parameters:
See output parameter list in user manual

### Test
To unit test type:
```python
$ test/test_procedural.py
```
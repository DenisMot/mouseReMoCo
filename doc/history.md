

# mouseReMoCo
The goal is to better understand how humans control the velocity of their movements.
[Guigon 2021](https://psycnet.apa.org/record/2021-74042-001)  proposed that motor control is based on three principles: 
- optimal feedback control
- control with a receding time horizon
- task representation by a series of via-points updated at fixed frequency

With `mouseReMoCo`, we want to test whether Guigon's theoretical predictions resist empirical tests: 
* replicate the results (in 1D task space) that back-and-forth movements at constant speed are in fact a sequence of 120 ms sub-movements, due to the sliding horizon control mode ([Guigon etal 2019](https://journals.physiology.org/doi/full/10.1152/jn.00576.2018)). 
* test the prediction that the same logic applies in a 2D task space, i.e., in circular steering at constant speed. 

## V1.1.0 
Fully operational version for user testing 

- Updated header in output files
- Lines to match with teh beeps in 

## V1.0.4 
First version for user testing. 


### 1D and 2 tasks with rhythmical beeps
  - back and forth at constant speed
  - circular steering at constant speed
  - new CLI keywords:
    - task
    - halfPeriod

### calibration 
  - screen to mm
  - tablet to mm
  - tablet to screen
  - display of calibration on screen (at start)
  - new CLI keywords: 
    - screenDiagonal
    - tabletSize
    - circlePerimeter_mm
    - interLineDistance_mm
    - lineHeight_mm

### Missing documentation

# LSL-Mouse 

### V 1.2.0 release candidate 1

#### Error rate display added  

`class PerformanceAtTask` computes the effective performance at each new sample

The logic is as follows:  

- count starts when the move has reached the path
- count a move from point A to point B if both A and B are inside/outside
- count for all record periods : effective performance is the sum of all periods (except the moves to reach the path)
- count a move from A to B in two metrics:   
  - Euclidean distance (pixel) : the classical distance from A to B.
    - For a same angular distance, a move that is farther from the circle centre will produce a longer path
  - Angular distance (radian): the phase angle from A to B
    - For a same Euclidean distance, a move that is farther from the circle centre will produce a smaller angle


In the computations, the effective performance is updated at each new move, following the logic :
- we want the standard deviation of the distribution of the radius of the trajectory
- we compute the sum of squares (and mean) incrementally ([see formula](http://datagenetics.com/blog/november22017/index.html))
- we use the sum of square to get the standard deviation
- we use the standard deviation to get the effective tolerance

This is done within `setEffectivePerformance`:

``` Java
private void setEffectivePerformance (double radius, int X, int Y ) {
double currentMean = radius;
double currentSumS = 0 ;
int currentNbSample = nbSample + 1;

// 	http://datagenetics.com/blog/november22017/index.html
currentMean = radiusMean + (radius - radiusMean) / currentNbSample ;
currentSumS = radiusSumS + (radius - radiusMean) * (radius - currentMean);

radiusMean = currentMean;
radiusSumS = currentSumS;
radiusStd  = stdev(currentSumS, currentNbSample);
effectiveTolerance = Math.sqrt(2 * Math.PI * Math.E) * radiusStd;

nbSample = currentNbSample;

}
```

#### Angular metrics
One tricky part is to properly compute the angular metrics...
My solution is to :
- shift (translate) X,Y to center of circle
- compute angle from horizontal using `atan`
- get the unsigned difference in angle (do not care if moving clockwise or not)
- take care of 'jumps' around 0 with atan...

``` java
private double phaseAngleDistance(int cX, int cY, int pX, int pY) {
// translate current XY to center of circle
int Xc = configuration.getCenterX() - cX;
int Yc = configuration.getCenterY() - cY;
// translate previous XY to center of circle
int Xp = configuration.getCenterX() - pX;
int Yp = configuration.getCenterY() - pY;
// get angles from horizontal
double Ac = Math.atan2(Yc, Xc);
double Ap = Math.atan2(Yp, Xp);
// get the unsigned difference in angle (do not care if moving clockwise or not)
double angle = Math.abs(Ac - Ap);
// cancel angle jumps around horizontal
if (angle > Math.PI) {
  angle = 2 * Math.PI - angle;
}
return angle ;
}

```



## V 1.2.0 release candidate 2

* 2020 Oct 30 :  
  - type 'w' to display the effective target width
  - Phase angle is now computed and displayed

## V 1.2.0 release candidate 3

* 2020 Nov 04 :  
  - Effective tolerance is displayed by trial  
  - Central target during rest is suppressed
  - Bug corrections:
    - Effective tolerance is now computed with cursor radius


## V 1.2.0 release candidate 4

* 2020 Nov 08 :  
- Added a histogram of radius by trial
- Refactoring:
  - Added `isWithPauseTarget` in configuration   
  - Added radius limits without cursor size in configuration
    - create `radiusInternalLimit` and `radiusExternalLimit` and initialization
    - rewrite `drawEffectiveTolerance` in `DoubleCircle` using radius limits
- Bug corrections:
  - do not draw effective tolerance if radius was not initialized (`R <= 0`)


-----
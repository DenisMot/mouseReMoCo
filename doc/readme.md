
# mouseReMoCo/doc — Documentation

<!--
To re generate toc
cd DOC
cat DOC/readme.md | /Users/dm/bin/gh-md-toc -
 -->

* [Command line arguments](#command-line-arguments)
* [Calibration](#calibration)
* [Output in CSV files](#output-in-csv-files)
	* [Header block](#header-block)
		* [configuration line](#configuration-line)
		* [timestamp](#timestamp)
	* [data.csv](#datacsv)
	* [markers.csv](#markerscsv)
		* [markers block](#markers-block)
		* [typical markers sequence](#typical-markers-sequence)
* [LSL Streams (and matlab)](#lsl-streams-and-matlab)
	 * [Data](#data)
	 * [Markers](#markers)
* [Code examples](#code-examples)
	 * [isInside](#isinside)

# Command line arguments

Command line arguments are possible :

```
java -jar mouseReMoCo.jar -borderColor blue -cycleDuration 10
```

| Group  		| Parameter   			|  unit  | comment |
| ----- 		| ------------- 		|------- | ------------ |
| App 			|  autoStart        	| second | time before automatic start of the sequence (default: 3600)
|  	  			|  cycleMaxNumber 		| int    | number of Record-Pause cycles in the sequence
|  				|  cycleDuration 		| second | duration of the Record (or Pause) phase
| Graphics		|  borderRadius			|  pixel | radius of the border of elements 
| 				|  cursorRadius 		|  pixel | radius of the (circular) cursor
| 				|  borderColor 		  	|  RGB   | color of the border of graphic elements
| 				|  textColor 		  	|  RGB   | color of the text messages 
| 				|  backgroundColor 		|  RGB   | default = black 
| Record-Pause 	|  cursorColorRecord	|  RGB   | color during Record phase  (red)
| 				|  cursorColorWait 		|  RGB   | color during Pause phase (yellow)
| Calibration 	|  screenDiagonal 		| mm 	 | diagonal of the screen used for the display
| 			  	|  tabletSize 			| mm=pixel | `311x216=62200x43200`: width and heigh of graphic tablet 
| Circular task | indexOfDifficulty 	|  bit	| from the [Steering Law](https://en.wikipedia.org/wiki/Steering_law). **NOTE:** A high ID value might result in tolerance = 0 pixel, hence an error rate = 100%.    
| 				|  circlePerimeter_mm 	| mm 	| perimeter of the target circle (middle of external and internal radius)
| Linear task	|  interLineDistance_mm | mm 	| distance between the (left and right) target lines
| 				| lineHeight_mm 		| mm 	| height of the (left and right) target lines 


RGB should be a valid color name such as {blue, red, white, yellow}
https://docs.oracle.com/javase/8/docs/api/java/awt/Color.html


To allow for multiple executions of mouseReMoCo without overwriting the previous output files, the output files must be renamed. This is easily done in a command line script.

With Windows OS, a typical `mouseReMoCo.bat` file reads:
```
cd "C:\"
java -jar MouseReMoCo.jar -cycleDuration 20 -cursorRadius 20 -cycleMaxNumber 3
rename data.csv data_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.csv
rename marker.csv marker_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.csv
pause
```

With *nix OS, a typical `mouseReMoCo.sh` file reads :

```
#!/bin/sh

# move to the chosen directory 
cd ~/

# run mouseReMoCo with command line parameters
java -jar mouseReMoCo.jar -cycleDuration 20 -cursorRadius 20 -cycleMaxNumber 3

# avoid overwriting output files on a future run 
cp data.csv marker.$(date "+%Y.%m.%d-%H.%M.%S").csv
cp marker.csv marker.$(date "+%Y.%m.%d-%H.%M.%S").csv
```
**NOTE:** Do not forget to make your `.sh` file executable with   `chmod u+x mouseReMoCo.sh`

# Calibration 
For most experiments, the calibration is not necessary: the startup message could simply be ignored.

However, it is sometimes necessary to map the visual space and the hand space (unless using a device doing that for you, e.g., [Wacom cintiq](https://www.wacom.com/fr-fr/products/pen-displays/wacom-cintiq)). We want that: 
- center of tablet = center of display 
- 1 mm on tablet = 1 mm on display 

This is where the calibration is necessary: 
- to know the real world size of the display: 
	- set `screenDiagonal` on the command line 
- to know the real world size of the tablet: 
    - set `tabletSize` on the command line as e.g., `311x216=62200x43200` 
		- `311x216` is the size of the active zone on the tablet **in millimeter**
		- `62200x43200` is the size of the active zone on the tablet **in pixel**, usually given in the device driver. If you cannot find the exact values, you can safely duplicate the values in mm. 

The tablet size will be represented in green on the display when the program starts. 

If (and only if) you provide calibration information on the command line, the startup message window provides the following information:
- Area of the screen corresponding to the complete tablet (also represented in green on the display when the program starts)
- Area of the tablet corresponding to the complete screen 

# Output in CSV files
CSV output consists in 2 files :
- `data.csv`: the mouse coordinate over time
- `marker.csv`: the marker generated over time  

These are CSV files organized as follows :
- header block  
- empty line
- data block

## Header block
The first lines in the CSV files are the `header_block` (up to the empty line) :  
- configuration line
- timestamp  

The header block is **identical** in all CSV files corresponding to the same record.


### configuration line
The `configuration_line` (L1) consists in a collection of name-value pairs, where pairs are separated by `';'` (semicolon), within which name and value are separated by `' '` (space).  
An example of the (long) first line is:
```
software mouseReMoCo;version 1.2.2;isWithLSL true;screenWidth 1352;screenHeight 815;centerX 676;centerY 407;autoStart 3600;cycleMaxNumber 6;cycleDuration 20;borderColor java.awt.Color[r=255,g=255,b=255];textColor java.awt.Color[r=255,g=255,b=255];backgroundColor java.awt.Color[r=0,g=0,b=0];cursorColorRecord java.awt.Color[r=255,g=0,b=0];cursorColorWait java.awt.Color[r=255,g=255,b=0];task circular;cornerX 349;cornerY 80;externalRadius 327;internalRadius 247;borderRadius 1;cursorRadius 16;indexOfDifficulty 38.30069341504152;taskRadius 286.5;taskTolerance 47;halfPeriod 1750
2022-04-01 08:33:00.578

timestamp,mouseX,mouseY,mouseInTarget
1648794797873,606,199,1
1648794797881,605,199,1
1648794797889,605,200,1
1648794797911,604,200,1
1648794797923,603,201,1
1648794797929,602,202,1
1648794797939,601,202,1
1648794797944,600,203,1
1648794797953,599,204,1
1648794797961,597,205,1
1648794797969,596,206,1
1648794797977,593,208,1
1648794797985,592,210,1
````
After parsing the previous `configuration_line`, we get :
```
software = mouseReMoCo
version = 1.2.2
isWithLSL = true
screenWidth = 1352
screenHeight = 815
centerX = 676
centerY = 407
autoStart = 3600
cycleMaxNumber = 6
cycleDuration = 20
borderColor = java.awt.Color[r=255,g=255,b=255]
textColor = java.awt.Color[r=255,g=255,b=255]
backgroundColor = java.awt.Color[r=0,g=0,b=0]
cursorColorRecord = java.awt.Color[r=255,g=0,b=0]
cursorColorWait = java.awt.Color[r=255,g=255,b=0]
task = circular
cornerX = 349
cornerY = 80
externalRadius = 327
internalRadius = 247
borderRadius = 1
cursorRadius = 16
indexOfDifficulty = 38.30069341504152
taskRadius = 286.5
taskTolerance = 47
halfPeriod = 1750
```
**IMPORTANT NOTE**: the order of the parameters may vary.  *You MUST NOT  rely on order when parsing the configuration line*. You should check for the name of each name=value pair.  

The parameters in the `configuration_line` detail the current configuration of the display and of the target, so to allow for the "replay" the recorded data, or to allow for the post-hoc analysis of the data. The name of each parameter should be be easy to understand, and the tables below provides more information:  

* General parameters 

| Parameter   |  unit | comment |
| ------------- |------------- | ------------ |
|  software 		| string  | `mouseReMoCo`
|  version 			| x.x.x  | semantic numbering of version
|  isWithLSL 		|  bool |  `true` if LSL is active
|  autoStart        | s    | default = 3600 (1 hour)
|  cycleMaxNumber 	| int  | number of Record-Pause cycles in the sequence ; default = 6
|  cycleDuration 	| s  |  duration of the Record (or Pause) phase ; default = 10
|  screenWidth   	|  pixel | :warning: JAVA origin is top-left 
|  screenHeight 	|  pixel | :warning: JAVA origin is top-left
|  centerX      	|  pixel | center of screen ; :warning: JAVA origin is top-left 
|  centerY      	|  pixel | center of screen ; :warning: JAVA origin is top-left 
|  borderColor 		|  RGB  | default = white
|  textColor 		|  RGB  | default = white
|  backgroundColor 	|  RGB | default = black
|  cursorRadius 	|  pixel | default = 16
|  cursorColorRecord|  RGB | color during Record phase ; default = red
|  cursorColorWait 	|  RGB | color during Pause phase ; default = yellow
|  task 			|  string |  linear / circular 

* circular task parameters 

| Parameter   |  unit | comment |
| ------------- |------------- | ------------ |
|  externalRadius 	|  pixel | radius of the external circle
|  internalRadius  	|  pixel | radius of the internal circle
|  borderRadius		|  pixel | width of the border  (drawn outside the circle)
|  taskRadius 		|  pixel | radius of the task (average of external and internal radius)
|  taskTolerance 	|  pixel | radius error tolerance (difference of external and internal radius)
|  indexOfDifficulty | bit     | ID = A / W in the [Steering Law](https://en.wikipedia.org/wiki/Steering_law)
|  circlePerimeter_mm 	| mm | 	perimeter of the target circle (2 * pi * taskRadius) :warning: only if screen diagonal is set 

* linear task parameters 

| Parameter   |  unit | comment |
| ------------- |------------- | ------------ |
|  interLineDistance_mm  | mm | distance between the (left and right) target lines
|  lineHeight_mm 		| mm | 	height of the (left and right) target lines 
|  Diagonal 	| pixel | [x1=109,y1=850,x2=1403,y2=66] coordinate pairs (:warning: JAVA: from top-left)
|  LineLeft 		| pixel | [x1=647,y1=690,x2=500,y2=447] coordinate pairs (:warning: JAVA: from top-left)
|  LineRight	| pixel | [x1=1012,y1=469,x2=865,y2=226] coordinate pairs (:warning: JAVA: from top-left)


* calibration parameters 

| Parameter   |  unit | comment |
| ------------- |------------- | ------------ |
|  mm2px 			| float | 	how many pixels in 1 mm  


* rhythm parameters 

| Parameter   |  unit | comment |
| ------------- |------------- | ------------ |
|  halfPeriod 	| ms | 	how many milliseconds between beeps ; default = 0 (no beeps)


### timestamp
The timestamp corresponds to the date (in milliseconds) of the effective start of mouseReMoCo, with the following format  
`2020-04-29 12:05:21.855`

## data.csv
A typical data file looks as follows, for the circular task:
```
software mouseReMoCo;version 1.1.0;isWithLSL true;screenWidth 1512;screenHeight 916;centerX 756;centerY 458;autoStart 3600;cycleMaxNumber 6;cycleDuration 20;borderColor java.awt.Color[r=255,g=255,b=255];backgroundColor java.awt.Color[r=0,g=0,b=0];cursorColorRecord java.awt.Color[r=255,g=0,b=0];cursorColorWait java.awt.Color[r=255,g=255,b=0];task circular;cornerX 378;cornerY 80;externalRadius 378;internalRadius 302;borderRadius 1;cursorRadius 16;indexOfDifficulty 49.60793980901092;taskRadius 339.5;taskTolerance 43
2022-03-05 21:20:17.450

timestamp,mouseX,mouseY,mouseInTarget
1646511624345,439,347,1
1646511624371,439,346,1
1646511624397,439,345,1
1646511624403,439,344,1
```

The `data_block` contains 4 columns of data (coma separated):
- Line 1: column headers
	- `timestamp` : date of the [mouse motion event](https://docs.oracle.com/javase/7/docs/api/java/awt/event/MouseEvent.html), in [milliseconds](https://docs.oracle.com/javase/8/docs/api/java/lang/System.html#currentTimeMillis--)
	- `mouseX` and `mouseY`: coordinates of the center of the cursor **from top-left**
	- `mouseInTarget`: 1 if the cursor is within the target limits (0 otherwise)  
- Next lines : data



## marker.csv

A typical marker file looks as follows (note the very long first line):
```
screenWidth 1440;screenHeight 856;cornerX 372;cornerY 80;centerX 720;centerY 428;externalRadius 348;internalRadius 268;borderRadius 1;cursorRadius 16;borderColor java.awt.Color[r=255,g=255,b=255];backgroundColor java.awt.Color[r=0,g=0,b=0];cursorColorRecord java.awt.Color[r=255,g=0,b=0];cursorColorWait java.awt.Color[r=255,g=255,b=0];autoStart 3600;cycleMaxNumber 6;cycleDuration 3;software mouseReMoCo;version 1.1.0;task CircularTarget;isWithLSL true
2020-05-02 20:28:22.268

2020-05-02 20:28:26.054,1588444106054,KeyTyped=32 DoCycleChange
2020-05-02 20:28:26.056,1588444106056,DoCycleChange:DoStartCycleTimedSequence
2020-05-02 20:28:26.056,1588444106056,DoCycleChange:DoRecord RecordDone=0 PauseDone=0 ToDo=6
2020-05-02 20:28:29.060,1588444109060,DoCycleChange:DoPause RecordDone=1 PauseDone=0 ToDo=6
2020-05-02 20:28:32.060,1588444112060,DoCycleChange:DoRecord RecordDone=1 PauseDone=1 ToDo=6

```
### markers block
The `markers_block` contains 3 columns (coma separated):
- Col 1: `timestamp` in a human readable information
- Col 2: `timestamp` in [Java milliseconds](https://docs.oracle.com/javase/8/docs/api/java/lang/System.html#currentTimeMillis--)
- Col 3: Marker (string)


### typical markers sequence  
The markers occur as follows in a typical sequence :

```
2020-05-02 20:28:26.054,1588444106054,KeyTyped=32 DoCycleChange
2020-05-02 20:28:26.056,1588444106056,DoCycleChange:DoStartCycleTimedSequence
2020-05-02 20:28:26.056,1588444106056,DoCycleChange:DoRecord RecordDone=0 PauseDone=0 ToDo=6
2020-05-02 20:28:29.060,1588444109060,DoCycleChange:DoPause RecordDone=1 PauseDone=0 ToDo=6
2020-05-02 20:28:32.060,1588444112060,DoCycleChange:DoRecord RecordDone=1 PauseDone=1 ToDo=6
...
2020-05-02 20:29:02.071,1588444142071,DoCycleChange:DoEndPause RecordDone=6 PauseDone=6 ToDo=6
2020-05-02 20:29:06.425,1588444146425,KeyTyped=113 WINDOW_CLOSING
```

More detailed explanations below :

> USER : mouseReMoCo was launched : waiting for manual start  
> USER : press ‘space’: start recording/pause sequence

- `2020-05-02 20:28:26.054,1588444106054,KeyTyped=32 DoCycleChange`  
	Key number `32` was typed `[ascii(32) = ‘ ’]`  
	Event `DoCycleChange` was sent  

- `2020-05-02 20:28:26.056,1588444106056,DoCycleChange:DoStartCycleTimedSequence`  
	Event `DoCycleChange:DoStartCycleTimedSequence` was sent  
	This is an automatic event (no KeyTyped)  
	NB : this is a direct consequence of the previous KeyTyped (~1 ms before)  

- `2020-05-02 20:28:26.056,1588444106056,DoCycleChange:DoRecord RecordDone=0 PauseDone=0 ToDo=6`  
	Event `DoCycleChange:DoRecord` was sent with context `RecordDone=0 PauseDone=0 ToDo=6`  
	This is an automatic event (no KeyTyped)  

- `2020-05-02 20:28:29.060,1588444109060,DoCycleChange:DoPause RecordDone=1 PauseDone=0 ToDo=6`  
	Event `DoCycleChange:DoPause` was sent with context `RecordDone=1 PauseDone=0 ToDo=6`  
	This is an automatic event (no KeyTyped)   

- `2020-05-02 20:28:32.060,1588444112060,DoCycleChange:DoRecord RecordDone=1 PauseDone=1 ToDo=6`  
	Event `DoCycleChange:DoRecord` was sent with context `RecordDone=1 PauseDone=1 ToDo=6`  
	This is an automatic event (no KeyTyped)  

. . .  
	This will automatically continue up to the end of the Record/Pause sequence  

> USER : press ‘q’ to quit  

- `2020-05-02 20:29:06.425,1588444146425,KeyTyped=113 WINDOW_CLOSING`  
	Key number 113 was typed [ascii(113) = ‘q’]  
	Event WINDOW_CLOSING was sent  

# LSL Streams (and matlab)
mouseReMoCo streams data and markers following the LSL specifications
https://github.com/sccn/xdf/wiki/Specifications  

## Data
Data are stored in a stream of type [MoCap](https://github.com/sccn/xdf/wiki/MoCap-Meta-Data):
- in stream numbered `s`, which corresponds to the stream that satisfies:
``` matlab
streams{s}.info.source_id == ‘MouseData’
% and also (though not useful)
% streams{s}.info.name = ‘Mouse’ & streams{s}.info.type = ‘MoCap’
```
- with description in
``` matlab
streams{s}.info.desc.channels.channel{:}
```

- with data and timestamps in
``` matlab
mouseX = streams{s}.time_series(1, :);
mouseY = streams{s}.time_series(2, :);
mouseInTarget = streams{s}.time_series(3, :);
timestamp = streams{s}.time_stamps;
% consider transposition to get column vectors
```  


## Markers
Markers are stored in a stream of type [Markers](https://github.com/sccn/xdf/wiki/Markers-Meta-Data):
- in stream numbered `s`, which corresponds to the stream that satisfies:
``` matlab
streams{s}.info.source_id == ‘MouseMarkers’
% and also (though not useful)
% streams{s}.info.name = ‘Mouse’ & streams{s}.info.type = ‘Markers’
```
- with labels and timestamps in
``` matlab
streams{s}.time_series{i}  % {} because markers contain strings
streams{s}.time_stamps(i)
```  

# Code examples
## isInside
To check if the cursor is within the target, mouseReMoCo uses :

``` java
// check if the cursor is inside the circular target
// inside = no part of the cursor is hitting the walls...

// mouse events are relative to the window listener
int X = mouseEvent.getX();
int Y = mouseEvent.getY();

// make event relative to frame (using insets)
X = X - configuration.getFrameInsets().left;
Y = Y - configuration.getFrameInsets().top;

// make event relative to center of circle
int dx = configuration.getCenterX() - X;
int dy = configuration.getCenterY() - Y;

double d = Math.sqrt(dx * dx + dy * dy ); // distance from circle center

int limitInternal = configuration.getInternalRadius();
int limitExternal = configuration.getExternalRadius();

// cursor has a radius : remove the size of the cursor
limitInternal = limitInternal + configuration.getCursorRadius() ;
limitExternal = limitExternal - configuration.getCursorRadius() ;

// border is drawn inside the circle: remove border of external circle
limitExternal = limitExternal - configuration.getBorderRadius();

boolean isInside = (d < limitExternal & d > limitInternal);
```

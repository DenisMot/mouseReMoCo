
# mouseReMoCo
Ths name is a shortcut for *"mouse for Research on Motor Control"*...  

mouseReMoCo does the following :
* It displays a target task that the participant has to perform, *with optional rhythmical pacing*
	 * linear back and forth task 
     * circular steering task 
* It records the mouse coordinates over time  
	* Data is saved into  `data.csv` and `marker.csv` (in the same directory), 
	* Data is eventually streamed to LSL   
https://labstreaminglayer.readthedocs.io   


### Requirements :
- Java 8 (or newer): https://www.java.com/fr/download/  
- `mouseReMoCo.jar`: download the last release (see in [Releases](https://github.com/DenisMot/mouseReMoCo/releases))
* Optional, but necessary for LSL streaming
	- go to https://github.com/sccn/liblsl/releases
	- Select the `liblsl-.....` archive corresponding to your needs. A reasonable choice is the latest stable version corresponding to your operating system.   
	- download the archive and expand it
	- copy the necessary  `liblslxxx.zzz` file next to `mouseReMoCo.jar`
		- Windows 7:  `liblsl32.dll`
		- Windows 10+: `liblsl64.dll`
		- OSX: `liblsl64.dylib` (it works well under roseta for M1)
		- Unix: `liblsl64.so`
	- :warning: **Make sure you have `mouseReMoCo.jar` and `liblslxxx.zzz` in the same directory**

### Launch
- double click `mouseReMoCo.jar`, this should do it...

### Console use
This is the **standard way to use mouseReMoCo**, as you will probably want to configure the software for your needs... 
- `cd ` to the directory where mouseReMoCo.jar is located    
- `java -jar mouseReMoCo.jar`   
- To list the command line options :  
	- `java -jar mouseReMoCo.jar -h`


### User input
To manage the phases of an experiment, press the following keys:
- `space`: toggle record-pause
- `c`: display configuration
- `q`: quit

You can also press (undocumented): 
- `w`: real time view of the circular steering performance

-----  

More detailed information: see in [mouseReMoCo/doc](/doc).  


-----  
mouseReMoCo was developed by reusing [LSL-Mouse](https://github.com/KarimaBak/LSL-Mouse). Many thanks to [Pierre JEAN](https://github.com/pierrejean) for his precious help with Java and LSL.

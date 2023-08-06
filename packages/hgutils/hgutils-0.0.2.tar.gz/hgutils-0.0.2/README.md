# hgutils

[hgutils](https://github.com/hiteshgulati/hgutils) is a python package having a repository of various utilities which come handy during python project development. 

## Current Features

* Timer - A python class to measure and print execution time of python code running over loops and in series.

## Timer
This is a python class built to measure the execution time of python script. 

#### Usage
Install `hgutils` to begin using timer class

```
$ pip install hgutils
```

Import `hgutils` in the python project and initiate `timer` class by assigning it to a variable while passing the project name in argument.

```
import hgutils
hgt = hgutils.timer("My Revolutionary Project")
```

Initiate the a new timer by calling `start` function and passing a name in argument. The new initiated timer will be child to current timer, which means current timer will continue to run and a new sub timer will be initiated.

```
hgt.start('New Timer')
```

To stop or end current timer simply call `stop` function. This function will end current timer, any parent timer(s) will keep on running. To end stop parent timer call the stop function again.

```
hgt.stop()
```

To get status of timers use `print` function. 
```
hgt.print()
```

`print` functions have following arguments to fine tune the required details:
* units - *millisesonds, seconds, minutes, hours, days and auto* Default - *auto*. Defines the units in which time of execution will be printed. *auto* will automatically select the best units based on the calculated time of execution.
* verbose - *0, 1, 2* Default - *0*. Determines the amount of information which will be printed. 
    - 0: Time of only current timer will be printed
    - 1: Time of current timer and its parent will be printed
    - 2: Time of all the timers used in the project will be printed

Status of timer can also be printed while stoping the timer by passing argument `print=True` in `stop` function.
```
hgt.stop(print=True,verbose=1)
```

To reset the timer use `reset` function. This will delete all existing timers and initiate a new timer for project.

```
hgt.reset()
```

#### Examples

Here's a sample python project implemented using timer utility.

```
import hgutils
import time

print("Using timer utility available in hgutils")
hgt = hgdatetime.timer("hgutils timer sample project")
time.sleep(2)
hgt.start("Top Level Timer")
for i in range(4):
    hgt.start("i="+str(i))
    time.sleep(1)    
    if i==2:
        for j in range(5):
            hgt.start("j="+str(j))
            time.sleep(.04)
            hgt.stop(print=True,verbose=1)
    hgt.stop(print=True,verbose=1)
hgt.stop(print=True,verbose=1)
hgt.print(verbose=2)
```

**Output**
```
Using timer utility available in hgutils
	 Top Level Timer - 1.01 seconds*
		 i=0 - 1.01 seconds
	 Top Level Timer - 2.01 seconds*
		 i=1 - 1.0 seconds
		 i=2 - 1.05 seconds*
			 j=0 - 45.11 milliseconds
		 i=2 - 1.1 seconds*
			 j=1 - 45.07 milliseconds
		 i=2 - 1.14 seconds*
			 j=2 - 45.07 milliseconds
		 i=2 - 1.19 seconds*
			 j=3 - 44.15 milliseconds
		 i=2 - 1.23 seconds*
			 j=4 - 41.47 milliseconds
	 Top Level Timer - 3.24 seconds*
		 i=2 - 1.23 seconds
	 Top Level Timer - 4.24 seconds*
		 i=3 - 1.01 seconds
 hgutils timer sample project - 6.25 seconds*
	 Top Level Timer - 4.24 seconds
 hgutils timer sample project - 6.25 seconds*
	 Top Level Timer - 4.24 seconds
		 i=0 - 1.01 seconds
		 i=1 - 1.0 seconds
		 i=2 - 1.23 seconds
			 j=0 - 45.11 milliseconds
			 j=1 - 45.07 milliseconds
			 j=2 - 45.07 milliseconds
			 j=3 - 44.15 milliseconds
			 j=4 - 41.47 milliseconds
		 i=3 - 1.01 seconds
```

## Authors
[@hiteshgulati](https://github.com/hiteshgulati)
[My Blog](https://hiteshgulati.com)


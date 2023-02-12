# ArControl-convert2-smcat
Convert ArControl Designer task to ["State Machine Cat"](https://github.com/sverweij/state-machine-cat) smcat file for beautiful visulazition.

## Install
Setup the python enviroment.

> pip install -U git+https://github.com/chenxinfeng4/ArControl-convert2-smcat

## Convert file
The easiest way.

> python -m arcontrol2smcat "Arcontrol/task/Go_NoGO/Go_NoGO.aconf"

Else go to the script. See the play ground.
```python
import arcontrol2smcat

taskfile = './Go_NoGO.aconf'
smcatfile = arcontrol2smcat.convert(taskfile)
print(f'OUTPUT to {smcatfile}')  #Go_NoGO.smcat
```

## View the result
Copy the context of the `XXX.smcat` file to the website https://state-machine-cat.js.org/
Or install local smcat by 
> npm install --global state-machine-cat
>
> smcat playground/Go_NoGo.smcat

### The Go/NoGo task
<img src="playground/Go_NoGo.svg" height=600>

### The OptoLaser task
![OptoLaser](playground/OptoLaser.svg)

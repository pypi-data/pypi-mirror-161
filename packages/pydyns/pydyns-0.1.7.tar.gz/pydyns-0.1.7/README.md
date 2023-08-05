pydyns
==============

Python wrapper for [DynS's C++ library](https://github.com/FishermenOnTuesdays/DynamicSystem) built with [pybind11](https://github.com/pybind/pybind11).
This requires Python 3.6+

Installation
------------

using PYPI
 - `pip install pydyns`

from source
 - clone this repository with `git clone --recurse-submodules -j8 https://github.com/FishermenOnTuesdays/pydyns.git`
 - `pip install ./pydyns`

NOTE: on macOS there could be errors with openMP headers, if so run `brew install libomp` and problem should be resolved.

Test call
---------

```python
import pydyns as dyns
# Lorenz system
dynamic_system = dyns.DynamicSystem([0.1,0.1,0.1], ["10*(y-x)","x*(28-z)-y","x*y-2.66*z"], 'x,y,z')
dynamic_system.SetDt(0.01)
trajectory = dynamic_system.GetTrajectory(100)
```

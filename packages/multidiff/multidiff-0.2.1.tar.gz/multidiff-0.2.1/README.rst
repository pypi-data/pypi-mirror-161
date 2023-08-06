multi-diff
==========

multi-diff is a Python module for fitting and manipulating
multi-diffusion data, such as concentration profiles measured in
multicomponent systems with coupled diffusion between components. It is
distributed under the 3-Clause BSD license.


Release howto
-------------

- Edit `setup.py` file with correct version number, if required update the dependencies

- Tag the release number, for example `git tag "v0.2"`

- Upload to pypi
  
```  
  python3 -m twine upload dist/* 
```

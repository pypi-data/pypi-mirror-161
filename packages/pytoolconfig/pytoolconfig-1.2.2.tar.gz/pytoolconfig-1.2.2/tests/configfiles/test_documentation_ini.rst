pytoolconfig supports the following configuration files
   1. pyproject.toml  
   2. setup.cfg  
   3. pytool.toml  
  
=====================  =======================================  ======  =========  ================================================  ===================
name                   description                              type    default    universal key                                     command line flag
=====================  =======================================  ======  =========  ================================================  ===================
subtool.subtool
foo_other.foo_other    Tool One                                         no                                                           ('--foo', '-f')
min_py_ver.min_py_ver  This field is set via an universal key.                     Mimimum target python version. Requires PEP 621.
=====================  =======================================  ======  =========  ================================================  ===================
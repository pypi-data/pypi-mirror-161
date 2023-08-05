
from setuptools import find_packages, setup
setup(
    name= "degradationmodels",
    version= "0.0.3",
    packages= find_packages(),
    py_modules=['stc','ssoc','st','sd','F_d1','f_dt','L_cyc','L_cal'],
) 


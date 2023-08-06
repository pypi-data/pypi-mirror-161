'''
Compilation de la librairie wolfogl via Cython 
  si la librairie fournie n'est pas compatible avec la version locale de Python3 (!=3.9)

Il faut lancer le script via votre interpréteur Python3 dans une ligne de commande ou un Powershell

Todo :

python compile_wcython.py build_ext --inplace

    --or--

python3 compile_wcython.py build_ext --inplace

Result :
   wolfogl.cp3xx-win_amd64.pyd    où xx est la sous-version du Python local

'''
from distutils.core import Extension,setup
from Cython.Build import cythonize

ext=Extension(name="wolfogl", sources=["WolfOGL.pyx"], libraries = ['opengl32']) #, extra_compile_args=['-O3'])
setup(
    ext_modules =  cythonize(ext)
)


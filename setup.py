#! /usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
setup (name='PPC-Project',
       version='1.0',
       description='Herramienta multiplataforma para la docencia e investigacion en gestion de proyectos',
       author='Cristina Urbano Roldan',
       author_email='i12urrom@uco.es',
       url= 'http://pi.ax5.org/ppc-proyect',
       py_modules=['graph', 'pert', 'proyecto', 'proyecto.glade'],
       data_files=(['proyecto.glade']))   

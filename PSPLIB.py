#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main program
#-----------------------------------------------------------------------
# PPC-PROJECT
#   Multiplatform software tool for education and research in 
#   project management
#
# Copyright 2007-8 Universidad de Córdoba
# This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#********************************************************************************************************************** 
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
      #                    PSPLIB                        #
      #++++++++++++++++++++++++++++++++++++++++++++++++++#
 
#-----------------------------------------------------------
# Lectura de un proyecto de la librería de proyectos PSPLIB   
#
# Parámetros: f (fichero) 
#
# Valor de retorno: prelaciones (lista que almacena las actividades 
#                                y sus siguientes)
#                   rec (lista que almacena el nombre y las unidades
#                       de recurso)
#                   asig (lista que almacena las duraciones y las 
#                         unid. de recurso necesarias por cada actividad)
#----------------------------------------------------------- 
     
def leerPSPLIB(f):
   prelaciones=[]
   asig=[]
   rec=[]
   l=f.readline()         
   while l:
      # Lectura de las actividades y sus siguientes
      if l[0]=='j' and l[10]=='#':
         l=f.readline()
         while l[0]!='*':                   
            prel=l.split()[0], l.split()[3:]
            prelaciones.append(prel)
            l=f.readline()
            
         # Lectura de la duración de las actividades y de las unidades de recursos necesarias por actividad
      if l[0]=='-':
         l=f.readline()
         while l[0]!='*': 
            asig.append(l.split())
            l=f.readline()
         
      # Lectura del nombre, tipo y unidad de los recursos
      if l[0:22]=='RESOURCEAVAILABILITIES':
         l=f.readline()
         while l[0]!='*': 
            rec.append(l.split())
            l=f.readline()
           
      l=f.readline()  
         
   return (prelaciones, rec, asig)


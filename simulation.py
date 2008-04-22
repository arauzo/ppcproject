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
import random

# Internationalization
import gettext
APP='PPC-Project' #Program name
DIR='po' #Directory containing translations, usually /usr/share/locale
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)


#*******************************************************************
#-----------------------------------------------------------
# Cálculo de las F.Absolutas y F.Relativas 
#
# Parámetros: dMax (duración máxima)
#             dMin (duración mímima)
#             itTotales (iteraciones totales)
#             N (número de intervalos)
#
# Valor de retorno: Fa (frecuencias absolutas)
#                   Fr (frecuencias relativas)
#----------------------------------------------------------- 

def calcularFrecuencias(duraciones, dMax, dMin, itTotales, N):
     Fa=[]
     Fr=[]
     # Se inicializa el vector de F.Absolutas
     for n in range(N):
        Fa.append(0)

     # Se calculan las F.Absolutas
     for d in duraciones:
         x=posicion(d, dMax, dMin, N)
         Fa[x]+=1

     # Se calculan las F.Relativas
     for a in Fa:
        r='%2.2f'%(float(a)/itTotales)
        Fr.append(r)

     return Fa, Fr

#*******************************************************************
#-----------------------------------------------------------
# Cálculo de la posición de una duración dentro del 
#          vector de F.Absolutas
#
# Parámetros: d (duración)
#             dMax (duración máxima)
#             dMin (duración mí­nima)
#             N (número de intervalos)
#
# Valor de retorno: x (posición)
#----------------------------------------------------------- 

def posicion(d, dMax, dMin, N):
     x = int ( ((d-dMin)/(dMax-dMin)) * N )
     return x

#*******************************************************************
#-----------------------------------------------------------
# Cálculo de la duración correspondiente a una posición 
#          (inversa de la Función anterior)
#
# Parámetros: x (posición)
#             dMax (duración máxima)
#             dMin (duración mí­nima)
#             N (número de intervalos)
#
# Valor de retorno: d (duración)
#----------------------------------------------------------- 

def duracion(x, dMax, dMin, N):
        d = ( x*(dMax-dMin)/N ) + dMin
        return d


#*******************************************************************
#-----------------------------------------------------------
# Prepara los datos de la simulación para ser mostrados
#          en formato CSV
#
# Parámetros: duraciones (lista con las duraciones de la simulación)
#             iteraciones (número de iteraciones totales)
#             media (duración media)
#             dTipica (desviación tí­pica)
#             modeloCriticidad (lista de caminos e í­ndice de criticidad)
#
# Valor de retorno: s (texto a mostrar en formato CSV) 
#-----------------------------------------------------------

def datosSimulacion2csv(duraciones, iteraciones, media, dTipica, modeloCriticidad): 
        s=''
        s+=gettext.gettext('SIMULATION DATA')
        s+='\n'
        s+='\n'
        s+=gettext.gettext('N, I.CRITICIDAD, PATH')
        s+='\n'
        for n in range(len(modeloCriticidad)):
           s+= modeloCriticidad[n][0]+','+ modeloCriticidad[n][1]+','+'"'+modeloCriticidad[n][2]+'"'
           s+='\n'
        s+='\n'
        s+='\n'
        s+=gettext.gettext('AVERAGE, TYPICAL DEV.')
        s+='\n'
        s+= media+','+dTipica
        s+='\n'
        s+='\n'
        s+=gettext.gettext('TOTAL SIMULATIONS')
        s+='\n'
        s+= iteraciones
        s+='\n'
        s+='\n'
        s+=gettext.gettext('DURATIONS')
        s+='\n'
        for d in duraciones:
           s+= str(d)
           s+='\n'

        #print s
        return s        

#***************************************************************
#-----------------------------------------------------------
# Generación de un número aleatorio para una 
#          distribución uniforme
#
# Parámetros: op (duración optimista)
#             pes (duración pesimista)
#
# Valor de retorno: unif (número aleatorio)
#----------------------------------------------------------- 

def generaAleatoriosUniforme(op, pes):
        #print "\n *** Uniform(",op,pes,")"
        unif=random.uniform(op,pes)
        return unif

#******************************************************************
#-----------------------------------------------------------
# Generación de un número aleatorio para una 
#          distribución beta
#
# Parámetros: op (duración optimista)
#             pes (duración pesimista)
#             shape_a (shape factor)
#             shape_b (shapa factor)
#
# Valor de retorno: beta (número aleatorio)
#----------------------------------------------------------- 

def generaAleatoriosBeta(op, pes, shape_a, shape_b):
        #mean, stdev, shape_a, shape_b=self.datosBeta(op, mode, pes)
   #print "Mean=", mean, "Stdev=", stdev
   #print "shape_a=", shape_a, "shape_b=", shape_b
   #for i in range(n):
      beta=random.betavariate(shape_a,shape_b)*(pes-op) + op
      return beta

#*******************************************************************
#-----------------------------------------------------------
# Obtención de datos necesarios para la generación de 
#          números aleatorios para una distribución beta
#
# Parámetros: op (duración optimista)
#             mode (duración más problable)
#             pes (duración pesimista)
#
# Valor de retorno:  mean (duración media)
#                    stdev (desviación tí­pica)
#                    shape_a (shape factor)
#                    shape_b (shape factor)
#----------------------------------------------------------- 

def datosBeta(op, mode, pes):
        #print "\n *** Beta(",op,mode,pes,")"
      mean  = (op + 4*mode + pes) / 6.0
      stdev = (pes - op) / 6.0
      shape_a = ((mean - op) / (pes-op)) * ((mean-op)*(pes-mean)/stdev**2 - 1)
      shape_b = ((pes-mean)/(mean-op)) * shape_a

      return mean, stdev, shape_a, shape_b

#******************************************************************
#-----------------------------------------------------------
# Generación de un número aleatorio para una 
#          distribución triangular
#
# Parámetros: op (duración optimista)
#             mode (duración más problable)
#             pes (duración pesimista)
#
# Valor de retorno: triang (número aleatorio)
#----------------------------------------------------------- 

def generaAleatoriosTriangular(op, mode, pes):
      #print "\n *** Triangle(",op,mode,pes,")"
      """
      Generates a random number in a triangular distribution in [op, pes]
      with mode
      """
      unif = random.random()  #[0,1]
        
      if unif <= (mode-op) / (pes-op):
         aux = unif * (pes-op) * (mode-op)
         triang = op + math.sqrt(aux)
      else:
         aux = (pes-op) * (pes-mode) * (1-unif)
         triang = pes - math.sqrt(aux)

      return triang

#*******************************************************************
#-----------------------------------------------------------
# Generación de un número aleatorio para una 
#          distribución normal
#
# Parámetros: mean (duración media)
#             stdev (desviación tí­pica)
#
# Valor de retorno: norm (número aleatorio)
#----------------------------------------------------------- 

def generaAleatoriosNormal(mean, stdev):
         #print "\n *** Normal(",mean,stdev,")"
      norm=random.gauss(mean,stdev)
      return norm

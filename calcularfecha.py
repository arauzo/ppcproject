#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import pygtk
pygtk.require("2.0")
from datetime import date, timedelta, datetime
from xml.dom import minidom
import gtk
import gtk.glade
import glob
import string

transDay = {'LUN' : 0, 'MAR' : 1, 'MIE' : 2, 'JUE' : 3, 'VIE' : 4, 'SAB' : 5, 'DOM' : 6}

# Calcula la fecha de finalización del proyecto
def calcularFinProyecto(fechaComienzo, duracion, noLaborables=(), laborables=()):
    semanas, dias = divmod(duracion, len(laborables))
    resultado = fechaComienzo + timedelta(weeks=semanas)
    diasFestivos = len([h for h in noLaborables if h >= fechaComienzo and h <= resultado])
    dias = dias + diasFestivos - 1  # Se le resta 1 porque en el día de inicio se consume un día de trabajo
    for i in range(dias):
        resultado += timedelta(days=1)
        while resultado in noLaborables or resultado.weekday() not in laborables:
            resultado += timedelta(days=1)
    return resultado

# Obtiene el contenido de las etiquetas especificadas por xmlTag y xmlTag2
def buscaXMLTag(xmlFile,xmlTag,xmlTag2):
    resultList = []
    resultList2 = []

    try:
        dom = minidom.parse(xmlFile)
        elements = dom.getElementsByTagName(xmlTag)
        elements2 = dom.getElementsByTagName(xmlTag2)

        if len(elements) != 0:
            for i in range(0,len(elements)):
                resultList.extend([elements[i].childNodes[0].nodeValue])

        if len(elements2) != 0:
            for i in range(0,len(elements2)):
                resultList2.extend([elements2[i].childNodes[0].nodeValue])
        else:
            print 'Error - No hay elementos en el fichero XML con la etiqueta ' + xmlTag

    except:
        print 'Error - El fichero no existe o está mal formado.'

    return resultList, resultList2

# Función que obtiene los valores numéricos que corresponden con los días laborables
def calcularDiasLaborables(diasLaborables):
    resultado = []

    for diaLaboral in diasLaborables:
        resultado.append(transDay[diaLaboral])
    return resultado

# Clase de la ventana principal del programa
class MainWin:
    
    def __init__(self):
        self.widgets = gtk.glade.XML("calcularfecha.glade")
        signals = { "on_calcular_clicked" : self.on_calcular_clicked,
                    "gtk_main_quit" : gtk.main_quit }     
        self.widgets.signal_autoconnect(signals)
        
        # Widgets
        self.entradaDuracion = self.widgets.get_widget("duracion")
        self.comboCalendario = self.widgets.get_widget("comboCalendario")
        self.calendario = self.widgets.get_widget("calendario")

        # Marcar dia actual en el calendario
        today = date.today()
        self.calendario.select_month(today.month - 1, today.year)
        self.calendario.select_day(today.day)

        calendarios = glob.glob("calendarios/*.cal")  # Se obtienen los ficheros de calendarios (carpeta "calendarios")    
        store=gtk.ListStore(str)
        store.append(["Elige un calendario"])
        for calendario in calendarios:
            store.append([calendario[12:-4]])   # se añade al ListStore
        self.comboCalendario.set_model(store)   # Modelo del comboBox
         
        self.comboCalendario.set_active(0)  # El valor por defecto es "Elige un calendario"

    # Muestra el resultado en un cuadro de diálogo
    def mostrarResultado(self, resultado):
        resultadoTexto = "Día de finalización: " + resultado.strftime("%d/%m/%Y")
        dialogo = gtk.MessageDialog(parent=None, flags=0, buttons=gtk.BUTTONS_OK)
        label = gtk.Label(resultadoTexto)
        dialogo.vbox.pack_start(label, True, True, 0)
        dialogo.show_all()
        dialogo.run()
        dialogo.destroy()

    # Función que se ejecuta al pulsar el botón "Calcular"
    def on_calcular_clicked(self, widget):
        (anio, mes, dia) = self.calendario.get_date()

        fechaComienzo = date(int(anio), int(mes + 1), int(dia))  # Fecha de comienzo del proyecto

        # Valor del comboBox
        model = self.comboCalendario.get_model()
        index = self.comboCalendario.get_active()
        rutaCalendario = "calendarios/" + model[index][0] + ".cal"  # Ruta del calendario

        diasLaborables, diasFestivos = buscaXMLTag(rutaCalendario,'laboral','noLaboral')  # Busca los días laborables (días de la semana) y los días no laborables (fecha de festivos)

        diasLaborables = calcularDiasLaborables(diasLaborables)
        
        listaFestivos = []

        for diaFestivo in diasFestivos:
            temp = datetime.strptime(diaFestivo,"%d-%m-%Y")
            listaFestivos.append(temp.date())

        resultado = calcularFinProyecto(fechaComienzo, int(self.entradaDuracion.get_text()), listaFestivos, tuple(diasLaborables))

        self.mostrarResultado(resultado)

if __name__ == "__main__":
    MainWin()
    gtk.main()


#! /usr/bin/env python
# -*- coding: UTF-8 -*-

# Importamos el módulo pygtk y le indicamos que use la versión 2
import pygtk
pygtk.require("2.0")

# Luego importamos el módulo de gtk y el gtk.glade, este ultimo que nos sirve
# para poder llamar/utilizar al archivo de glade
import gtk
import gtk.glade

# Creamos la clase de la ventana principal del programa
class MainWin:
    
    def __init__(self):
        # Le decimos a nuestro programa que archivo de glade usar (puede tener
        # un nombre distinto del script). Si no esta en el mismo directorio del
        # script habría que indicarle la ruta completa en donde se encuentra
        self.widgets = gtk.glade.XML("ejemplo1.glade")
        
        # Creamos un pequeño diccionario que contiene las señales definidas en
        # glade y su respectivo método (o llamada)
        signals = { "on_entry1_activate" : self.on_button1_clicked,
                    "on_button1_clicked" : self.on_button1_clicked,
                    "gtk_main_quit" : gtk.main_quit }
        
        # Luego se auto-conectan las señales.
        self.widgets.signal_autoconnect(signals)
        # Nota: Otra forma de hacerlo es No crear el diccionario signals y
        # solo usar "self.widgets.signal_autoconnect(self)" -->Ojo con el self
        
        # Ahora obtenemos del archivo glade los widgets que vamos a
        # utilizar (en este caso son label1 y entry1)
        self.label1 = self.widgets.get_widget("label1")
        self.entry1 = self.widgets.get_widget("entry1")
        
    # Se definen los métodos, en este caso señales como "destroy" ya fueron
    # definidas en el .glade, así solo se necesita definir "on_button1_clicked"
    def on_button1_clicked(self, widget):
        texto = self.entry1.get_text()
        self.label1.set_text("Hola %s" % texto)

# Para terminar iniciamos el programa
if __name__ == "__main__":
    MainWin()
    gtk.main()

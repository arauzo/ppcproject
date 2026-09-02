# Manual de ejecucion de PPCProject con CRO-SL

Este documento resume los pasos necesarios para ejecutar la version de PPCProject incluida en el TFG y utilizar el algoritmo CRO-SL integrado para nivelacion de recursos.

## 1. Requisitos

La aplicacion se ha probado en Windows utilizando el entorno MSYS2 MinGW64. Se recomienda ejecutar PPCProject desde ese entorno para disponer de Python, GTK 3 y las librerias graficas necesarias.

Requisitos principales:

- Windows 10 o superior.
- MSYS2 con entorno MinGW64.
- Python instalado dentro de MSYS2 MinGW64.
- GTK 3 disponible para Python mediante PyGObject.
- Paquetes Python utilizados por la aplicacion: `numpy`, `scipy`, `matplotlib`, `namedlist` y dependencias habituales de GTK.
- Graphviz, opcional, si se desea generar o visualizar algunos grafos PERT mediante herramientas externas.

## 2. Instalacion orientativa de dependencias

Desde la terminal MSYS2 MinGW64 se pueden instalar paquetes mediante `pacman`. Los nombres exactos pueden depender de la instalacion local, pero habitualmente se necesitan paquetes equivalentes a:

```bash
pacman -S mingw-w64-x86_64-python
pacman -S mingw-w64-x86_64-python-gobject
pacman -S mingw-w64-x86_64-gtk3
pacman -S mingw-w64-x86_64-python-numpy
pacman -S mingw-w64-x86_64-python-scipy
pacman -S mingw-w64-x86_64-python-matplotlib
```

Si un paquete no esta disponible mediante `pacman`, puede instalarse en un entorno virtual de Python. En instalaciones recientes de MSYS2 puede aparecer el aviso `externally-managed-environment` si se intenta usar `pip` directamente sobre el Python del sistema.

Para `namedlist`, si no existe paquete de `pacman`, puede instalarse con `pip` en un entorno virtual o, bajo responsabilidad del usuario, con la opcion indicada por el propio mensaje de error de Python.

## 3. Ejecucion de PPCProject

La forma mas segura de ejecutar la aplicacion es abrir una terminal MSYS2 MinGW64, situarse en la carpeta del proyecto y lanzar el fichero principal:

```bash
cd /ruta/a/ppcproject-master-entrega
python ppcproject.py
```

En Windows tambien se incluye el fichero:

```text
run_ppcproject.bat
```

Este fichero cambia el directorio actual a la carpeta del proyecto y ejecuta `ppcproject.py` con Python. Si la ventana se abre y se cierra inmediatamente, conviene ejecutar el programa desde una terminal para poder leer el mensaje de error.

## 4. Carga de un proyecto

Una vez abierta la aplicacion:

1. Pulsar `Abrir` o acceder a `File > Open`.
2. Seleccionar una instancia de proyecto, por ejemplo un fichero `.sm` dentro de `examples/Elmaghraby`.
3. Comprobar que se cargan las actividades, duraciones, precedencias y recursos.
4. Si procede, visualizar el grafo PERT, la matriz de Zaderenko o el diagrama de Gantt.

## 5. Ejecucion del algoritmo CRO-SL

Para ejecutar la nivelacion de recursos con CRO-SL:

1. Abrir un proyecto con actividades y recursos definidos.
2. Acceder a la ventana de nivelacion/asignacion desde la interfaz.
3. En el selector de algoritmo, elegir `CRO-SL`.
4. Configurar los parametros principales:
   - Numero de generaciones.
   - Numero de ejecuciones.
   - Dimensiones del arrecife `N x M`.
   - `r_0`: ocupacion inicial del arrecife.
   - `f_b`: fraccion de broadcast spawning.
   - `r_l`: tasa de larvas aleatorias.
   - `f_a`: reproduccion asexual/brooding.
   - `f_d`: fraccion de depredacion.
   - `p_d`: probabilidad de depredacion.
   - Recursos a optimizar, si se desea optimizar solo un subconjunto. Por ejemplo: `R1` o `R1,R3`.
5. Pulsar `Ejecutar`.
6. Esperar a que finalice la ejecucion.

Al terminar, la interfaz actualiza:

- Mejor varianza encontrada.
- Recursos optimizados.
- Mejor generacion.
- Tiempo de ejecucion.
- Duracion critica y duracion permitida.
- Tasa de asentamiento de larvas.
- Diagrama de Gantt resultante.
- Grafica de cargas de recursos.

## 6. Ficheros de salida

Los resultados generados por CRO-SL se almacenan en la carpeta:

```text
crosl_results/
```

Los ficheros principales son:

- `crosl_generation_history_*.csv`: evolucion por generacion.
- `crosl_population_history_*.csv`: individuos de la poblacion por ejecucion y generacion.
- `crosl_elite_seeds.csv`: semillas de elite reutilizables en ejecuciones posteriores.

En esta copia de entrega la carpeta se incluye vacia, salvo un fichero informativo, para evitar adjuntar historicos pesados generados durante las pruebas.

## 7. Scripts experimentales

Ademas de la ejecucion desde interfaz, se incluyen scripts para reproducir pruebas experimentales:

```bash
python run_crosl_factorial_tests.py e402.sm
python summarize_crosl_factorial_results.py crosl_results/factorial_tests
```

El primero ejecuta combinaciones de parametros del algoritmo. El segundo resume resultados factoriales ya generados.

## 8. Errores frecuentes

### La ventana se abre y se cierra inmediatamente

Ejecutar desde terminal para ver el error:

```bash
python ppcproject.py
```

Si se usa `.bat`, comprobar que contiene `pause` al final para que la ventana no se cierre.

### `ValueError: Namespace Gtk not available`

GTK 3 no esta disponible para Python. Instalar los paquetes de GTK/PyGObject en MSYS2 MinGW64.

### `ModuleNotFoundError: No module named 'namedlist'`

Falta la dependencia `namedlist`. Instalarla en el entorno Python usado por PPCProject.

### `python: command not found`

La terminal no esta usando el entorno correcto. Abrir `MSYS2 MinGW64` y comprobar:

```bash
which python
python --version
```

### Problemas con rutas que contienen espacios o tildes

Usar comillas al ejecutar rutas completas o situarse previamente en la carpeta del proyecto con `cd`.

### No se generan CSV

Comprobar que existe la carpeta `crosl_results` y que la aplicacion tiene permisos de escritura en la carpeta del proyecto.

## 9. Recomendacion para el tribunal

Para una comprobacion rapida, se recomienda:

1. Abrir una instancia pequeña, por ejemplo `examples/Elmaghraby/e402.sm`.
2. Ejecutar CRO-SL con parametros por defecto.
3. Comprobar que aparece el resumen de varianza y que se actualizan el Gantt y la grafica de recursos.
4. Revisar que se generan ficheros CSV en `crosl_results`.

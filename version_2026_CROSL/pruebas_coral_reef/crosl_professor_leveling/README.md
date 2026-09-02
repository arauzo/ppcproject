# CRO-SL profesor adaptado a nivelacion

Esta carpeta contiene una adaptacion del esquema CRO-SL proporcionado por el profesor al problema de nivelacion de recursos.

## Configuracion recomendada

La configuracion recomendada esta en `recommended_config.py`:

```text
generaciones: 100
tamano del arrecife por substrato: 8 x 8
elitismo: 0.05
p_0: 0.7
f_b: 0.7
r_l: 0.1
f_a: 0.1
f_d: 0.2
p_d: 0.15
k: 3
broadcast_mutation: False
similarity_check_interval: 10
similarity_threshold: 0.5
reset_keep_rate: 0.05
infeasibility_penalty: 1000000.0
pyramidal_search: False
pyramid_step: 10
pyramid_increment_n: 2
pyramid_increment_m: 2
initialization_file: None
elite_file: None
```

Esta configuracion se fija tras comparar:

- CRO-SL con elitismo frente a CRO-SL sin elitismo.
- CRO-SL adaptado frente a simulated annealing usando la misma funcion objetivo.

La funcion objetivo es la suma de varianzas de carga de los recursos, manteniendo fija la duracion del proyecto.

## Codificacion del individuo

Cada individuo almacena el tiempo de inicio de cada actividad:

```text
actividad -> tiempo_inicio
```

La generacion inicial sigue la propuesta del profesor:

1. Se calculan los caminos del proyecto.
2. Se identifican los caminos no criticos.
3. Para cada camino no critico se calcula su margen.
4. Ese margen se reparte aleatoriamente entre actividades del camino.
5. Si una actividad aparece en varios caminos, se conserva el retraso compatible y se repara el calendario para respetar precedencias.

## Substratos activos

```text
OX+Switch / TWORS
OX+Switch / TWORS+Exchange
Switch+PMX / Dept_swap
Cycle+PMX / Invert+Dept_swap
```

La parte izquierda de `/` indica operadores de cruce y la parte derecha indica mutaciones.

## Flujo CRO-SL

El ciclo actual sigue mas de cerca el codigo original del profesor:

1. `broadcast_spawning`: selecciona padres de cada capa, aplica los cruces del substrato y genera larvas sexuales.
2. `brooding`: los corales no seleccionados para cruce generan larvas por mutacion.
3. `random larvae`: se crean larvas aleatorias adicionales segun `r_l`.
4. `larvae_setting`: las larvas intentan asentarse en el arrecife durante `k` intentos.
5. `asexual_reproduction`: los mejores corales se clonan y mutan.
6. `depredation`: una fraccion de los peores corales puede eliminarse.
7. `elitism`: se conserva una elite global para no perder las mejores soluciones.
8. `similarity_check/reset_layer`: cada cierto numero de generaciones se reinician capas demasiado parecidas, manteniendo una pequena fraccion de los mejores corales.

## Mecanismos opcionales

- El elitismo filtra duplicados por la firma de tiempos de inicio del individuo, para conservar soluciones distintas.
- La penalizacion por infeasibilidad es defensiva: si una solucion reparada siguiera violando precedencias, ventanas temporales o duracion del proyecto, su fitness recibe una penalizacion alta.
- La busqueda piramidal esta disponible con `--pyramidal-search`, pero queda desactivada por defecto porque aumenta el tamano del arrecife y puede alargar mucho los experimentos.
- La elite puede guardarse y reutilizarse con `--elite-file`. Tambien puede pasarse un CSV de arranque con `--initialization-file`.
- La ejecucion individual exporta cargas por recurso y varianza por recurso para analizar la nivelacion obtenida.

## Ejecucion individual

Desde `pruebas_coral_reef`:

```bash
python test_run_crosl_professor_leveling.py e801.sm
```

Con guardado de elite:

```bash
python test_run_crosl_professor_leveling.py e801.sm --elite-file elite_e801.csv
```

Reutilizando una elite previa:

```bash
python test_run_crosl_professor_leveling.py e801.sm --initialization-file elite_e801.csv
```

## Ejecucion batch

```bash
python test_compare_professor_crosl_leveling_batch.py "/c/Users/Alvaro/Desktop/TFG/ppcproject-master/examples/Elmaghraby"
```

## Comparacion con annealing

```bash
python test_compare_professor_crosl_vs_annealing_leveling_batch.py "/c/Users/Alvaro/Desktop/TFG/ppcproject-master/examples/Elmaghraby"
```

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load, save, import and export files with project related data.
Compatible with Python 3.
"""

import os.path
import pickle


def load_with_some_format(filename, formats):
    extension = os.path.splitext(filename)[1][1:].lower()

    for file_format in formats:
        if extension in file_format.filenameExtensions:
            try:
                data = file_format.load(filename)
                if data is not None:
                    return data
            except Exception:
                continue

    for file_format in formats:
        try:
            data = file_format.load(filename)
            if data is not None:
                return data
        except Exception:
            continue

    return None


class ProjectFileFormat(object):
    def __init__(self):
        self.filenameExtensions = []

    def filenamePatterns(self):
        return ['*.' + ext for ext in self.filenameExtensions]

    def __str__(self):
        return ''.join(['(', ', '.join(self.filenamePatterns()), ')'])

    def canLoad(self):
        return True

    def canSave(self):
        return False

    def load(self, filename):
        raise Exception('Virtual method')

    def save(self, data, filename):
        raise Exception('Virtual method')


class PSPProjectFileFormat(ProjectFileFormat):
    def __init__(self):
        super(PSPProjectFileFormat, self).__init__()
        self.filenameExtensions = ['sm']

    def canSave(self):
        return False

    def load(self, filename):
        with open(filename, mode='r', encoding='latin-1', errors='ignore') as f:
            lines = f.readlines()

        prelaciones = []
        asignaciones_raw = []
        resource_availabilities = []
        resource_names = []
        seccion = None

        for line in lines:
            upper_line = line.strip().upper()
            if not upper_line or upper_line.startswith('***'):
                continue

            if 'PRECEDENCE RELATIONS' in upper_line:
                seccion = 'PREL'
                continue

            if 'REQUESTS/DURATIONS' in upper_line:
                seccion = 'ASIG'
                continue

            if 'RESOURCEAVAILABILITIES' in upper_line:
                seccion = 'REC'
                continue

            parts = line.split()
            if not parts:
                continue

            if seccion == 'PREL':
                if parts[0].isdigit():
                    job_id = parts[0]
                    sucesores = parts[3:]
                    prelaciones.append((job_id, sucesores))

            elif seccion == 'ASIG':
                # Cabecera con nombres de recursos: R 1 R 2 ...
                if parts[0].lower() == 'jobnr.' and 'duration' in [p.lower() for p in parts]:
                    duration_index = [p.lower() for p in parts].index('duration')
                    resource_tokens = parts[duration_index + 1:]
                    resource_names = []
                    i = 0
                    while i < len(resource_tokens):
                        if resource_tokens[i].upper() == 'R' and i + 1 < len(resource_tokens):
                            resource_names.append('R' + resource_tokens[i + 1])
                            i += 2
                        else:
                            resource_names.append(resource_tokens[i])
                            i += 1
                    continue

                if parts[0].isdigit():
                    asignaciones_raw.append(parts)

            elif seccion == 'REC':
                # Cabecera: R 1 R 2 ...
                if parts[0].upper() == 'R':
                    resource_names = []
                    i = 0
                    while i < len(parts):
                        if parts[i].upper() == 'R' and i + 1 < len(parts):
                            resource_names.append('R' + parts[i + 1])
                            i += 2
                        else:
                            i += 1
                    continue

                # Disponibilidades
                if parts[0].isdigit():
                    resource_availabilities = parts

        # Sucesores
        sucs_dict = {}
        for job_id, sucesores in prelaciones:
            sucs_dict[int(job_id)] = [int(s) for s in sucesores if s.isdigit()]

        # Predecesores
        precedents_dict = {jid: [] for jid in sucs_dict.keys()}
        for jid, lista_sucesores in sucs_dict.items():
            for sucesor in lista_sucesores:
                if sucesor in precedents_dict:
                    precedents_dict[sucesor].append(jid)

        # Recursos
        resources = []
        if resource_names and resource_availabilities:
            for idx, resource_name in enumerate(resource_names):
                availability = ''
                if idx < len(resource_availabilities):
                    availability = str(resource_availabilities[idx])

                # Formato esperado por la app:
                # [nombre, tipo, disponibilidad renovable, disponibilidad no renovable]
                resources.append([resource_name, 'Renewable', availability, ''])

        # Actividades y asignaciones
        activities = []
        asignaciones = []

        for jid in sorted(sucs_dict.keys()):
            duracion = 0.0
            resource_consumption = []

            for row in asignaciones_raw:
                if int(row[0]) == jid:
                    duracion = float(row[2])
                    resource_consumption = row[3:]
                    break

            activities.append([
                None,
                jid,
                precedents_dict[jid],
                '',
                '',
                '',
                duracion,
                duracion * 0.2,
                'Normal',
            ])

            # Asignación recurso-actividad
            for idx, amount in enumerate(resource_consumption):
                if idx < len(resource_names):
                    try:
                        amount_value = float(amount)
                    except ValueError:
                        amount_value = 0.0

                    if amount_value != 0:
                        asignaciones.append([
                            str(jid),
                            str(resource_names[idx]),
                            str(amount_value),
                        ])


        return (activities, [], resources, asignaciones)


class PPCProjectFileFormat(ProjectFileFormat):
    def __init__(self):
        super(PPCProjectFileFormat, self).__init__()
        self.filenameExtensions = ['ppc']

    def canSave(self):
        return True

    def load(self, filename):
        with open(filename, 'rb') as f:
            return pickle.load(f, encoding='latin-1')

    def save(self, data, filename):
        with open(filename, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


PPCProjectOLDFileFormat = PPCProjectFileFormat


if __name__ == '__main__':
    pass

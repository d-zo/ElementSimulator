# -*- coding: utf-8 -*-
"""
programmsteuerung.py   v0.2
2023-09 Dominik Zobel
"""

# Copyright 2017-2023 Dominik Zobel.
# All rights reserved.
#
# This file is part of the ElementSimulator package.
# ElementSimulator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ElementSimulator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ElementSimulator. If not, see <http://www.gnu.org/licenses/>.


# -------------------------------------------------------------------------------------------------
def Umgebung_Vorbereiten(einstellungen, versuch, programm):
    """Pruefe die Existenz von Ordnern bzw. lege notwendige Ordner fuer die weitere Bearbeitung an.
    Prueft vorhandene Ordner und erstellt Hilfsordner. Gibt False zurueck, wenn benoetigte Ordner
    nicht vorhanden sind (andernfalls True).
    """
    import os
    import time

    if (not os.path.isdir('utilities')):
        print('# Abbruch: Benoetigter Ordner utilities nicht vorhanden')
        return False

    # Einen Absolutpfad zu arbeitsordner und bezugsordner ermitteln, so dass beide als vollwertige
    # Quellen/Ziele fuer zukuenftige Zugriffe genutzt werden koennen
    arbeitsordner = os.path.abspath(time.strftime('%Y%m%d%H%M%S') + '_' + versuch.capitalize())
    einstellungen.update([('arbeitsordner', arbeitsordner)])
    os.makedirs(arbeitsordner)

    bezugsordner = os.getcwd()
    einstellungen.update([('bezugsordner', bezugsordner)])

    if (not os.path.isdir('output')):
        os.makedirs('output')

    return True



# -------------------------------------------------------------------------------------------------
def _Relevante_Materialroutinen_Bereitstellen(zielendung='.f'):
    """Durchsucht die Ordner UMAT, VUMAT und XMAT im Hauptverzeichnis nach Fortran-Routinen
    (.f-Dateien). Weitere Unterordner werden ignoriert. Kopiert die Routinen ins aktuelle
    Arbeitsverzeichnis und modifiziert ggfs. den Namen. Gibt eine Liste der gefundenen Eintraege in
    dem Muster (modifizierter Routinename, Originalname, Bezeichnung) zurueck.
    """
    import os
    from shutil import copy

    ordnerliste = ['../UMAT', '../VUMAT', '../XMAT']
    materialroutinen = []
    for suchordner in ordnerliste:
        for aktueller_ordner, unterordner, dateiliste in os.walk(suchordner):
            if (aktueller_ordner != suchordner):
                continue

            for datei in dateiliste:
                if (datei[-2:] != '.f'):
                    continue
                # Modifiziere den (neuen) Dateinamen und den Ordnernamen fuer die Rueckgabe
                modname = datei[:-2].replace('.', '')
                materialroutinen += [(modname, datei, aktueller_ordner[3:].capitalize())]
                zieldatei = modname + zielendung
                if (os.path.isfile(zieldatei)):
                    print('# Warnung: Datei existiert bereits (wird ueberschrieben).' \
                        + ' Alle Routinen sollten unterschiedliche Namen haben')

                copy(aktueller_ordner + os.sep + datei, zieldatei)

    return materialroutinen



# -------------------------------------------------------------------------------------------------
def _Ergebnisse_Kopieren(bezugsordner):
    """Kopiere alle Ergebnisse in csv- und png-Dateien aus dem aktuellen Arbeitsverzeichnis in
    das Ausgabeverzeichnis.
    """
    import os
    from shutil import copy

    print('# Kopiere Dateien ins Ausgabeverzeichnis')
    dateiliste = os.listdir('.')
    for datei in dateiliste:
        if ((datei[-4:] == '.csv') or (datei[-4:] == '.png') or (datei[-4:] == '.pdf')):
            copy(datei, bezugsordner + os.sep + 'output' + os.sep)



# -------------------------------------------------------------------------------------------------
def _Programmaufruf_Intern_Verarbeiten(einstellungen, optionen, routinennamen):
    """Leitet den Aufruf an die entsprechenden Unterfunktionen und -programme weiter und fuehrt alle
    notwendigen Operationen durch. Wenn alles erfolgreich ausgefuehrt werden kann und auch anhand der
    uebergebenen optionen der arbeitsordner hiernach geloescht werden soll, wird True zurueckgegeben.
    Aansonsten - wenn der Ordner behalten werden soll - False.
    """
    from .aufrufabaqus import Abaqus_Dateivorbereitung, Abaqus_CAE_Joberstellung, Abaqus_Simulation
    from .aufruffortran import Fortran_Dateivorbereitung, Fortran_Kompilieren, Fortran_Simulation
    from .aufrufhilfen import Reihenfolge_Anpassen
    from .plotausgabe import Plot_Ergebnisse

    programm = optionen['prog']

    print('\n------------------------------')
    print('# 1)   V O R B E R E I T U N G\n')

    # a) Dateien Kopieren und Variablen ersetzen
    if (programm == 'fortran'):
        dateien_und_routinen = Fortran_Dateivorbereitung(einstellungen=einstellungen,
            optionen=optionen, routinennamen=routinennamen)
    elif (programm == 'abaqus'):
        dateien_und_routinen = Abaqus_Dateivorbereitung(einstellungen=einstellungen,
            optionen=optionen, routinennamen=routinennamen)

    if (len(dateien_und_routinen) == 0):
        print('# Warnung: Vorbereitung der ' + programm.capitalize() \
            + '-Skriptdateien fehlgeschlagen')
        return False

    dateien_und_routinen, ausgabenamen = Reihenfolge_Anpassen(einstellungen=einstellungen,
        dateien_und_routinen=dateien_und_routinen)

    # b) Vorkompilieren bzw. final ausführbare Dateien erstellen
    if (programm == 'fortran'):
        erfolgreiche_vorbereitung = Fortran_Kompilieren(einstellungen=einstellungen,
            optionen=optionen, dateien_und_routinen=dateien_und_routinen)
        nachricht_dateien = 'vorkompilierten Fortran-Dateien'
    elif (programm == 'abaqus'):
        erfolgreiche_vorbereitung = Abaqus_CAE_Joberstellung(einstellungen=einstellungen,
            dateien_und_routinen=dateien_und_routinen)
        nachricht_dateien = 'Abaqus-Inputdateien'

    if (not erfolgreiche_vorbereitung):
        print('# Warnung: Erzeugen der ' + nachricht_dateien + ' fehlgeschlagen')
        return False

    if (optionen['zusatz'] == 'nurvorbereiten'):
        print('# Alles erfolgreich vorbereitet')
        return False

    print('\n--------------------------')
    print('# 2)   S I M U L A T I O N\n')

    if (programm == 'fortran'):
        erfolgreiche_simulation, plotdateien = Fortran_Simulation(einstellungen=einstellungen,
            dateien_und_routinen=dateien_und_routinen)
    elif (programm == 'abaqus'):
        erfolgreiche_simulation, plotdateien = Abaqus_Simulation(einstellungen=einstellungen,
            dateien_und_routinen=dateien_und_routinen)

    ordner_entfernen = True
    if (not erfolgreiche_simulation):
        # Nur Warnung ausgeben, aber trotzdem fortsetzen, wenn mindestens eine Simulation erfolgreich
        # war (plotdateien != [])
        print('# Warnung: Mindestens eine Simulation konnte nicht fehlerfrei ausgefuehrt werden')
        ordner_entfernen = False

    print('\n--------------------------------')
    print('# 3)   N A C H B E R E I T U N G\n')

    if (optionen['zusatz'] != 'keinplot'):
        if (not Plot_Ergebnisse(dateien=plotdateien, namen=ausgabenamen, aktuellertest=optionen['test'],
            programm=programm.capitalize(), einstellungen=einstellungen)):
            print('# Warnung: Beim Plotten der Ergebnisse ist ein Fehler aufgetreten')
            return False

    _Ergebnisse_Kopieren(bezugsordner=einstellungen['bezugsordner'])

    if (optionen['zusatz'] == 'ordnerbehalten'):
        return False
    else:
        return ordner_entfernen



# -------------------------------------------------------------------------------------------------
def Programmaufruf_Verarbeiten(einstellungen, optionen):
    """Wechselt in das Arbeitsverzeichnis und laesst alle notwendigen Operationen durchfuehren. Am
    Ende der Bearbeitung wird wieder in das Verzeichnis gewechselt, aus dem der Aufruf kam.
    """
    import os
    import shutil

    bezugsordner = einstellungen['bezugsordner']
    arbeitsordner = einstellungen['arbeitsordner']
    os.chdir(arbeitsordner)

    routinennamen = _Relevante_Materialroutinen_Bereitstellen(zielendung=einstellungen['Fortran']['Endung'])
    if (routinennamen == []):
        print('# Abbruch: Keine Routinen ausgewaehlt/verfuegbar')
        loesche_arbeitsverzeichnis = True
    else:
        loesche_arbeitsverzeichnis = _Programmaufruf_Intern_Verarbeiten(einstellungen=einstellungen,
            optionen=optionen, routinennamen=routinennamen)

    os.chdir(bezugsordner)
    if (loesche_arbeitsverzeichnis):
        try:
            shutil.rmtree(arbeitsordner)
        except OSError:
            print('# Warnung: Arbeitsverzeichnis ' + arbeitsordner + ' konnte nicht geloescht werden')



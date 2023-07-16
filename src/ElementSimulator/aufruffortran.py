# -*- coding: utf-8 -*-
"""
aufruffortran.py   v0.1
2019-12 Dominik Zobel
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
def Fortran_Dateivorbereitung(einstellungen, optionen, routinennamen):
   """Bereite die Fortran-Quelldateien vor, d.h. ersetze Platzhalter mit sinnvollen Werten, damit
   alle Eingabedateien anschliessend kompiliert und ausgefuehrt werden koennen. Je nach gewaehlten
   einstellungen und optionen werden mehrere Dateien (fuer mehrere Routinen) erzeugt.
   Gibt None bei Fehlern zurueck oder eine Liste von Eintraegen mit dem Muster
   (dateiname, routine, routinentyp).
   """
   import os
   from shutil import copy
   from .aufrufhilfen import Muster_Ersetzen
   from .parameter import Ersatzwerte_Zuweisen
   #
   # FIXME: Fuer jede Routine in eigenen Ordner
   # Im Ordner utilities/fort werden alle Dateien erwartet, die fuer ein Kompilieren direkt in
   # Fortran benoetigt werden. Kopiere alle Dateien ins arbeitsverzeichnis
   fort_utilities = einstellungen['bezugsordner'] + os.sep + 'utilities' + os.sep + 'fort' + os.sep
   for datei in os.listdir(fort_utilities):
      copy(fort_utilities + datei, '.')
   #
   dateien_und_routinen = []
   for routine, originalname, routinentyp in routinennamen:
      zuordnung = Ersatzwerte_Zuweisen(einstellungen=einstellungen, prog=optionen['prog'],
         routine=originalname, zusatz='_dp')
      programmdatei = routine.capitalize() + '_' + optionen['test'].capitalize() + '_' \
         + optionen['prog'].capitalize()
      dateien_und_routinen += [(programmdatei, originalname)]
      #
      zuordnung.update([('--outfilename--', programmdatei)])
      Muster_Ersetzen(eingabedatei=einstellungen['bezugsordner'] + os.sep + 'utilities' + os.sep \
         + routinentyp + '_' + optionen['test'].capitalize() + '.f', \
         ausgabedatei=programmdatei + '.f', zuordnung=zuordnung)
   #
   return dateien_und_routinen
#


# -------------------------------------------------------------------------------------------------
def Fortran_Kompilieren(einstellungen, optionen, dateien_und_routinen):
   """Kompiliert die uebergebene datei mit der dazugehoerigen routine vom Typ routinentyp.
   Die richtigen Compileroptionen werden aus den einstellungen ermittelt. Es wird eine ausfuehrbare
   Datei (mit aktuellertest im Namen) erstellt. Gibt True zurueck, wenn alles erfolgreich kompiliert
   werden kann, ansonsten False.
   """
   import os
   from .programmausfuehrung import Programmausfuehrung
   #
   system = einstellungen['System']
   if (system == 'win'):
      arg_start = ' /'
   else:
      arg_start = ' -'
   #
   aktuellertest = optionen['test']
   compiler = einstellungen['Fortran']['Compiler']
   argumente_dateien = einstellungen['Fortran']['Compiler Argumente']
   #
   erfolgreich = True
   prep_datei = 'preparation'
   for datei, routine in dateien_und_routinen:
      if (routine not in argumente_dateien):
         print('Abbruch: Kein Compiler-Argumente fuer Routine ' + routine + ' in Einstellungsdatei')
         erfolgreich = False
         break
      #
      argumente, abhaengigkeiten = argumente_dateien[routine]
      #
      print('# Kompilieren')
      #
      if (compiler == 'gfortran'):
         extraflags = ['ffree-form', 'cpp']
      else:
         extraflags = ['free', 'fpp']
      #
      befehl_routine = einstellungen['Befehle'][compiler] + arg_start + arg_start.join(argumente + ['o ']) \
         + datei + '.o' + ' ' + routine + ' ' + arg_start + 'c'
      if (not Programmausfuehrung(befehl=befehl_routine,
         nachricht_abbruch='Fehler beim Kompilieren der Routine ' + routine,
         nachricht_fehler='Kompilieren der Routine ' + routine + ' fehlgeschlagen')):
         erfolgreich = False
         print('Abbruch bei: ' + befehl_routine)
         continue
      #
      abh_liste = [prep_datei + '.o']
      befehl_routine = einstellungen['Befehle'][compiler] + arg_start \
         + arg_start.join(extraflags + argumente + ['o ']) + prep_datei + '.o' \
         + ' ' + prep_datei + '.f' + ' ' + arg_start + 'c'
      if (not Programmausfuehrung(befehl=befehl_routine,
         nachricht_abbruch='Fehler beim Kompilieren der Routine ' + routine,
         nachricht_fehler='Kompilieren der Routine ' + routine + ' fehlgeschlagen')):
         erfolgreich = False
         print('Abbruch bei: ' + befehl_routine)
         continue
      #
      for abh_datei in abhaengigkeiten:
         # FIXME: Harte Annahme, dass die Datei auf .f endet
         befehl_abh_datei = einstellungen['Befehle'][compiler] + arg_start \
            + arg_start.join(argumente + ['o ']) + abh_datei[:-2] + '.o ' \
            + abh_datei + arg_start + 'c'
         abh_liste += [abh_datei[:-2] + '.o']
         if (not Programmausfuehrung(befehl=befehl_abh_datei,
            nachricht_abbruch='Fehler beim Kompilieren der angegebenen Abhängigkeit ' + abh_datei,
            nachricht_fehler='Kompilieren der Abhängigkeit ' + abh_datei + ' fehlgeschlagen')):
            erfolgreich = False
            print('Abbruch bei: ' + befehl_abh_datei)
            break
      #
      abh_liste += [datei + '.o']
      befehl_eingabedatei = einstellungen['Befehle'][compiler] + arg_start \
         + arg_start.join(extraflags + argumente + ['o ']) + datei \
         + ' ' + ' '.join(abh_liste) + ' ' + datei + '.f'
      if (not Programmausfuehrung(befehl=befehl_eingabedatei,
         nachricht_abbruch='Fehler beim Kompilieren der Eingabedatei ' + datei,
         nachricht_fehler='Kompilieren der Eingabedatei ' + datei + ' fehlgeschlagen')):
         erfolgreich = False
         print('Abbruch bei: ' + befehl_eingabedatei)
         continue
      #

      print('# Entferne temporaere Fortran-Dateien')
      temp_dateien = os.listdir('.')
      for datei in temp_dateien:
         if (datei[-4:] == '.mod'):
            os.remove(datei)
   #
   return erfolgreich
#


# -------------------------------------------------------------------------------------------------
def Fortran_Simulation(einstellungen, dateien_und_routinen):
   """Ruft alle notwendigen Funktionen auf, um die Quelldateien fuer einen externen Fortran-Aufruf
   vorzubereiten, den Aufruf auszufuehren und die Ergebnisse auszuwerten.
   """
   import time
   from .programmausfuehrung import Programmausfuehrung
   #
   plotdateien = []
   laufzeiten = []
   erfolgreich = True
   for datei, routine in dateien_und_routinen:
      befehl = datei
      if (einstellungen['System'] == 'lnx'):
         befehl = './' + datei
      #
      startzeit = time.time()
      if (not Programmausfuehrung(befehl=befehl,
         nachricht_abbruch='Fehler beim Ausfuehren von Programm ' + datei,
         nachricht_fehler='Ausfuehren von Programm ' + datei + ' fehlgeschlagen')):
         erfolgreich = False
         continue
      #
      laufzeit = time.time() - startzeit
      # Die Fortran-Skripte geben selber eine Zeitmessung aus
      #print(datei + ':  ' + str(laufzeit) + 's')
      #
      plotdateien += [datei]
      laufzeiten += [laufzeit]
   #
   if (len(plotdateien) == 0):
      erfolgreich = False
   else:
      print('---\nZusammenfassung Laufzeiten (subprocess):')
      formatstring = '{:' + str(max([len(x) for x in plotdateien])) + 's}: {:7.3f}s'
      for idx in range(len(plotdateien)):
         print(formatstring.format(plotdateien[idx], laufzeiten[idx]))
      #
      print('---')
   #
   return [erfolgreich, plotdateien]
#

# -*- coding: utf-8 -*-
"""
aufrufabaqus.py   v0.3
2021-07 Dominik Zobel
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
def _Abaqus_Dateien_Anpassen(testname, eingangsroutine, zuordnung, bezugsordner):
   """Passt die Dateien fuer die Abaqus-Simulation an, d.h. Platzhalter werden mit sinnvollen Werten
   ersetzt, damit alle Eingabedateien anschliessend in Abaqus ausgefuehrt werden koennen.
   """
   import os
   from .aufrufhilfen import Muster_Ersetzen
   #
   util_pfad = bezugsordner + os.sep + 'utilities' + os.sep
   Muster_Ersetzen(eingabedatei=util_pfad + zuordnung['--routinetype--'] + '_' \
      + testname.capitalize() + '.py', ausgabedatei=zuordnung['--outfilename--'] + '.py',
      zuordnung=zuordnung)
   Muster_Ersetzen(eingabedatei=util_pfad + 'Auswertung_' + testname + '.py',
      ausgabedatei='Auswertung_' + zuordnung['--outfilename--'] + '.py', zuordnung=zuordnung)
   Muster_Ersetzen(eingabedatei=eingangsroutine, ausgabedatei=zuordnung['--userroutine--'],
      zuordnung=zuordnung)
#


# -------------------------------------------------------------------------------------------------
def Abaqus_Dateivorbereitung(einstellungen, optionen, routinennamen):
   """Bereite die Abaqus-Skripte vor, d.h. ersetze Platzhalter mit sinnvollen Werten, damit
   alle Eingabedateien anschliessend in Abaqus ausgefuehrt werden koennen. Je nach gewaehlten
   einstellungen und optionen werden mehrere Dateien (fuer mehrere Routinen) erzeugt.
   Gibt None bei Fehlern zurueck oder eine Liste von Eintraegen mit dem Muster
   (dateiname, routine, routinentyp).
   """
   import os
   from shutil import copy
   from .aufrufhilfen import Abaqus_Version
   from .parameter import Ersatzwerte_Zuweisen
   #
   endung = einstellungen['Fortran']['Endung']
   bezugsordner = einstellungen['bezugsordner']
   # FIXME: Fuer jede Routine in eigenen Ordner
   utilities_dir = einstellungen['bezugsordner'] + os.sep + 'utilities' + os.sep
   copy(utilities_dir + 'auswertungshilfe.py', '.')
   #
   fort_utilities = einstellungen['bezugsordner'] + os.sep + 'utilities' + os.sep + 'fort' + os.sep
   optionalcopies = [
      (fort_utilities + 'matplotlibrc_notex', 'matplotlibrc'),
      (fort_utilities + 'materialdaten.py', 'materialdaten.py')
   ]
   for srcfile, tgtfile in optionalcopies:
      try:
         copy(srcfile, tgtfile)
      except:
         pass
   #
   abaqus_version = Abaqus_Version(abaqus_basisaufruf=einstellungen['Befehle']['Abaqus'])
   einstellungen.update([('Abaqus', {'Version': abaqus_version})])
   #
   dateien_und_routinen = []
   for routine, originalname, routinentyp in routinennamen:
      zuordnung = Ersatzwerte_Zuweisen(einstellungen=einstellungen, prog=optionen['prog'],
         routine=originalname)
      #
      if (originalname not in einstellungen['Fortran']['Compiler Argumente'].keys()):
         continue
      #
      if any([(x == 'free' or x == 'ffree-form') for x in einstellungen['Fortran']['Compiler Argumente'][originalname][0]]):
         fortranformat = 'free'
      else:
         fortranformat = 'fixed'
      #
      # Aufruf jeweils in Bedingung, damit fuer Xmat auch zwei Aufrufe durchgefuehrt werden
      if ((routinentyp == 'Umat') or (routinentyp == 'Xmat')):
         ausgabedatei = routine
         if (routinentyp == 'Xmat'):
            ausgabedatei = routine + '_imp'
         #
         name_skriptdatei = ausgabedatei.capitalize() + '_' + optionen['test'].capitalize() + '_' \
            + optionen['prog'].capitalize()
         zuordnung.update([('--outfilename--', name_skriptdatei)])
         zuordnung.update([('--userroutine--', ausgabedatei + endung)])
         zuordnung.update([('--routinetype--', 'Implicit')])
         zuordnung.update([('--abaqustype--', 'ABQ_STD_CALLING')])
         #
         _Abaqus_Dateien_Anpassen(testname=optionen['test'].capitalize(),
            eingangsroutine=routine + endung, zuordnung=zuordnung, bezugsordner=bezugsordner)
         dateien_und_routinen += [(name_skriptdatei, ausgabedatei + endung, fortranformat)]
      #
      if ((routinentyp == 'Vumat') or (routinentyp == 'Xmat')):
         ausgabedatei = routine
         if (routinentyp == 'Xmat'):
            ausgabedatei = routine + '_exp'
         #
         name_skriptdatei = ausgabedatei.capitalize() + '_' + optionen['test'].capitalize() + '_' \
            + optionen['prog'].capitalize()
         zuordnung.update([('--outfilename--', name_skriptdatei)])
         zuordnung.update([('--userroutine--', ausgabedatei + endung)])
         zuordnung.update([('--routinetype--', 'Explicit')])
         zuordnung.update([('--abaqustype--', 'ABQ_EXP_CALLING')])
         #
         _Abaqus_Dateien_Anpassen(testname=optionen['test'].capitalize(),
            eingangsroutine=routine + endung, zuordnung=zuordnung, bezugsordner=bezugsordner)
         dateien_und_routinen += [(name_skriptdatei, ausgabedatei + endung, fortranformat)]
   #
   return dateien_und_routinen
#


# -------------------------------------------------------------------------------------------------
def Abaqus_CAE_Joberstellung(einstellungen, dateien_und_routinen):
   """Fuehre alle in dateien_und_routinen aufgelisteten Python-Skripte in Abaqus/CAE aus, um daraus
   Jobs in Form von Input-Dateien zu erstellen.
   """
   import os
   from .programmausfuehrung import Programmausfuehrung
   #
   erfolgreich = True
   for zieldatei, routine, fortranformat in dateien_und_routinen:
      if (not Programmausfuehrung(befehl=einstellungen['Befehle']['Abaqus'] + ' cae noGUI=' \
         + zieldatei + '.py', nachricht_abbruch='Fehler beim Erstellen der inp-Datei ' + zieldatei,
         nachricht_fehler='Erstellung der inp-Datei ' + zieldatei + ' fehlgeschlagen')):
         erfolgreich = False
         continue
      #
      if (not os.path.isfile(zieldatei + '.inp')):
         print('# Abbruch: inp-Datei existiert nicht')
         erfolgreich = False
         continue
   #
   return erfolgreich
#


# -------------------------------------------------------------------------------------------------
def Abaqus_Simulation(einstellungen, dateien_und_routinen):
   """Fuehre die eigentliche Simulation in Abaqus anhand der vorbereiteten Dateien aus
   dateien_und_routinen durch. Nach jeder Simulation werden mit Abaqus/CAE und einem Python-Skript
   die Ergebnisse aus den odb-Dateien extrahiert.
   """
   import os
   import time
   from shutil import copy
   from .programmausfuehrung import ABQ_Programmausfuehrung, Programmausfuehrung
   #
   plotdateien = []
   laufzeiten = []
   abaqus_basisaufruf = einstellungen['Befehle']['Abaqus']
   #
   erfolgreich = True
   for datei, routine, fortranformat in dateien_und_routinen:
      # Wenn eine Routine im free-Format vorliegt, muessen zusaetzliche Dateien mit Modifikationen
      # bereitgestellt (und nach dem Aufruf wieder entfernt) werden. Die .inc-Dateien werden immer
      # bereitgestellt, da manche Routinen sonst nicht kompilieren.
      pfad_extradatei = '../utilities' + os.sep \
         + 'abq' + einstellungen['Abaqus']['Version'] + '_' + einstellungen['System'] + os.sep
      extradateien = []
      if (os.path.isdir(pfad_extradatei)):
         for tempdatei in os.listdir(pfad_extradatei):
            if (fortranformat == 'fixed'):
               if (not tempdatei.endswith('.inc')):
                  continue
            #
            copy(pfad_extradatei + tempdatei, '.')
            extradateien += [tempdatei]
      #
      startzeit = time.time()
      if (not ABQ_Programmausfuehrung(befehl=abaqus_basisaufruf + ' job=' + datei \
         + ' user=' + routine + ' cpus=1 double interactive',
         nachricht_abbruch='Fehler beim Simulieren in Abaqus von ' + datei,
         nachricht_fehler='Simulieren von ' + datei + ' in Abaqus fehlgeschlagen',
         laufzeit=einstellungen['Global']['max. Laufzeit Abaqus [s]'])):
         erfolgreich = False
         continue
      #
      laufzeit = time.time() - startzeit
      print(datei + ':  ' + str(laufzeit) + 's')
      #
      for tempdatei in extradateien:
         os.remove(tempdatei)
      #
      if (not os.path.isfile(datei + '.odb')):
         print('# Abbruch: odb-Datei existiert nicht')
         erfolgreich = False
         continue
      #
      if (not Programmausfuehrung(befehl=abaqus_basisaufruf + ' cae noGUI=Auswertung_' + datei + '.py',
         nachricht_abbruch='Fehler beim Auswerten der odb-Datei ' + datei,
         nachricht_fehler='Auswertung der odb-Datei ' + datei + ' fehlgeschlagen')):
         erfolgreich = False
         continue
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

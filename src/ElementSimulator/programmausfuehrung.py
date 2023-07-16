# -*- coding: utf-8 -*-
"""
programmausfuehrung.py   v0.2
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
def Programmausfuehrung(befehl, nachricht_abbruch, nachricht_fehler):
   """Fuehrt mit dem uebergebenen befehl einen Systemaufruf durch. Wenn der Aufruf erfolgreich war,
   gibt die Funktion True zurueck, sonst False. Bei Misserfolg wird nachricht_abbruch ausgegeben,
   wenn der Rueckgabewert einer nicht erfolgreichen Ausfuehrung entspricht oder nachricht_fehler,
   wenn die Ausfuehrung selbst nicht erfolgreich war.
   """
   import subprocess
   #
   print('# ' + befehl)
   try:
      ergebnis = subprocess.run(befehl, shell=True, check=True)
   except subprocess.CalledProcessError:
      print('# Abbruch: ' + nachricht_abbruch)
      return False
   except:
      print('# Fehler: ' + nachricht_fehler)
      return False
   #
   if (ergebnis.returncode == 0):
      return True
   else:
      print('# Abbruch: Rueckgabewert ungleich Null')
      return False
#


# -------------------------------------------------------------------------------------------------
def ABQ_Programmausfuehrung(befehl, nachricht_abbruch, nachricht_fehler, laufzeit=600):
   """Erwartet als befehl einen Abaqus-Aufruf mit einer Option job=...
   Fuehrt wie Programmausfuehrung einen Systemaufruf durch, aber gibt dem Prozess nur eine
   maximale laufzeit (in Sekunden). Diese Funktion extrahiert den Jobnamen aus befehl und
   untersucht waehrend der Laufzeit, ob eine Datei <job>.sta vorhanden ist. Falls die Datei
   existiert, wird nach Schluesselbegriffen wie "error" oder "COMPLETED" gesucht, um zu ermitteln,
   ob ein Aufruf fehlgeschlagen ist und sich nicht automatisch beendet (v.a. in nicht offiziell
   unterstuetzen Linux-Distributionen wie Ubuntu moeglich).
   """
   import time
   import os
   import signal
   import subprocess
   #
   print('# ' + befehl)
   #
   befehlsteile = befehl.split()
   job = ''
   for tempjob in befehlsteile:
      if (tempjob[:4] == 'job='):
         job = tempjob[4:]
   #
   if (job == ''):
      print('# Abbruch: Konnte job=... aus dem Befehl nicht extrahieren')
      return False
   #
   statusdatei = job + '.sta'
   prozess = subprocess.Popen(befehl, shell=True)
   #prozess = subprocess.Popen(befehl.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   startzeit = time.time()
   inBearbeitung = False
   while (prozess.returncode == None):
      # Wenn die Simulation nach dieser Zeit noch immer laeuft, breche ab
      if (time.time()-startzeit >= laufzeit):
         print('# Abbruch: Simulation dauert laenger als ' + str(laufzeit) + 's und wird beendet')
         prozess.kill()
         try:
            prozess.communicate(timeout=5)
         except subprocess.TimeoutExpired:
            print('# Warnung: Prozess antwortet nicht')
            # Testing prozess.kill() instead of prozess.terminate() (3x): Should be the same in Windows, but different in Linux
            prozess.kill()
            os.kill(prozess.pid, signal.SIGTERM)
         #
         return False
      #
      if (not os.path.isfile(statusdatei)):
         continue
      #
      nachricht = ''
      with open(statusdatei, 'rb') as statuseingabe:
         statuseingabe.seek(os.SEEK_END)
         try:
            statuseingabe.seek(-50, os.SEEK_END)
            nachricht = ''.join([x.decode('utf-8') for x in list(statuseingabe)])
         except:
            pass
      #
      if ('COMPLETED SUCCESSFULLY' in nachricht):
         try:
            prozess.communicate(timeout=15)
         except subprocess.TimeoutExpired:
            print('# Hinweis: Toete scheinbar erfolgreiche Analyse, die sich nicht beendet')
            prozess.kill()
            try:
               prozess.communicate(timeout=5)
            except subprocess.TimeoutExpired:
               print('# Warnung: Prozess antwortet nicht')
               os.kill(prozess.pid, signal.SIGTERM)
         #
         return True
      elif ('error' in nachricht):
         print('# Hinweis: Simulation ist scheinbar fehlgeschlagen. Beende Prozess')
         prozess.kill()
         try:
            prozess.communicate(timeout=5)
         except subprocess.TimeoutExpired:
            print('# Warnung: Prozess antwortet nicht')
            os.kill(prozess.pid, signal.SIGTERM)
      # FIXME: Wenn die Ausgabe genutzt wird, kann der ganze Prozess blockiert werden
      #ausgabe = prozess.stdout.readline().decode('utf-8').rstrip()
      #if ((ausgabe != '') or (prozess.poll() is None)):
         #print(ausgabe)
#

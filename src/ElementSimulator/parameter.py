# -*- coding: utf-8 -*-
"""
parameter.py   v0.3
2023-01 Dominik Zobel
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


# Globale Variablen

referenzeinstellungen = {
   'Global': {
      'max. Iterationen': [],
      'Startzeit [s]': [],
      'Startinkrement [s]': [],
      'Abaqus Simulationsdauer [s]': [],
      'Anzahl Ausgaben Abaqus': [],
      'max. Laufzeit Abaqus [s]': []
   },
   'Fortran': {
      'Compiler': [],
      'Compiler Argumente': [],
   },
   'Ausgabe': {
      'Plotreihenfolge': []
   },
   'Material': {
      'Name': [],
      'Bezeichnung': [],
      'Anfangsporenzahl e_0 [-]': [],
      'Einbaudichte [g/cm^3]': [],
      'Winkel Grenzbedingung [Grad]': [],
      'Intergranulare Dehnung h [-]': [],
      'Intergr. Dehnung aktiv': [],
      'max. Anzahl Parameter': [],
      'max. Anzahl Statusvariablen': []
   },
   'Oedometerversuch': {
      'Probenhoehe [mm]': [],
      'Probenradius [mm]': [],
      'Druckverlauf [kPa]': []
   },
   'Triaxialversuch': {
      'Probenhoehe [mm]': [],
      'Probenradius [mm]': [],
      'max. Stauchung [%]': [],
      'max. Druck [kPa]': []
   },
   'Einfachscherversuch': {
      'Probenhoehe [mm]': [],
      'Probenradius [mm]': [],
      'max. seitliche Auslenkung [%]': [],
      'max. Druck [kPa]': [],
      'Scherzyklen': []
   },
   'Impulsantwort': {
      'Eingangsdruecke [kPa]': [],
      'Dehnungsinkremente [-]': []
   },
   'Spannungspfade': {
      'Referenzspannung [kPa]': [],
      'Grenzspannungen [kPa]': [],
      'Dehnungsinkremente [-]': [],
      'Winkelunterteilungen': []
   },
   'Antwortellipsen': {
      'Spannungspunkte [kPa]': [],
      'Dehnungsinkrement [-]': [],
      'Winkelunterteilungen': [],
      'Max. Spannung [kPa]': []
   }
}


referenzbefehle = {
   'Linux': {
      'Abaqus': [],
      'Python': [],
      'Intel Fortran': [],
      'GNU Fortran': []
   },
   'Windows': {
      'Abaqus': [],
      'Python': [],
      'Intel Fortran': [],
      'GNU Fortran': []
   }
}


programmoptionen = [
   ['Was soll simuliert werden?', 'test',
      [['Oedometerversuch', 'oedo'],
      ['Triaxialversuch', 'triax'],
      ['Einfachscherversuch', 'scher'],
      ['Impulsantwort', 'impuls'],
      ['Spannungspfade', 'pfade'],
      ['Antwortellipsen', 'ellipsen']]],
   ['Welches Programm soll benutzt werden?', 'prog',
      [['Fortran UMAT/VUMAT/XMAT', 'fortran'],
      ['Abaqus Standard/Explicit', 'abaqus']]],
   ['Zusaetzliche Einstellungen', 'zusatz',
      [['normaler Ablauf', 'normal'],
      ['Berechnungen ohne Plot durchfuehren', 'keinplot'],
      ['Arbeitsverzeichnis nicht entfernen', 'ordnerbehalten'],
      ['nur Dateien vorbereiten', 'nurvorbereiten']]]]
#


# -------------------------------------------------------------------------------------------------
def Informationsausgabe(einstellungen, optionen):
   """Gebe zusammenfassende Informationen ueber die durchzufuehrenden Versuche aus.
   """
   global programmoptionen
   #
   auswahltext = 'Folgende Auswahl ist getroffen worden: '
   verfuegbare_optionen = [tempoption[1] for tempoption in programmoptionen]
   for idx_option, tempoption in enumerate(verfuegbare_optionen):
      werte = [tempwert[1] for tempwert in programmoptionen[idx_option][2]]
      for idx_wert, einzelwert in enumerate(werte):
         if (optionen[tempoption] == einzelwert):
            auswahltext += programmoptionen[idx_option][2][idx_wert][0] + ' - '
            break
   #
   print(auswahltext[:-3])
   #
   # Ungueltige Kombinationen ausschliessen
   if (((optionen['test'] == 'scher') and (optionen['prog'] == 'fortran'))
      or ((optionen['test'] == 'impuls') and (optionen['prog'] == 'abaqus'))
      or ((optionen['test'] == 'pfade') and (optionen['prog'] == 'abaqus'))
      or ((optionen['test'] == 'ellipsen') and (optionen['prog'] == 'abaqus'))):
      print('Die ausgewählte Kombination von test=' + optionen['test'] \
         + ' und prog=' + optionen['prog'] + ' wird nicht unterstuetzt')
      return False
   #
   # Informationsausgabe
   if (optionen['test'] == 'oedo'):
      print('Der Druckverlauf des Oedometerversuchs ist ' \
         + ', '.join([str(x) + 'kPa' for x in einstellungen['Oedometerversuch']['Druckverlauf [kPa]']]) \
         + ' (Probenhoehe: ' + str(einstellungen['Oedometerversuch']['Probenhoehe [mm]']) \
         + 'mm, Probenradius: ' + str(einstellungen['Oedometerversuch']['Probenhoehe [mm]']) \
         + 'mm).')
   elif (optionen['test'] == 'triax'):
      print('Der Triaxialversuch hat einen max. Druck von ' \
         + str(einstellungen['Triaxialversuch']['max. Druck [kPa]']) \
         + ' kPa und eine max. Stauchung von ' \
         + str(einstellungen['Triaxialversuch']['max. Stauchung [%]']) + '% (Probenhoehe: '  \
         + str(einstellungen['Triaxialversuch']['Probenhoehe [mm]']) + 'mm, Probenradius: ' \
         + str(einstellungen['Triaxialversuch']['Probenhoehe [mm]']) + 'mm).')
   elif (optionen['test'] == 'scher'):
      print('Der Einfachscherversuch soll bis zu ' \
         + str(einstellungen['Einfachscherversuch']['max. seitliche Auslenkung [%]']) \
         + '%% seitlich ausgelenkt werden bein einem Druck von ' \
         + str(einstellungen['Einfachscherversuch']['max. Druck [kPa]']) \
         + ' kPa (Probenhoehe: '  \
         + str(einstellungen['Triaxialversuch']['Probenhoehe [mm]']) + 'mm, Probenradius: ' \
         + str(einstellungen['Triaxialversuch']['Probenhoehe [mm]']) + 'mm).')
      print('Es sollen ' + str(einstellungen['Einfachscherversuch']['Scherzyklen']) \
         + ' Zyklen betrachtet werden')
   elif (optionen['test'] == 'impuls'):
      print('Für die Impulsantwort sollen die folgenden Drücke und Dehnungen genutzt werden:')
      print('Drücke [kPa]: ' + ', '.join([str(x) for x in einstellungen['Impulsantwort']['Eingangsdruecke [kPa]']]))
      print('Dehnungen [-]: ' + ', '.join([str(x) for x in einstellungen['Impulsantwort']['Dehnungsinkremente [-]']]))
   elif (optionen['test'] == 'pfade'):
      print('Für die Erstellung der Spannungspfade werden der folgende Referenzdruck und Dehnungsrate verwendet:')
      print('Referenzdruck [kPa]: ' + ', '.join([str(x) for x in einstellungen['Spannungspfade']['Referenzspannung [kPa]']]))
      print('Dehnungsrate [-]: ' + str(einstellungen['Spannungspfade']['Dehnungsinkremente [-]']))
      print('Es werden Spannungspfade in ' + str(einstellungen['Spannungspfade']['Winkelunterteilungen']) \
         + ' Winkelschritten im Spannungsintervall [' \
         + ', '.join([str(x) for x in einstellungen['Spannungspfade']['Grenzspannungen [kPa]']]) + '] verfolgt')
   elif (optionen['test'] == 'ellipsen'):
      print('Es werden Antwortellipsen um die folgenden Spannungspunkte erstellt:')
      for refspannungen in einstellungen['Antwortellipsen']['Spannungspunkte [kPa]']:
         print('   ' + ', '.join([str(x) for x in refspannungen]))
      #
      print('Die Dehnungsrate [-] beträgt: ' + str(einstellungen['Antwortellipsen']['Dehnungsinkrement [-]']))
      print('Für die Antwortellipsen werden Punkte in ' + str(einstellungen['Spannungspfade']['Winkelunterteilungen']) \
         + ' Winkelschritten ausgewertet.')
   print('---')
   print('Die Versuche starten bei ' + str(einstellungen['Global']['Startzeit [s]']) \
      + 's mit einem Startinkrement von ' + str(einstellungen['Global']['Startinkrement [s]']) \
      + 's und max. ' + str(einstellungen['Global']['max. Iterationen']) + ' Interationen.')
   if (optionen['prog'] == 'fortran'):
      print('Es wird der Compiler ' + einstellungen['Fortran']['Compiler'] + ' verwendet.')
   elif (optionen['prog'] == 'abaqus'):
      print('Es wird Abaqus und der damit verlinkte Intel-Compiler verwendet.')
      print('Die maximale Abaqus-Laufzeit beträgt jeweils ' + str(einstellungen['Global']['max. Laufzeit Abaqus [s]']) \
      + 's und die Simulationen haben eine Dauer von ' + str(einstellungen['Global']['Abaqus Simulationsdauer [s]']) \
      + 's mit insgesamt ' + str(einstellungen['Global']['Anzahl Ausgaben Abaqus']) + ' Ausgabewerten.')
   #
   print('Das verwendete Material ist ' + einstellungen['Material']['Name'] \
      + ' mit der Bezeichnung ' + einstellungen['Material']['Bezeichnung'])
   print('---')
   return True
#


# -------------------------------------------------------------------------------------------------
def Ersatzwerte_Zuweisen(einstellungen, prog, routine, zusatz=''):
   """Erstelle eine Zuordnung einzelner Ersatzvariablen zu den in einstellungen uebergebenen Werten.
   Falls an jeden Float-Zahlenwerte am Ende ein Zusatz hinzugefuegt werden soll, kann dieser
   entsprechend uebergeben werden (bspw. '_dp' fuer Fortran-Dateien mit
   integer, parameter :: dp = selected_real_kind(15)
   """
   import sys
   import os
   sys.path.insert(0, os.path.abspath(os.path.curdir))
   #
   constitutive_model_name = einstellungen['Material']['Name']
   # materialparameters und statevariables werden mithilfe einer optional bereitsgestellten Datei berechnet
   materialparameters = [0.0 for x in range(16)]
   statevariables = [0.0 for x in range(20)]
   #
   # Fuer ein direktes Ersetzen von Materialparametern und Statusvariablen wird eine Datei materialdaten.py
   # benoetigt, die die folgenden Funktionen bereitstellt
   #  - [success, materialparameters, adj_name] = Get_Material(material_description, igran_active,
   #        constitutive_model_name, nu, routine_flag) und
   #  - [success, statevariables] = Prepare_State(constitutive_model_name, voidratio,
   #        intergranular_strain, igran_active, integration_method, first_dt, integration_tolerance,
   #        crit_voidratio, routine_flag)
   functions_found = False
   try:
      from materialdaten import Get_Material, Prepare_State
      functions_found = True
   except:
      print('Hinweis: Keine Datei materialdaten.py mit Get_Material() und Prepare_State() gefunden, um materialparameters zu berechnen')
   #
   if (functions_found):
      flags = None
      try:
         flags = einstellungen['Fortran']['Compiler Argumente'][routine]
      except:
         pass
         # Es sollte vorher sichergestellt werden, dass diese Abfrage fehlschlaegt.
         # Aktuell wird das an spaeterer Stelle durchgefuehrt
         #print('Warnung: Keine Eintraege fuer "Compiler Argumente" mit dem Eintrag ' + routine + ' gefunden')
      #
      if (flags is not None):
         routine_flag = '_XMAT'
         for flag in flags[0]:
            if (flag.startswith('D_')):
               routine_flag = flag[1:]
               break
         #
         material_description = einstellungen['Material']['Bezeichnung']
         igran_active = einstellungen['Material']['Intergr. Dehnung aktiv']
         #
         print('Hinweis: Berechne materialparameters und statevariables basierend auf den Funktionen in materialdaten.py')
         print('fuer ' + material_description + ' mit dem Stoffmodell ' + constitutive_model_name + ' und Routine ' + routine_flag)
         #
         [is_success, materialparameters, adj_name] = Get_Material(material_description=material_description,
            igran_active=igran_active, constitutive_model_name=constitutive_model_name, nu=0.25,
            routine_flag=routine_flag)
         if (not is_success):
            print('Warnung: Berechnung der materialparameters fehlgeschlagen')
         #
         voidratio = einstellungen['Material']['Anfangsporenzahl e_0 [-]']
         intergranular_strain = einstellungen['Material']['Intergranulare Dehnung h [-]']
         first_dt = einstellungen['Global']['Startinkrement [s]']
         #
         crit_voidratio = 1.0
         if (constitutive_model_name.lower() == 'Baro-Ko21'.lower()):
            crit_voidratio = materialparameters[9]
         #
         [is_success, statevariables] = Prepare_State(constitutive_model_name=constitutive_model_name,
            voidratio=voidratio, intergranular_strain=intergranular_strain, igran_active=igran_active,
            integration_method=1, first_dt=first_dt, integration_tolerance=0.0001,
            crit_voidratio=crit_voidratio, routine_flag=routine_flag)
         if (not is_success):
            print('Warnung: Berechnung der statevariables fehlgeschlagen')
   #
   sys.path.remove(os.path.abspath(os.path.curdir))
   #
   zuordnung = {
      '--outfilename--': '',
      '--maxiter--': str(einstellungen['Global']['max. Iterationen']),
      '--starttime--': str(einstellungen['Global']['Startzeit [s]']) + zusatz,
      '--sim_duration--': str(einstellungen['Global']['Abaqus Simulationsdauer [s]']) + zusatz,
      '--num_outputs--': str(einstellungen['Global']['Anzahl Ausgaben Abaqus']) + zusatz,
      '--timeincrement--': str(einstellungen['Global']['Startinkrement [s]']) + zusatz,
      '--materialname--': constitutive_model_name,
      '--materialdescription--': einstellungen['Material']['Bezeichnung'],
      '--initialvoidratio--': str(einstellungen['Material']['Anfangsporenzahl e_0 [-]']) + zusatz,
      '--initialdensity--': str(einstellungen['Material']['Einbaudichte [g/cm^3]']) + zusatz,
      '--intergranularstrain--': ', '.join([str(x) + zusatz for x in einstellungen['Material']['Intergranulare Dehnung h [-]']]),
      '--igranactive--': ''.join(['.True.' if einstellungen['Material']['Intergr. Dehnung aktiv'] else '.False.']),
      '--numparameter--': str(einstellungen['Material']['max. Anzahl Parameter']),
      '--numstatevar--': str(einstellungen['Material']['max. Anzahl Statusvariablen']),
      # The following two are not defined in einstellungen.json but calculated based on given
      # constitutive_model_name, material_description, void ratio, intergranular strain flag and values
      '--materialparameters--': ', '.join([str(x) + zusatz for x in materialparameters]),
      '--statevariables--': ', '.join([str(x) + zusatz for x in statevariables]),
      # Oedometerversuch
      '--oedo_height--': str(einstellungen['Oedometerversuch']['Probenhoehe [mm]']/1000.0) + zusatz,
      '--oedo_radius--': str(einstellungen['Oedometerversuch']['Probenradius [mm]']/1000.0) + zusatz,
      '--pressure_entries--': str(len(einstellungen['Oedometerversuch']['Druckverlauf [kPa]'])),
      '--oedo_pressure--': ', '.join([str(x) + zusatz for x in einstellungen['Oedometerversuch']['Druckverlauf [kPa]']]),
      # Triaxialversuch
      '--triax_height--': str(einstellungen['Triaxialversuch']['Probenhoehe [mm]']/1000.0) + zusatz,
      '--triax_radius--': str(einstellungen['Triaxialversuch']['Probenradius [mm]']/1000.0) + zusatz,
      '--triax_maxcontraction--': str(einstellungen['Triaxialversuch']['max. Stauchung [%]']/100.0) + zusatz,
      '--triax_pressure--': str(einstellungen['Triaxialversuch']['max. Druck [kPa]']) + zusatz,
      # Einfachscherversuch
      '--shear_height--': str(einstellungen['Einfachscherversuch']['Probenhoehe [mm]']/1000.0) + zusatz,
      '--shear_radius--': str(einstellungen['Einfachscherversuch']['Probenradius [mm]']/1000.0) + zusatz,
      '--shear_pressure--': str(einstellungen['Einfachscherversuch']['max. Druck [kPa]']) + zusatz,
      '--shear_excitation--': str(einstellungen['Einfachscherversuch']['max. seitliche Auslenkung [%]']/100.0) + zusatz,
      '--shear_cycles--': str(einstellungen['Einfachscherversuch']['Scherzyklen']),
      # Impulsantwort
      '--impuls_stress--': ', '.join([str(x) + zusatz for x in einstellungen['Impulsantwort']['Eingangsdruecke [kPa]']]),
      '--impuls_strain--': ', '.join([str(x) + zusatz for x in einstellungen['Impulsantwort']['Dehnungsinkremente [-]']]),
      # Spannungspfade
      '--spider_refstress--': ', '.join([str(x) + zusatz for x in einstellungen['Spannungspfade']['Referenzspannung [kPa]']]),
      '--spider_maxstress--': ', '.join([str(x) + zusatz for x in einstellungen['Spannungspfade']['Grenzspannungen [kPa]']]),
      '--spider_refstrain--': str(einstellungen['Spannungspfade']['Dehnungsinkremente [-]']) + zusatz,
      '--spider_numangles--': str(einstellungen['Spannungspfade']['Winkelunterteilungen']),
      # Antwortellipsen
      '--envelopes_numstresses--': str(len(einstellungen['Antwortellipsen']['Spannungspunkte [kPa]'])),
      '--envelopes_stresses--': ', '.join([', '.join([str(x) + zusatz for x in y]) for y in einstellungen['Antwortellipsen']['Spannungspunkte [kPa]']]),
      '--envelopes_refstrain--': str(einstellungen['Antwortellipsen']['Dehnungsinkrement [-]']) + zusatz,
      '--envelopes_numangles--': str(einstellungen['Antwortellipsen']['Winkelunterteilungen']),
      # Abaqus
      '--routinetype--': '',
      '--abaqustype--': ''
   }
   return zuordnung
#

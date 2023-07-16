# -*- coding: utf-8 -*-
"""
plotausgabe.py   v0.1
2020-05 Dominik Zobel
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
def Plot_Hinzufuegen(ax, xwerte, ywerte, label, xlabel='', ylabel='', xlim=[], ylim=[],
   xscale='linear', fontsize=8, idx_plot=0, num_plots=1, legpos='upper right', marknum=1000):
   """Plotte einen weiteren Datensatz mit xwerte und ywerte und der Bezeichnung label in die
   uebergebene Plotflaeche ax. Der Stil wird anhand der Laufnummer idx_plot von erwarteten
   num_plots gesetzt, wobei diese Funktion fuer jede einzelne Laufnummer aufgerufen werden sollte.
   Im Plot werden alle marknum Marker gesetzt.

   Optional koennen die Beschriftungen xlabel und ylabel, sowie die Begrenzungen xlim und ylim
   fuer die jeweiligen Achsen uebergeben werden. Falls die Skalierung in x-Richtung nicht linear
   dargestellt werden soll, kann das ueber xscale angepasst werden. Die Schriftgroesse wird mit
   fontsize angepasst.
   """
   from matplotlib import pyplot
   #
   # Starte immer von der dunkelsten Farbe
   #plotfarbe = pyplot.cm.viridis([float(idx_plot-1)/num_plots])[0]
   plotfarbe = pyplot.cm.viridis([1/num_plots*(0.5 + idx_plot)])[0]
   #
   # Kleinste Dicke 1.2 und dann in 0.6 Schritten zunehmen
   liniendicke = 0.6 + (num_plots - idx_plot)*0.6
   #
   # Alle marknum Werte markieren
   markerdicke = 2.4 + (num_plots - idx_plot)*0.6
   markerlist = ['x', 'o', 'd', '<', 'p']
   #
   ax.plot(xwerte, ywerte, label=label, color=plotfarbe, linewidth=liniendicke,
      marker=markerlist[(idx_plot+1) % len(markerlist)], markersize=markerdicke, markevery=marknum)
   #ax.grid(which='major', linestyle=':')
   ax.grid(which='minor', color='#dddddd', linestyle=':')
   if (xlim != []):
      ax.set_xlim(xlim[0], xlim[1])
   #
   if (ylim != []):
      ax.set_ylim(ylim[0], ylim[1])
   #
   ax.set_xscale(xscale)
   #
   #for tick in ax.xaxis.get_major_ticks():
   #   tick.label.set_fontsize(fontsize)
   #
   #for tick in ax.yaxis.get_major_ticks():
   #   tick.label.set_fontsize(fontsize)
   #
   if (xlabel != ''):
      ax.set_xlabel(xlabel)
   #
   if (ylabel != ''):
      ax.set_ylabel(ylabel)
   #
   ax.legend(loc=legpos)#, fontsize=fontsize)
#


# -------------------------------------------------------------------------------------------------
def Plot_Ergebnisse(dateien, namen, aktuellertest, programm, einstellungen):
   """Plottet die Ergebnisse aus den Ausgabedateien von Simulationen. Dazu wird eine Liste dateien
   mit den Dateinamen der jeweiligen csv-Dateien benoetigt (ohne die Endung .csv). Ausserdem sind
   aktuellertest fuer die Unterscheidung des Plottyps und programm fuer die Bezeichnung der
   Ausgabedateien erforderlich. einstellungen entspricht der Struktur der Datei einstellungen.json
   und enthaelt Informationen, mit welchen Optionen die jeweiligen Tests durchgefuehrt worden sind.
   """
   #
   import matplotlib
   from matplotlib import pyplot
   from math import floor, sqrt, pi, sin, tan, atan, atan2
   #
   if (dateien == []):
      return False
   #
   print('# Plotte Ergebnisse')
   #
   plotbreite = 8.0 # [cm]
   plothoehe = 6.4 # [cm]
   #
   breite_beschriftung_links = 1.6 # [cm]
   hoehe_beschriftung_unten = 1.0 # [cm]
   abstand_rechts = 0.4 # [cm]
   abstand_oben = 0.2 # [cm]
   ylabeloffset = 0.3 # [cm]
   #
   # Fixwerte
   dpi = 300
   inch = 2.54; # [cm]
   #
   fig1 = pyplot.figure(figsize=(plotbreite/inch, plothoehe/inch), dpi=dpi)
   ax1 = fig1.gca()
   axoffset = [breite_beschriftung_links/plotbreite, hoehe_beschriftung_unten/plothoehe]
   axsize = [1.0-(breite_beschriftung_links+abstand_rechts)/plotbreite,
             1.0-(hoehe_beschriftung_unten+abstand_oben)/plothoehe]
   ax1.set_position([axoffset[0], axoffset[1], axsize[0], axsize[1]])
   #
   fig2 = pyplot.figure(figsize=(plotbreite/inch, plothoehe/inch), dpi=dpi)
   ax2 = fig2.gca()
   ax2.set_position([axoffset[0], axoffset[1], axsize[0], axsize[1]])
   #
   fontsize = 8
   linienbreite = 0.5
   #
   #matplotlib.rcParams['axes.linewidth'] = linienbreite
   #matplotlib.rcParams['lines.linewidth'] = 2.4*linienbreite
   #matplotlib.rcParams['grid.linewidth'] = linienbreite
   #matplotlib.rcParams['xtick.major.width'] = linienbreite
   #matplotlib.rcParams['xtick.minor.width'] = linienbreite
   #matplotlib.rcParams['ytick.major.width'] = linienbreite
   #matplotlib.rcParams['ytick.minor.width'] = linienbreite
   #
   dateiendung = '.pdf'; # pdf oder png
   plotnamen = []
   #
   for idx_datei, datei in enumerate(dateien):
      label = namen[idx_datei]
      # Aktuelle Datei einlesen -> zwischen Abaqus-Output und Fortran-Output unterscheiden/beruecksichtigen
      tabelle = []
      with open(datei + '.csv', 'r') as eingabe:
         for zeile in eingabe:
            eintraege = zeile.split()
            if (len(eintraege) < 2):
               continue
            #
            try:
               zahlen = [float(x) for x in eintraege]
            except:
               continue
            #
            tabelle += [zahlen]
      #
      if (len(tabelle) == 0):
         print('# Warnung: Es konnten keine Werte aus ' + datei + '.csv eingelesen werden')
         continue
      #
      if (len(tabelle[0]) < 2):
         print('# Warnung: Weniger als zwei Spalten an Werten in ' + datei + '.csv')
         continue
      #
      # FIXME: Pruefen ob tabelle auch tatsaechlich (genuegend) Werte hat
      if (aktuellertest == 'oedo'):
         xwerte = [t[0] for t in tabelle]
         ywerte = [t[1] for t in tabelle]
         xlim = [-max(einstellungen['Oedometerversuch']['Druckverlauf [kPa]']),
                 -min(einstellungen['Oedometerversuch']['Druckverlauf [kPa]'])]
         Plot_Hinzufuegen(ax=ax1, xwerte=xwerte, ywerte=ywerte, label=label,
            xlabel='Spannung $-T_1$ [kPa]', ylabel='Porenzahl $e$ [-]', xlim=xlim, xscale='log',
            fontsize=fontsize, idx_plot=idx_datei, num_plots=len(dateien))
         plotnamen = ['Oedo_' + programm + dateiendung]
      #
      elif (aktuellertest == 'triax'):
         xwerte = [-t[0] for t in tabelle]
         ywerte = [-t[1] for t in tabelle]
         xlim = [0.0, einstellungen['Triaxialversuch']['max. Stauchung [%]']]
         Plot_Hinzufuegen(ax=ax1, xwerte=xwerte, ywerte=ywerte, label=label,
            xlabel='Axiale Dehnung $-\\varepsilon_1$ [\\%]', ylabel='Volumetrische Dehnung $\\varepsilon_V$ [\\%]', xlim=xlim,
            fontsize=fontsize, idx_plot=idx_datei, num_plots=len(dateien), legpos='lower left')
         ywerte = [t[2] for t in tabelle]
         Plot_Hinzufuegen(ax=ax2, xwerte=xwerte, ywerte=ywerte, label=label,
            xlabel='Axiale Dehnung $-\\varepsilon_1$ [\\%]', ylabel='Dev. Spannung $-\\left(T_1 - T_3\\right)$ [kPa]', xlim=xlim,
            fontsize=fontsize, idx_plot=idx_datei, num_plots=len(dateien), legpos='lower right')
         plotnamen = ['Triax_' + programm + '_vol' + dateiendung,
                      'Triax_' + programm + '_dev' + dateiendung]
      #
      elif (aktuellertest == 'scher'):
         xwerte = [t[0] for t in tabelle]
         ywerte = [t[1] for t in tabelle]
         scherzyklen = einstellungen['Einfachscherversuch']['Scherzyklen']
         max_auslenkung = einstellungen['Einfachscherversuch']['max. seitliche Auslenkung [%]']
         if (scherzyklen == 0):
            xlim = [0.0, max_auslenkung]
         else:
            xlim = [-max_auslenkung, max_auslenkung]
         #
         Plot_Hinzufuegen(ax=ax1, xwerte=xwerte, ywerte=ywerte, label=label,
            xlabel='Scherdehnung $-\\varepsilon_{12}$ [\\%]', ylabel='Axiale Dehnung $-\\varepsilon_1$ [\\%]', xlim=xlim, fontsize=fontsize,
            idx_plot=idx_datei, num_plots=len(dateien))
         ywerte = [t[2] for t in tabelle]
         Plot_Hinzufuegen(ax=ax2, xwerte=xwerte, ywerte=ywerte, label=label,
            xlabel='Scherdehnung $-\\varepsilon_{12}$ [\\%]', ylabel='Scherspannung $-T_{12}$ [kPa]', xlim=xlim, fontsize=fontsize,
            idx_plot=idx_datei, num_plots=len(dateien))
         plotnamen = ['Scher_' + programm + '_axial' + dateiendung,
                      'Scher_' + programm + '_stress' + dateiendung]
      #
      elif (aktuellertest == 'impuls'):
         xwerte = [t[0] for t in tabelle]
         ywerte = [t[6] for t in tabelle]
         Plot_Hinzufuegen(ax=ax1, xwerte=xwerte, ywerte=ywerte, label=label,
            xlabel='Spannung $-T_1$ [kPa]', ylabel='Porenzahl $e$ [-]', fontsize=fontsize,
            idx_plot=idx_datei, num_plots=len(dateien))
         plotnamen = ['Impuls_' + programm + dateiendung]
      #
      elif ((aktuellertest == 'pfade') or (aktuellertest == 'ellipsen')):
         refspannungen = einstellungen['Spannungspfade']['Referenzspannung [kPa]']
         aktueller_winkel = tabelle[0][0]
         num = 0
         labels = [aktueller_winkel]
         xdaten = [[]]
         ydaten = [[]]
         for zeile in tabelle:
            if (zeile[0] != aktueller_winkel):
               aktueller_winkel = zeile[0]
               labels += [aktueller_winkel]
               xdaten += [[]]
               ydaten += [[]]
               num += 1
            #
            xdaten[num] += [zeile[2]]
            ydaten[num] += [zeile[1]]
         #
         if (aktuellertest == 'pfade'):
            maxwert = einstellungen['Spannungspfade']['Grenzspannungen [kPa]'][0]
            xlim = [0, -floor(maxwert/10)*10]
            ylim = [0, -floor(maxwert/10)*10]
            #
            idx_labeloffset = 0
            red_fak = 0.7
            delta1 = red_fak * min([-(maxwert-x) for x in refspannungen[:3]])
            delta2 = red_fak * min([-x for x in refspannungen[:3]])
            #
            for idx, wert in enumerate(xdaten[0]):
               if ((wert-xdaten[0][0]) > delta1):
                  idx_labeloffset = idx
                  break
            #
            datensatz_mitte = len(xdaten)//2
            for idx, wert in enumerate(xdaten[datensatz_mitte]):
               if (-(wert-xdaten[datensatz_mitte][0]) > delta2):
                  idx_labeloffset = min(idx_labeloffset, idx)
                  break
         #
         else:
            maxwert = einstellungen['Antwortellipsen']['Max. Spannung [kPa]']
            xlim = [0, -(round(maxwert/10)+2)*10]
            ylim = [0, -(round(sqrt(2)*maxwert/10)+1)*10]
         #
         if (idx_datei == 0):
            # FIXME Einlesen, sofern vorhanden
            phi_c = einstellungen['Material']['Winkel Grenzbedingung [Grad]']
            p_mean = sum(refspannungen[0:3])/3.0
            M_ext = (2.0*sqrt(6.0)*sin(phi_c*pi/180.0))/(3.0+sin(phi_c*pi/180.0))
            M_komp = (2.0*sqrt(6.0)*sin(phi_c*pi/180.0))/(3.0-sin(phi_c*pi/180.0))
            q_ext = M_ext*p_mean
            q_komp = M_komp*p_mean
            #
            # FIXME: Nur die obere Grenze sollte passen, die untere wurde abgeschaetzt
            grenzwinkel = pi/2.0-atan((1.0 - sin(phi_c*pi/180.0))/(1.0 + sin(phi_c*pi/180.0)))
            grenze_oben = -maxwert*tan(grenzwinkel)
            grenze_unten = -maxwert*tan(pi/2.0 - grenzwinkel)
            #print([-maxwert, grenze_unten, grenze_oben])
            ax1.plot([0.0, -maxwert], [0.0, grenze_oben],
               linewidth=linienbreite, linestyle='--', color=[0.4, 0.4, 0.4])
            ax1.plot([0.0, -maxwert], [0.0, grenze_unten],
               linewidth=linienbreite, linestyle='--', color=[0.4, 0.4, 0.4])
            #
            #M_ext = 6.0*sin(phi_c*pi/180.0)/(3.0+sin(phi_c*pi/180.0))
            #M_komp = 6.0*sin(phi_c*pi/180.0)/(3.0-sin(phi_c*pi/180.0))
            #skal = sqrt(2)/3
            #M_ext_s = M_ext*skal
            #M_komp_s = M_komp*skal
            ##
            #fac_max = (1 + 2*M_ext_s)/(sqrt(2)*(1.0 - M_ext_s))
            #fac_min = (sqrt(2)*(1 - M_komp_s))/(2.0 + M_komp_s)
            ##
            #print([0.0, -maxwert/fac_max ,-maxwert])
            #ax1.plot([0.0, -maxwert/fac_max], [0.0,-maxwert],
               #linewidth=linienbreite, linestyle='--', color=[0.4, 0.4, 0.4])
            #ax1.plot([0.0, -maxwert], [0.0, -maxwert*fac_min],
               #linewidth=linienbreite, linestyle='--', color=[0.4, 0.4, 0.4])
         #
         for idx_plot in range(num+1):
            if ((len(xdaten[idx_plot]) < 2) or (len(ydaten[idx_plot]) < 2)):
               print('# Warnung: Nicht genuegend Werte fuer Ploterstellung')
               return False
            #
            #plotfarbe = pyplot.cm.cubehelix([float(idx_plot)/(num+1)])[0]
            #plotfarbe = pyplot.cm.rainbow_r([float(idx_plot)/(num+1)])[0]
            plotfarbe = pyplot.cm.rainbow_r([float(idx_datei)/len(dateien)])[0]
            #
            #plotlabel = str(labels[idx_plot])
            plotlabel = '_nolegend_'
            if (idx_plot == 0):
               plotlabel = label
            #
            marker = 'None'
            if (aktuellertest == 'pfade'):
               marker = '.'
            #
            if (aktuellertest == 'ellipsen'):
               ax1.plot(xdaten[idx_plot][0], ydaten[idx_plot][0], color=plotfarbe, marker='o', zorder=5,
                  mfc='#000000', mec='#ffffff', markersize=3.4, markeredgewidth=0.65)
               del xdaten[idx_plot][0]
               xdaten[idx_plot] += [xdaten[idx_plot][0]]
               del ydaten[idx_plot][0]
               ydaten[idx_plot] += [ydaten[idx_plot][0]]
            #
            Plot_Hinzufuegen(ax=ax1, xwerte=xdaten[idx_plot], ywerte=ydaten[idx_plot], label=plotlabel,
               xlabel='Spannung $-\sqrt{2}T_2$ [kPa]', ylabel='Spannung $-T_1$ [kPa]', fontsize=fontsize,
               idx_plot=idx_datei, num_plots=len(dateien), marknum=16)
            #ax1.plot(xdaten[idx_plot], ydaten[idx_plot], label=plotlabel, color=plotfarbe, linewidth=linienbreite,
            #   marker=marker, markersize=2.4, markeredgecolor=[0.0, 0.0, 0.0], markevery=20)
            if ((aktuellertest == 'pfade') and (idx_datei == len(dateien)-1)):
               dx = xdaten[idx_plot][idx_labeloffset] - xdaten[idx_plot][idx_labeloffset-1]
               dy = ydaten[idx_plot][idx_labeloffset] - ydaten[idx_plot][idx_labeloffset-1]
               laenge = sqrt(dx**2 + dy**2)
               if (laenge == 0.0):
                  laenge = 1.0
               #
               dx_skal = dx/laenge
               dy_skal = dy/laenge
               winkel = atan2(dy_skal, dx_skal)/pi*180.0
               #
               if (abs(winkel) > 90.0):
                  winkel += 180.0
               #
               xpos_text = xdaten[idx_plot][idx_labeloffset]
               ypos_text = ydaten[idx_plot][idx_labeloffset]
               #
               temptext = ax1.text(xpos_text, ypos_text, str(int(labels[idx_plot])), fontsize=6, ha='center', va='center',
                  rotation=winkel);#, color=line.get_color())
               temptext.set_bbox(dict(facecolor='white', edgecolor='white',
                  boxstyle='square,pad=0.15', mutation_aspect=0.2))
         #
         if ((aktuellertest == 'pfade') and (idx_datei == len(dateien)-1)):
            ax1.plot([x[1] for x in xdaten] + [xdaten[0][1]], [y[1] for y in ydaten] + [ydaten[0][1]],
               linewidth=linienbreite, linestyle='-', color=[0.5, 0.5, 0.5])
            ax1.plot(xdaten[0][0], ydaten[0][0], 'r', marker='o', zorder=5,
               mfc='#000000', mec='#ffffff', markersize=3.4, markeredgewidth=0.65)
         #
         #xlim = [0, max([max(x) for x in xdaten])]
         #ylim = [0, max([max(x) for x in ydaten])]
         #ax1.set_xlim(0.0, -maxwert/sqrt(2.0))
         #ax1.set_ylim(0.0, -maxwert)
         #
         ax1.set_xlim(xlim)
         ax1.set_ylim(ylim)
         #
         #ax1.grid(which='major', linestyle=':')
         #ax1.grid(which='minor', color='#eeeeee', linestyle=':')
         #
         #ax1.set_xlabel('Spannung $-\sqrt{2}T_2$ [kPa]')
         #ax1.set_ylabel('Spannung $-T_1$ [kPa]')
         #ax1.legend(loc='lower right', fontsize=fontsize)
         plotnamen = [aktuellertest.capitalize() + '_' + programm + dateiendung]
   #
   for ax in [ax1, ax2]:
      t_ax_pos = ax.get_position()
      ax_pos = [t_ax_pos.x0, t_ax_pos.y0, t_ax_pos.x1, t_ax_pos.y1]
      yax = ax.get_yaxis()
      yax.set_label_coords(-(breite_beschriftung_links-ylabeloffset)/(plotbreite*ax_pos[3]), 0.5)
   # Plots speichern
   fig1.savefig(plotnamen[0])
   if (len(plotnamen) == 2):
      fig2.savefig(plotnamen[1])
   #
   return True
#

# -*- coding: utf-8 -*-
"""
aufrufhilfen.py   v0.4
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
def Reihenfolge_Anpassen(einstellungen, dateien_und_routinen):
    """Erwartet eine Liste mit den verwendeten Dateien und routinen. Vergleicht die Namen der
    Routinen mit einer (optional) in einstellungen hinterlegten Ausgabe-Reihenfolge und sortiert
    sie entsprechend um. Was nicht in der Ausgabe-Reihenfolge ist, wird nach allen vorhandenen
    Eintraegen in der gleichen relativen Reihenfolge wieder angehaengt. Gibt den modifizierten
    Eintrag fuer dateien_und_routinen zurueck.
    """
    dateien = [x[0] for x in dateien_und_routinen]
    routinen = [x[1] for x in dateien_und_routinen]
    use_extra = False
    if (len(dateien_und_routinen[0]) == 3):
        extra = [x[2] for x in dateien_und_routinen]
        use_extra = True

    dateien_mod = []
    routinen_mod = []
    extra_mod = []
    namen = []
    for refroutine, refname in einstellungen['Ausgabe']['Plotreihenfolge']:
        if (refroutine in routinen):
            idx_add = routinen.index(refroutine)
            routinen_mod += [routinen[idx_add]]
            dateien_mod += [dateien[idx_add]]
            namen += [refname]
            if (use_extra):
                extra_mod += [extra[idx_add]]

    for routine in routinen:
        if (routine not in routinen_mod):
            idx_add = routinen.index(routine)
            routinen_mod += [routinen[idx_add]]
            dateien_mod += [dateien[idx_add]]
            namen += [routine]
            if (use_extra):
                extra_mod += [extra[idx_add]]

    if (use_extra):
        return [list(zip(dateien_mod, routinen_mod, extra_mod)), namen]
    else:
        return [list(zip(dateien_mod, routinen_mod)), namen]



# -------------------------------------------------------------------------------------------------
def Muster_Ersetzen(eingabedatei, ausgabedatei, zuordnung):
    """Lese eingabedatei ein und ersetze alle Muster in zuordnung.keys() mit den dazugehoerigen
    Werten. Schreibe die geaenderte Datei als ausgabedatei.
    """
    import bisect
    from .parameter import programmoptionen

    dateiinhalt = ''
    zeilenlimit = 100
    einrueckung_umbruch = 3

    fortran_startdatei = False
    util_dateien = [testoption[1] for testoption in programmoptionen[0][2]]
    if ((eingabedatei[-2:] == '.f') and any([x in eingabedatei.lower() for x in util_dateien])):
        fortran_startdatei = True

    with open(eingabedatei, 'r') as eingabe:
        for idx_zeile, ganzezeile in enumerate(eingabe):
            if ('--' in ganzezeile):
                # An dieser Stelle befindet sich mindestens ein '--' in der Zeile - und somit
                # wahrscheinlich auch ein Ersatzmuster. Pruefe alle Muster und ersetze ggfs. den Eintrag
                for muster in zuordnung.keys():
                    ganzezeile = ganzezeile.replace(muster, zuordnung[muster])

            # Zu lange Zeilen in Fortran automatisch aufteilen. Es wird erwartet, dass der Fortran-Code im free-Format
            # geschrieben ist, so dass am Ende der Zeile ein '&' angehaengt und einer neuen Zeile fortgefahren wird.
            if (fortran_startdatei and (len(ganzezeile) > zeilenlimit)):
                zeile_kuerzen = True
                # Falls die Ueberlaenge an einem Kommentar liegt -> ignorieren
                if (ganzezeile.startswith('c') or ganzezeile.startswith('!')):
                    zeile_kuerzen = False

                idx_kommentar = ganzezeile.find('!')
                if ((idx_kommentar != -1) and (idx_kommentar < zeilenlimit)):
                    zeile_kuerzen = False

                # Aktuelle Einrueckung ermitteln
                for idx_einrueckung in range(len(ganzezeile)):
                    if (ganzezeile[idx_einrueckung] != ' '):
                        break

                einrueckung = ''.join([' ' for idx in range(idx_einrueckung + einrueckung_umbruch)])
                # Alle Kommata und Leerzeichen der Zeile finden, um am letzten moeglichen Trennzeichen
                # vor Zeichenlimit umbrechen zu koennen
                temp_zeile = ganzezeile
                ganzezeile = ''
                idx_it = 0
                it_max = 50
                while (zeile_kuerzen):
                    idx_it += 1
                    if (idx_it > it_max):
                        print('Warnung: Fehler beim automatischen Umbrechen der Zeilen (' + eingabedatei + ' Zeile ' + str(idx_zeile+1) + ')')
                        ganzezeile += temp_zeile
                        break

                    if (len(temp_zeile) < zeilenlimit):
                        if (temp_zeile.strip() != '&'):
                            ganzezeile += temp_zeile

                        break

                    indizes = [idx for idx in range(len(temp_zeile)) if ((temp_zeile[idx] == ',') or (temp_zeile[idx] == ' '))]
                    if (len(indizes) == 0):
                        print('Warnung: Zu lange Zeile konnte nicht komplett umgebrochen werden')
                        ganzezeile += temp_zeile
                        break

                    try:
                        trennungs_idx = bisect.bisect(indizes, zeilenlimit) - 1
                    except:
                        trennungs_idx = -1

                    trennung = indizes[trennungs_idx]
                    ganzezeile += temp_zeile[:trennung] + ' &\n'
                    temp_zeile = einrueckung + temp_zeile[trennung:]

            dateiinhalt += ganzezeile

    with open(ausgabedatei, 'w') as ausgabe:
        ausgabe.write(dateiinhalt)



# -------------------------------------------------------------------------------------------------
def Abaqus_Version(abaqus_basisaufruf):
    """Ermittle aus einem Abaqus-Aufruf, welches Release gerade verwendet wird.
    """
    import subprocess

    try:
        ausgabe = subprocess.run([abaqus_basisaufruf, 'information=release'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    except:
        print('Warnung: Konnte abaqus nicht aufrufen. Pfad korrekt? Nehme testweise Version 2020 an')
        return '2020'

    # Typischerweise steht in der Ausgabe nahe dem Anfang eine Zeile "Abaqus JOB" und darunter
    # "Abaqus <version> ..." wobei <version> ermittelt und zurueckgegeben werden soll.
    ausgabezeilen = ausgabe.stdout.decode('utf-8').split('\n')
    while (not ausgabezeilen[0].startswith('Abaqus')):
        ausgabezeilen = ausgabezeilen[1:]

    version = ausgabezeilen[1].split()[1]
    return version



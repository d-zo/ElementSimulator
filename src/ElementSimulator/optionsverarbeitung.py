# -*- coding: utf-8 -*-
"""
optionsverarbeitung.py   v0.5
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
def Hilfsausgabe(programmname, optionen):
    """Gib Benutzungshinweise in der Konsole aus.
    """
    print('Das Programm kann interaktiv oder mit allen folgenden Argumenten aufgerufen werden:')
    schalter = ''
    optionsuebersicht = '      mit'
    for option in optionen:
        schalter += ' -' + option[1] + '=[arg]'
        einrueckung = ' ' * (len(option[1]) + 5)
        for idx_unteropt, unteroption in enumerate(option[2]):
            if (idx_unteropt == 0):
                optionsuebersicht += '\n   -' + option[1] + '=' + unteroption[1] + ': '  \
                    + unteroption[0]
            else:
                optionsuebersicht += '\n' + einrueckung + unteroption[1] + ': '  + unteroption[0]

    print('python3 ' + programmname + schalter)
    print(optionsuebersicht)
    return None



# -------------------------------------------------------------------------------------------------
def _Uebergabewerte_Interpretieren(optionen, argumente):
    """Vergleiche die uebergebenen argumente, ob sie den in optionen definierten Erwartungswerten
    entsprechen. Es wird ein dict mit den eingelesenen Werten zurueckgegeben.
    Falls -h oder --help uebergeben wird oder die argumente nicht einwandfrei eingelesen werden
    können, wird die Hilfsausgabe aufgerufen. In diesem Fall wird None zurueckgegeben.
    """
    if (len(argumente) >= 1):
        programmname = argumente[0]
        argumente = argumente[1:]

    if ((len(argumente) == 1) and any([argumente[0] == hilfe for hilfe in ['-h', '-help', '--help']])):
        return Hilfsausgabe(programmname=programmname, optionen=optionen)

    gesamtoptionen = dict()
    argument_bezeichner = [elem.split('=')[0] for elem in argumente]
    gueltige_optionen = [x[1] for x in optionen]

    for idx_arg, arg in enumerate(argument_bezeichner):
        if (not arg.startswith('-')):
            print('# Abbruch: Ungueltige Angabe ' + arg)
            return Hilfsausgabe(programmname=programmname, optionen=optionen)

        arg = arg[1:]
        if (arg not in gueltige_optionen):
            print('# Abbruch: Argument -' + arg+ ' unbekannt')
            return Hilfsausgabe(programmname=programmname, optionen=optionen)

        if (arg in gesamtoptionen):
            print('# Warnung: Option ' + arg + ' mehrfach uebergeben - werte nur die erste Angabe aus')
            continue

        # arg ist gueltig und noch nicht eingetragen. Extrahiere den dazugehoerigen Wert und speichere ihn in gesamtoptionen
        wert_eingelesen = argumente[idx_arg].split('=')[1]
        erlaubte_werte = [unteropt[1] for unteropt in optionen[gueltige_optionen.index(arg)][2]]

        if (wert_eingelesen not in erlaubte_werte):
            print('# Abbruch: Ungueltiger Wert ' + wert_eingelesen + ' für Argument -' + arg)
            return Hilfsausgabe(programmname=programmname, optionen=optionen)

        gesamtoptionen.update([(arg, wert_eingelesen)])

    for option in optionen:
        if (option[1] not in gesamtoptionen):
            print('# Abbruch: Argument -' + option[1] + ' nicht vorhanden')
            return Hilfsausgabe(programmname=programmname, optionen=optionen)

    return gesamtoptionen



# -------------------------------------------------------------------------------------------------
def _Auswahlliste_Zahleneingabe(beschreibung, optionen, max_iterationen=10):
    """Erstelle eine interaktive Auswahlliste mit der uebergebenen beschreibung. Unter optionen wird
    eine Liste mit bis zu neun Tupeln mit jeweils zwei Einträgen erwartet. Der erste Eintrag
    entspricht jeweils der angezeigten Option und der zweite Eintrag dem dazugehörigen Rückgabewert.
    Die Optionen werden der Reihe nach von 1 an durchnummeriert und durch eine interaktive Eingabe
    wird der entsprechende Wert ausgewählt. Falls 0 (Beenden) ausgewählt wird oder die Anzahl
    max_iterationen an zulässigen Versuchen überschritten wird, wird stattdessen None zurückgegeben.
    """
    idx_iteration = 0
    while True:
        idx_iteration += 1
        if (idx_iteration >= max_iterationen):
            print('# Abbruch: Zuviele Iterationen bei Verarbeitung der Zahleneingabe')
            return None

        print(beschreibung)
        for idx, einzeloption in enumerate(optionen):
            print('      (' + str(idx+1) + ') ' + einzeloption[0])

        print('      (0) Beenden')
        try:
            eingabewert = int(input('> '))
        except:
            # Integer ausserhalb der zulaessigen Optionen
            eingabewert = len(optionen)+1

        if (eingabewert == 0):
            return None
        elif (eingabewert > 0) and (eingabewert <= len(optionen)):
            return optionen[eingabewert-1][1]
        else:
            print('Ungültige Eingabe\n')



# -------------------------------------------------------------------------------------------------
def _Interaktive_Optionsauswahl(optionen):
    """Lese die uebergebenen optionen über eine Benutzereingabe ein. Gibt ein dict mit den Werten
    aus optionen und der Benutzereingabe zuruck. Falls die Eingabe beendet worden ist, wird None
    zurueckgegeben.
    """
    gesamtoptionen = dict()
    for option in optionen:
        auswahl = _Auswahlliste_Zahleneingabe(beschreibung=option[0],
            optionen=option[2])
        if (auswahl is None):
            print('Beende ...')
            return None
        else:
            gesamtoptionen.update([(option[1], auswahl)])

    return gesamtoptionen



# -------------------------------------------------------------------------------------------------
def Optionen_verarbeiten(argumente=[]):
    """Lese die uebergebenen argumente in eine Struktur von Optionen ein. Falls die Liste ungueltig
    ist, wird eine Hilfe ausgegeben und None zurueckgegeben. Falls eine leere Liste uebergeben wird,
    wird die Struktur von Optionen interaktiv ermittelt.
    """
    from .parameter import programmoptionen

    if (len(argumente) <= 1):
        optionen_formatiert = _Interaktive_Optionsauswahl(optionen=programmoptionen)
    else:
        optionen_formatiert = _Uebergabewerte_Interpretieren(optionen=programmoptionen,
            argumente=argumente)

    return optionen_formatiert



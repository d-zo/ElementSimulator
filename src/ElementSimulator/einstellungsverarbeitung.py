# -*- coding: utf-8 -*-
"""
einstellungsverarbeitung.py   v0.3
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
def _JSONDateiEinlesen(dateiname):
    """Lade eine JSON-formatierte Datei und gib die eingelesene Struktur zurueck.
    """
    import json

    eingelesen = None
    try:
        with open(dateiname, 'r', encoding='utf-8') as eingabe:
            eingelesen = json.load(eingabe)
    except FileNotFoundError:
        print('# Fehler: Datei ' + dateiname + ' konnte nicht gefunden/geoeffnet werden')
    except Exception as e:
        print('# Fehler: Datei ' + dateiname + ' konnte nicht eingelesen werden')
        print(e)

    return eingelesen




# -------------------------------------------------------------------------------------------------
def _Pruefe_Struktur_Rekursiv(struktur, referenz):
    """Prueft rekursiv, ob die uebergebene Struktur mit dem Schema der internen Struktur ueberein
    stimmt.
    """
    for refschluessel in referenz.keys():
        if (refschluessel not in struktur.keys()):
            print('# Abbruch: Erforderlicher Schluessel ' + refschluessel \
                + ' nicht in Einstellungsdatei')
            return False

        if isinstance(referenz[refschluessel], dict):
            if (not _Pruefe_Struktur_Rekursiv(struktur=struktur[refschluessel],
                referenz=referenz[refschluessel])):
                return False

    return True



# -------------------------------------------------------------------------------------------------
def _Einstellungen_Einlesen(dateiname, referenzstruktur=[]):
    """Liest die Einstellungen aus einer Datei namens dateiname ein und prueft, ob die Struktur der
    erwarteten referenzstruktur entspricht. Wenn die Struktur uebereinstimmt (Werte werden nicht
    geprueft!), dann wird die Struktur zurueckgegeben. Gibt andernfalls None zurueck.
    """
    einstellungen = _JSONDateiEinlesen(dateiname=dateiname)
    if (einstellungen is None):
        return None

    if (_Pruefe_Struktur_Rekursiv(struktur=einstellungen, referenz=referenzstruktur)):
        return einstellungen
    else:
        return None



# -------------------------------------------------------------------------------------------------
def _Betriebssystemspezifische_Einstellungen(einstellungen, programm, systembefehle):
    """Ergaenze die Struktur an uebergebenen Einstellungen mit betriebssystemspezifischen
    Einstellungen.
    """
    import platform

    einstellungen['Fortran'].update([('Endung', '.f')])

    if (platform.system() == 'Windows'):
        einstellungen.update([('System', 'win')])
        einstellungen.update([('Befehle', systembefehle['Windows'])])
        if (programm == 'abaqus'):
            einstellungen['Fortran'].update([('Endung', '.for')])

    elif (platform.system() == 'Linux'):
        einstellungen.update([('System', 'lnx')])
        einstellungen.update([('Befehle', systembefehle['Linux'])])
    else:
        print('# Abbruch: Betriebssystem nicht erkannt')
        return False

    return True



# -------------------------------------------------------------------------------------------------
def Einstellungen_Laden(programm):
    """Lese die relevanten Einstellungen aus den JSON-Dateien einstellungen.json und
    systembefehle.json ein und fuehre alle noetigen Anpassungen fuer den aktuellen Aufruf durch.
    """
    from .parameter import referenzeinstellungen, referenzbefehle

    einstellungen = _Einstellungen_Einlesen(dateiname='einstellungen.json',
        referenzstruktur=referenzeinstellungen)
    if (einstellungen is None):
        return False

    systembefehle = _Einstellungen_Einlesen(dateiname='systembefehle.json',
        referenzstruktur=referenzbefehle)
    if (systembefehle is None):
        return False

    if (not _Betriebssystemspezifische_Einstellungen(einstellungen=einstellungen,
        programm=programm, systembefehle=systembefehle)):
        return False

    return einstellungen



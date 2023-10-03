# -*- coding: utf-8 -*-
"""
__main__.py   v0.5
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


# Paketname muss explizit angegeben werden, wenn mit relativen Abhaengigkeiten gearbeitet wird.
# Diese sind wiederum fuer ein Laden der Bibliotheken aus einem zip-Archiv (.pyz) erforderlich
__package__ = 'ElementSimulator'


# -------------------------------------------------------------------------------------------------
def main(argumente):
    """Diese Funtion startet den Elementsimulator und ruft alle notwendigen Funktionen auf.
    """
    from .optionsverarbeitung import Optionen_verarbeiten
    from .einstellungsverarbeitung import Einstellungen_Laden
    from .parameter import Informationsausgabe
    from .programmsteuerung import Umgebung_Vorbereiten, Programmaufruf_Verarbeiten

    print('Starte ElementSimulator')

    optionen = Optionen_verarbeiten(argumente=argumente)
    if (optionen is None):
        return

    einstellungen = Einstellungen_Laden(programm=optionen['prog'])
    if (not einstellungen):
        return

    if (not Umgebung_Vorbereiten(einstellungen=einstellungen, versuch=optionen['test'],
        programm=optionen['prog'])):
        return

    if (not Informationsausgabe(einstellungen=einstellungen, optionen=optionen)):
        return

    Programmaufruf_Verarbeiten(einstellungen=einstellungen, optionen=optionen)



# -------------------------------------------------------------------------------------------------
import sys


if (sys.version_info[0] < 3):
    print('ElementSimulator benötigt mindestens Python3')
else:
    if (__name__ == '__main__'):
        main(sys.argv)
    else:
        main(sys.argv)


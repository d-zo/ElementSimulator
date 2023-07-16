# -*- coding: utf-8 -*-


# -------------------------------------------------------------------------------------------------
def DatenSpeichern(dateiname, session, xydatenname, nachkommastellen=6):
   """Speichert den Datensatz xydatenname des aktiven Viewports von session als csv-Datei dateiname.
   Optional kann die Anzahl an nachkommastellen angepasst werden.
   """
   from abaqusConstants import OFF
   #
   reportname = dateiname + '.csv';
   if isinstance(xydatenname, list):
      xyObject = [];
      for xydatensatz in xydatenname:
         xyObject += [session.xyDataObjects[xydatensatz]];
   else:
      xyObject = [session.xyDataObjects[xydatenname]];
   #
   session.xyReportOptions.setValues(numDigits=nachkommastellen);
   session.writeXYReport(fileName=reportname, appendMode=OFF, xyData=tuple(xyObject));
#

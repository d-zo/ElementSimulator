from odbAccess import *
from odbMaterial import *
from odbSection import *
from abaqusConstants import *
from visualization import *
from auswertungshilfe import DatenSpeichern


myviewport = session.viewports[session.currentViewportName];

filename = '--outfilename--'
odbfile = filename + '.odb';

odb = session.openOdb(name=odbfile);
steps = tuple(session.odbs[odbfile].steps.keys());

yy_stress = session.XYDataFromHistory(name='Vertical_Stress', odb=odb,
   outputVariableName='Stress components: S22 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );
voidratio = session.XYDataFromHistory(name='Voidratio', odb=odb,
   outputVariableName='Solution dependent state variables: SDV1 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );

temp = combine(-yy_stress, voidratio);
session.xyDataObjects.changeKey(fromName=temp.name, toName='Stress_Voidratio');

DatenSpeichern(filename, session, ['Stress_Voidratio']);
odb.close();
#

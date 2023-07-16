from odbAccess import *
from odbMaterial import *
from odbSection import *
from abaqusConstants import *
from visualization import *
from auswertungshilfe import DatenSpeichern


myviewport = session.viewports[session.currentViewportName];

shear_hoehe = 0.015;

filename = '--outfilename--';
odbfile = filename + '.odb';

odb = session.openOdb(name=odbfile);
steps = tuple(session.odbs[odbfile].steps.keys());

xx_displ = session.XYDataFromHistory(name='Horizontal_Displacement', odb=odb,
   outputVariableName='Spatial displacement: U1 at Node 4 in NSET SETOBERKANTE', steps=steps, );
yy_displ = session.XYDataFromHistory(name='Axial_Displacement', odb=odb,
   outputVariableName='Spatial displacement: U2 at Node 4 in NSET SETOBERKANTE', steps=steps, );
xx_stress = session.XYDataFromHistory(name='Horizontal_Stress', odb=odb,
   outputVariableName='Stress components: S11 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );
xy_stress = session.XYDataFromHistory(name='Shear_Stress', odb=odb,
   outputVariableName='Stress components: S12 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );
yy_stress = session.XYDataFromHistory(name='Vertical_Stress', odb=odb,
   outputVariableName='Stress components: S22 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );

temp = combine(100.0*xx_displ/shear_hoehe, 100.0*yy_displ/shear_hoehe);
session.xyDataObjects.changeKey(fromName=temp.name, toName='Shear_Strain_Axial');

temp = combine(100.0*xx_displ/shear_hoehe, xy_stress);
session.xyDataObjects.changeKey(fromName=temp.name, toName='Shear_Strain_Stress');

DatenSpeichern(filename, session, ['Shear_Strain_Axial', 'Shear_Strain_Stress']);
odb.close();
#

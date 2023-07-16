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

xx_stress = session.XYDataFromHistory(name='Horizontal_Stress', odb=odb,
   outputVariableName='Stress components: S11 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );
yy_stress = session.XYDataFromHistory(name='Vertical_Stress', odb=odb,
   outputVariableName='Stress components: S22 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );
xx_strain = session.XYDataFromHistory(name='Horizontal_Strain', odb=odb,
   outputVariableName='Strain components: E11 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );
yy_strain = session.XYDataFromHistory(name='Vertical_Strain', odb=odb,
   outputVariableName='Strain components: E22 at Element 1 Int Point 1 in ELSET SETELEMENT', steps=steps, );

temp = combine(100.0*yy_strain, 100.0*(yy_strain + 2.0*xx_strain));
session.xyDataObjects.changeKey(fromName=temp.name, toName='Strain_Vol_Strain');

temp = combine(100.0*yy_strain, xx_stress - yy_stress);
session.xyDataObjects.changeKey(fromName=temp.name, toName='Strain_Deviator_Stress');

DatenSpeichern(filename, session, ['Strain_Vol_Strain', 'Strain_Deviator_Stress']);
odb.close();

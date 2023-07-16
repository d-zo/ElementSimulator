# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
#
# Parameter
#
probenhoehe = --shear_height--;
probenradius = --shear_radius--;

anfangsspannung = --shear_pressure--;
scherfaktor = --shear_excitation--;
max_scherung = scherfaktor*probenhoehe;
zyklen = --shear_cycles--;
dichte_probenmaterial = --initialdensity--;

konstantes_volumen = 'nein';
#
userroutine = "--userroutine--";
hypoplastische_parameter = (--materialparameters--);
outputshalberzyklus = 100;
steptime = --sim_duration--;
#
# Modell
#
modelname = '--outfilename--';
#if (konstantes_volumen == 'ja'):
#   modelname = modelname + '_volkonst';
#else:
#   modelname = modelname + '_lastkonst';
#

mdb.Model(name=modelname, modelType=STANDARD_EXPLICIT);
mymodel = mdb.models[modelname];
#
# Part: Element
#
zeichnung = mymodel.ConstrainedSketch(name='__profile__', sheetSize=1.0);
zeichnung.rectangle(point1=(-probenradius, 0.0), point2=(probenradius, probenhoehe));
zeichnung.ObliqueDimension(textPoint=(0.0, -probenhoehe/2.0), value=2.0*probenradius,
   vertex1=zeichnung.vertices.findAt((-probenradius, 0.0)),
   vertex2=zeichnung.vertices.findAt((probenradius, 0.0)));
zeichnung.ObliqueDimension(textPoint=(3.0/2.0*probenradius, probenhoehe/2.0), value=probenhoehe,
   vertex1=zeichnung.vertices.findAt((probenradius, 0.0)),
   vertex2=zeichnung.vertices.findAt((probenradius, probenhoehe)));
partElement = mymodel.Part(dimensionality=TWO_D_PLANAR, name='Element', type=DEFORMABLE_BODY);
partElement.BaseShell(sketch=zeichnung);
del zeichnung;
#
Punkt_LO = partElement.vertices.findAt((-probenradius, probenhoehe, 0.0));
Punkt_RO = partElement.vertices.findAt((probenradius, probenhoehe, 0.0));
Punkt_LU = partElement.vertices.findAt((-probenradius, 0.0, 0.0));
Punkt_RU = partElement.vertices.findAt((probenradius, 0.0, 0.0));
#
partElement.Set(name='setUnterkante', vertices=[
   partElement.vertices[Punkt_LU.index:Punkt_LU.index+1] \
   + partElement.vertices[Punkt_RU.index:Punkt_RU.index+1]]);
partElement.Set(name='setOberkante', vertices=[
   partElement.vertices[Punkt_LO.index:Punkt_LO.index+1] \
   + partElement.vertices[Punkt_RO.index:Punkt_RO.index+1]]);
partElement.Set(name='setPunktLO', vertices=[partElement.vertices[Punkt_LO.index:Punkt_LO.index+1]]);
partElement.Set(name='setPunktRO', vertices=[partElement.vertices[Punkt_RO.index:Punkt_RO.index+1]]);
partElement.Set(faces=partElement.faces, name='setElement');
#
oberkante = partElement.edges.findAt((0.0, probenhoehe, 0.0));
partElement.Surface(name='surfOberkante',
   side1Edges=partElement.edges[oberkante.index:oberkante.index+1]);
#
# Material
#
mymodel.Material(name='--materialname--');
mymodel.materials['--materialname--'].Density(table=((dichte_probenmaterial, ), ));
mymodel.materials['--materialname--'].Depvar(n=20);
mymodel.materials['--materialname--'].UserMaterial(mechanicalConstants=hypoplastische_parameter);
mymodel.HomogeneousSolidSection(material='--materialname--', name='secElement', thickness=None);
partElement.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
   region=partElement.sets['setElement'], sectionName='secElement', thicknessAssignment=FROM_SECTION);
#
# Mesh
#
partElement.setElementType(elemTypes=(ElemType(elemCode=CPE4R, elemLibrary=EXPLICIT,
   secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT), ),
   regions=(partElement.sets['setElement']));
partElement.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=max(probenhoehe, 2*probenradius));
partElement.generateMesh();
#
# Assembly
#
mymodel.rootAssembly.DatumCsysByThreePoints(coordSysType=CYLINDRICAL,
   origin=(0.0, 0.0, 0.0), point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0));
instElement = mymodel.rootAssembly.Instance(dependent=ON, name='instElement', part=partElement);
#
# Initial Conditions
#
mymodel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM,
   fieldName='', localCsys=None, name='bcUnterkanteHalten',
   region=instElement.sets['setUnterkante'], u1=SET, u2=SET, ur3=UNSET);
if (konstantes_volumen == 'ja'):
   # Die Oberkante muss immer auf der gleichen Hoehenlinie bleiben
   mymodel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM,
      fieldName='', localCsys=None, name='bcAbscheren', region=instElement.sets['setOberkante'],
      u1=SET, u2=SET, ur3=UNSET);
else:
   # Oberkante kann die Hoehe variieren, aber beide Eckpunkte muessen die gleiche Hoehe haben
   mymodel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM,
      fieldName='', localCsys=None, name='bcAbscheren', region=instElement.sets['setOberkante'],
      u1=SET, u2=UNSET, ur3=UNSET);
   mymodel.Equation(name='ObereEbene', terms=((1.0, 'instElement.setPunktLO', 2),
      (-1.0, 'instElement.setPunktRO', 2)));
#
mymodel.GeostaticStress(lateralCoeff1=0.5, lateralCoeff2=None, name='Spannungszustand',
   region=instElement.sets['setElement'], stressMag1=anfangsspannung, stressMag2=anfangsspannung,
   vCoord1=0.0, vCoord2=probenhoehe);
#
# Step: Anfangsspannungszustand
#
mymodel.ExplicitDynamicsStep(name='Anfangszustand', previous='Initial',
   timePeriod=0.05, scaleFactor=0.2, nlgeom=OFF, linearBulkViscosity=0.42);
mymodel.steps['Anfangszustand'].Restart(overlay=ON, timeMarks=OFF);
mymodel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Feldausgabe');
mymodel.fieldOutputRequests['Feldausgabe'].setValues(variables=('U', 'E', 'S', 'SDV'), numIntervals=5);
mymodel.historyOutputRequests.changeKey(fromName='H-Output-1', toName='AusgabeElementverlauf');
mymodel.historyOutputRequests['AusgabeElementverlauf'].setValues(rebar=EXCLUDE, numIntervals=5,
   region=instElement.sets['setElement'], sectionPoints=DEFAULT,
   variables=('E11', 'E22', 'E12', 'S11', 'S22', 'S12', 'SDV'));
mymodel.HistoryOutputRequest(createStepName='Anfangszustand', name='AusgabeOberkante',
   numIntervals=5, rebar=EXCLUDE, region=instElement.sets['setOberkante'], sectionPoints=DEFAULT,
   variables=('U1', 'U2'));
mymodel.Pressure(amplitude=UNSET, createStepName='Anfangszustand', distributionType=UNIFORM,
   field='', name='Auflast', magnitude=-anfangsspannung,
   region=instElement.surfaces['surfOberkante']);
#
# Step: Abscheren1
#
thisstep = 'Abscheren1';
mymodel.ExplicitDynamicsStep(name=thisstep, previous='Anfangszustand', timePeriod=steptime,
   scaleFactor=0.2, nlgeom=OFF, linearBulkViscosity=0.42);
mymodel.steps[thisstep].Restart(overlay=ON, timeMarks=OFF);
mymodel.fieldOutputRequests['Feldausgabe'].setValuesInStep(stepName=thisstep,
   numIntervals=outputshalberzyklus);
mymodel.historyOutputRequests['AusgabeElementverlauf'].setValuesInStep(stepName=thisstep,
   numIntervals=outputshalberzyklus);
mymodel.historyOutputRequests['AusgabeOberkante'].setValuesInStep(stepName=thisstep,
   numIntervals=outputshalberzyklus);
verlauf = [(0.0, 0.0), (steptime, 1.0)];
mymodel.TabularAmplitude(data=tuple(verlauf), name='Verlauf', smooth=SOLVER_DEFAULT, timeSpan=STEP);
if (konstantes_volumen == 'ja'):
   mymodel.boundaryConditions['bcAbscheren'].setValuesInStep(stepName=thisstep, amplitude='Verlauf',
      u1=max_scherung, u2=0.0);
else:
   mymodel.boundaryConditions['bcAbscheren'].setValuesInStep(stepName=thisstep, amplitude='Verlauf',
      u1=max_scherung);
#
# Step: Laststufe
#
for izyklus in range(2, 2*zyklen + 2):
   laststep = thisstep;
   thisstep = 'Abscheren' + str(izyklus);
   mymodel.ExplicitDynamicsStep(name=thisstep, previous=laststep, timePeriod=steptime,
      scaleFactor=0.2, nlgeom=OFF, linearBulkViscosity=0.42);
   mymodel.steps[thisstep].Restart(overlay=ON, timeMarks=OFF);
   mymodel.fieldOutputRequests['Feldausgabe'].setValuesInStep(stepName=thisstep,
      numIntervals=outputshalberzyklus);
   mymodel.historyOutputRequests['AusgabeElementverlauf'].setValuesInStep(stepName=thisstep,
      numIntervals=outputshalberzyklus);
   mymodel.historyOutputRequests['AusgabeOberkante'].setValuesInStep(stepName=thisstep,
      numIntervals=outputshalberzyklus);
   if (konstantes_volumen == 'ja'):
      mymodel.boundaryConditions['bcAbscheren'].setValuesInStep(stepName=thisstep,
         amplitude='Verlauf', u1=(-1.0)**(izyklus + 1)*max_scherung, u2=0.0);
   else:
      mymodel.boundaryConditions['bcAbscheren'].setValuesInStep(stepName=thisstep,
         amplitude='Verlauf', u1=(-1.0)**(izyklus + 1)*max_scherung);
#
# Job
#
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE,
   getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=PERCENTAGE, model=modelname,
   modelPrint=OFF, multiprocessingMode=DEFAULT, name=modelname, nodalOutputPrecision=FULL,
   numCpus=1, numDomains=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS,
   userSubroutine=userroutine, waitHours=0, waitMinutes=0);
myjob = mdb.jobs[modelname];
#
# Nachbearbeitung im Schluesselworteditor
# (letzte Operation vor dem Schreiben der Input-Datei)
mymodel.keywordBlock.synchVersions(storeNodesAndElements=False);
for idx, text in enumerate(mymodel.keywordBlock.sieBlocks):
   # Kontakt ohne op=NEW
   if (text[0:19] == '*Initial Conditions'):
      # Fuer jeden der angeforderten SDV muss eine Loesung angegeben werden
      # In der inp-Datei duerfen nicht mehr als 8 Werte pro Zeile stehen!
      neuerBlock = '**\n*Initial Conditions, type=SOLUTION\ninstElement.setElement, ' \
         + '--initialvoidratio--, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0\n' \
         + ' 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0\n' \
         + ' 0.0, 0.0, 0.0, 0.0, 0.0';
      mymodel.keywordBlock.insert(idx, neuerBlock);
#

myjob.writeInput(consistencyChecking=OFF);

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
probenhoehe = --triax_height--;
probenradius = --triax_radius--;
spannung = --triax_pressure--;
scherweg = -probenhoehe*--triax_maxcontraction--;
dichte_probenmaterial = --initialdensity--;
#
userroutine = "--userroutine--";
hypoplastische_parameter = (--materialparameters--);
#
numoutputs = 100;
steptime = --sim_duration--;
#
# Modell
#
modelname = '--outfilename--';
mdb.Model(name=modelname, modelType=STANDARD_EXPLICIT);
mymodel = mdb.models[modelname];
#
# Part: Element
#
zeichnung = mymodel.ConstrainedSketch(name='__profile__', sheetSize=1.0);
zeichnung.sketchOptions.setValues(viewStyle=AXISYM);
zeichnung.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5));
zeichnung.FixedConstraint(entity=zeichnung.geometry.findAt((0.0, 0.0)));
zeichnung.rectangle(point1=(0.0, 0.0), point2=(probenradius, probenhoehe));
zeichnung.ObliqueDimension(textPoint=(probenradius/2, -probenhoehe/2), value=probenradius,
   vertex1=zeichnung.vertices.findAt((0.0, 0.0)),
   vertex2=zeichnung.vertices.findAt((probenradius, 0.0)));
zeichnung.ObliqueDimension(textPoint=(-probenradius/2, probenhoehe/2), value=probenhoehe,
   vertex1=zeichnung.vertices.findAt((0.0, 0.0)),
   vertex2=zeichnung.vertices.findAt((0.0, probenhoehe)));
partElement = mymodel.Part(dimensionality=AXISYMMETRIC, name='Element', type=DEFORMABLE_BODY);
partElement.BaseShell(sketch=zeichnung);
del zeichnung;
#
Punkt_MO = partElement.vertices.findAt((0.0, probenhoehe, 0.0));
Punkt_AO = partElement.vertices.findAt((probenradius, probenhoehe, 0.0));
Punkt_MU = partElement.vertices.findAt((0.0, 0.0, 0.0));
Punkt_AU = partElement.vertices.findAt((probenradius, 0.0, 0.0));
#
partElement.Set(name='setUnterkante', vertices=[
   partElement.vertices[Punkt_MU.index:Punkt_MU.index+1] \
   + partElement.vertices[Punkt_AU.index:Punkt_AU.index+1]]);
partElement.Set(name='setSymmetrieachse', vertices=[
   partElement.vertices[Punkt_MU.index:Punkt_MU.index+1] \
   + partElement.vertices[Punkt_MO.index:Punkt_MO.index+1]]);
partElement.Set(name='setOberkante', vertices=[
   partElement.vertices[Punkt_MO.index:Punkt_MO.index+1] \
   + partElement.vertices[Punkt_AO.index:Punkt_AO.index+1]]);
partElement.Set(faces=partElement.faces, name='setElement');
#
oberkante = partElement.edges.findAt((probenradius/2, probenhoehe, 0.0));
partElement.Surface(name='surfOberkante',
   side1Edges=partElement.edges[oberkante.index:oberkante.index+1]);
aussenkante = partElement.edges.findAt((probenradius, probenhoehe/2, 0.0));
partElement.Surface(name='surfAussenkante',
   side1Edges=partElement.edges[aussenkante.index:aussenkante.index+1]);
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
partElement.setElementType(elemTypes=(ElemType(elemCode=CAX4R, elemLibrary=EXPLICIT,
   secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT),
   ElemType(elemCode=CAX3, elemLibrary=EXPLICIT)), regions=(partElement.sets['setElement']));
partElement.seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=max(probenhoehe, probenradius));
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
   fieldName='', localCsys=None, name='bcUnterkante', region=instElement.sets['setUnterkante'],
   u1=UNSET, u2=SET, ur3=UNSET);
mymodel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM,
   fieldName='', localCsys=None, name='bcSymmetrieachse', region=instElement.sets['setSymmetrieachse'],
   u1=SET, u2=UNSET, ur3=UNSET);
#
mymodel.GeostaticStress(lateralCoeff1=1.0, lateralCoeff2=None, name='Spannungszustand',
   region=instElement.sets['setElement'], stressMag1=spannung, stressMag2=spannung, vCoord1=0.0,
   vCoord2=probenhoehe);
#
# Step: Anfangsspannungszustand
#
mymodel.ExplicitDynamicsStep(name='Anfangszustand', previous='Initial',
   timePeriod=0.05, scaleFactor=0.2, nlgeom=OFF, linearBulkViscosity=0.42);
mymodel.steps['Anfangszustand'].Restart(overlay=ON, timeMarks=OFF);
mymodel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Feldausgabe');
mymodel.fieldOutputRequests['Feldausgabe'].setValues(variables=('U', 'E', 'S', 'RF', 'SDV'),
   numIntervals=5);
mymodel.historyOutputRequests.changeKey(fromName='H-Output-1', toName='AusgabeElementverlauf');
mymodel.historyOutputRequests['AusgabeElementverlauf'].setValues(rebar=EXCLUDE, numIntervals=5,
   region=instElement.sets['setElement'], sectionPoints=DEFAULT,
   variables=('E11', 'E22', 'S11', 'S22', 'RF1', 'RF2', 'SDV'));
mymodel.HistoryOutputRequest(createStepName='Anfangszustand', name='AusgabeOberkante',
   numIntervals=5, rebar=EXCLUDE, region=instElement.sets['setOberkante'], sectionPoints=DEFAULT,
   variables=('U1', 'U2'));
mymodel.Pressure(amplitude=UNSET, createStepName='Anfangszustand', distributionType=UNIFORM,
   field='', name='SpannungOben', magnitude=-spannung, region=instElement.surfaces['surfOberkante']);
mymodel.Pressure(amplitude=UNSET, createStepName='Anfangszustand', distributionType=UNIFORM,
   field='', name='SpannungAussen', magnitude=-spannung,
   region=instElement.surfaces['surfAussenkante']);
#
# Step: Belastung
#
mymodel.ExplicitDynamicsStep(name='Belastungsgeschichte', previous='Anfangszustand',
   timePeriod=steptime, scaleFactor=0.2, nlgeom=OFF, linearBulkViscosity=0.42);
mymodel.steps['Belastungsgeschichte'].Restart(overlay=ON, timeMarks=OFF);
mymodel.fieldOutputRequests['Feldausgabe'].setValuesInStep(stepName='Belastungsgeschichte',
   numIntervals=numoutputs);
mymodel.historyOutputRequests['AusgabeElementverlauf'].setValuesInStep(stepName='Belastungsgeschichte',
   numIntervals=numoutputs);
mymodel.historyOutputRequests['AusgabeOberkante'].setValuesInStep(stepName='Belastungsgeschichte',
   numIntervals=numoutputs);
mymodel.TabularAmplitude(name='Verlauf', timeSpan=STEP, smooth=SOLVER_DEFAULT,
   data=((0.0, 0.0), (steptime, 1.0)));
mymodel.DisplacementBC(amplitude='Verlauf', createStepName='Belastungsgeschichte',
   distributionType=UNIFORM, fieldName='', localCsys=None, name='bcAbscheren',
   region=instElement.sets['setOberkante'], u1=UNSET, u2=scherweg, ur3=UNSET);
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

@echo off
rem @call ifortvars.bat intel64 vs2015
@call "C:\Path\to\Intel\oneAPI\compiler\latest\env\vars.bat" intel64 vs2019

rem C:\Path\to\Python\python.exe ElementSimulator.pyz -test=triax -prog=abaqus -zusatz=normal
C:\Path\to\Python\python.exe ElementSimulator.pyz -test=triax -prog=fortran -zusatz=normal
rem C:\Path\to\Python\python.exe ElementSimulator.pyz -test=oedo -prog=abaqus -zusatz=normal
C:\Path\to\Python\python.exe ElementSimulator.pyz -test=oedo -prog=fortran -zusatz=normal
rem C:\Path\to\Python\python.exe ElementSimulator.pyz -test=scher -prog=abaqus -zusatz=normal
C:\Path\to\Python\python.exe ElementSimulator.pyz -test=impuls -prog=fortran -zusatz=normal
C:\Path\to\Python\python.exe ElementSimulator.pyz -test=pfade -prog=fortran -zusatz=normal
C:\Path\to\Python\python.exe ElementSimulator.pyz -test=ellipsen -prog=fortran -zusatz=normal
pause

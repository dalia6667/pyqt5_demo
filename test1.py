import vmtk
from vmtk import pypes

vmtkCommand = '''vmtksurfaceviewer -ifile KONG.stl    
--pipe vmtksurfaceclipper -ofile vessel_cut.vtp    
--pipe vmtkcenterlines -ofile vessel.vtk    
--pipe vmtkrenderer    
--pipe vmtksurfaceviewer -opacity 0.25    
--pipe vmtksurfaceviewer -i @vmtkcenterlines.o -array MaximumInscribedSphereRadius'''

# 执行vmtk命令
pype = pypes.PypeRun(vmtkCommand)


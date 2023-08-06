# TESTKODE FOR UTPRØVING AV NY SYNTAKS
from astronomi import Tyngdekraft
from numpy import array, random, sin, cos, pi, sqrt
modell = Tyngdekraft(L=20.0,dt=0.01,tittel="Lek med kollisjoner (testkode)")
modell.nyttObjekt([0,0],[0,0],100.)
#modell.nyttObjekt([-4.0,0],[0,2.0],10.)
#modell.nyttObjekt([+8.0,0],[0,-0.0],10.)
for i in range(500): 
    masse     = random.uniform(1.0,1.5) 
    avstand   = random.uniform(2.0,8.0)
    vinkel    = random.uniform(0.0,2.0*pi)
    fart      = 16.0*masse/avstand**1.1
    posisjon  = array([avstand*cos(vinkel), avstand*sin(vinkel)])
    hastighet = array([fart*sin(vinkel), -fart*cos(vinkel)])
    modell.nyttObjekt(posisjon, hastighet, masse)

modell.start()



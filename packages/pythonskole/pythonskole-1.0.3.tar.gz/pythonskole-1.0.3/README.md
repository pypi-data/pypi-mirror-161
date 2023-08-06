# Pythonskole
## Koding med mening

# Installer

For å installere siste versjon av kodebiblioteket, bruk pip fra din Python-konsoll eller kommandolinjevindu. 

	pip install pythonskole


Om du allerede har installert pythonskole-biblioteket, kan du oppgradere til siste versjon med

	pip install --upgrade pythonskole


# Eksempler

## Tyngdekraft
Kodeeksempler med Tyngdekraft-modulen

	from pythonskole.astronomi import Tyngdekraft
	modell = Tyngdekraft(L=10.0,tittel="Ellipse")
	#Nytt objekt i origo, med null hastighet og masse=500. 
	modell.nyttObjekt([0,0],[0,0],500.) 
	#Nytt objekt til venstre for origo og hastighet i y-retning og masse=10
	modell.nyttObjekt([-5.0,0],[0,2.0],10.) 
	modell.start()

#Mer informasjon 
Les mer på [pythonskole.no] for eksempler og forklaring på disse kodene. Du kan også lese og laste ned kodene på [github.com]. 

[//]: # 
   [pythonskole.no]: <https://pythonskole.no>
   [github.com]: <https://github.com/vegardlr/pythonskole.git>

BEDIENUNGSANLEITUNG 

---INSTALLATION----
- gehe in die Eingabeaufforderung
- gebe ein <pip install monke2>
- um das Paket in ein Python Notebook einzubinden gebe ein <import monke> 



----Geraden-Fits----

- Als erstes muss ein Objekt linear_fit() definiert werden 
- anschließend muss der y-Fehler mit set_y_error() definiert werden
- mit der funktion make_fit() kann ein Geraden-Fit erstellt werden

Beispiel code:
----------------------------------
from monke.fit import linear_fit

myfit = linear_fit()
myfit.set_y_error(y_err)
result = myfit.make_fit(x, y)

myfit.plot()
----------------------------------

--Variablen--
Variablen gehören alle zum Objekt linear_fit()
Beispiel (änderen den Wert der Variable var):
-----------------------
myift = linear_fit()
myfit.var = 1
----------------------
Dieses Schema gilt für alle Variablen:

- detail: (boolean), bei True werden extra-infos ausgegeben, bei False nicht
- m_round: (integer), gibt an, auf welche Nachkommastelle die Steigung m gerundet wird
- n_round: (integer), gibt an, auf welche Nachkommastelle der Achsenabschnitt n gerundet wird
- textloc: (string), bestimme, in welche Ecke der Infokasten des Graphen gesetzt wird. 
    -verfügbare Optionen: 'upper right', 'upper left', 'lower right', 'lower left'
- plotsize: (tupel), bestimme die Größe des Diagramms
- errbar: (5d List [marker, caps, eline, markerwidth, shape]), 5 Parameter die das Aussehen der Fehlerbalken ändern
    - MARKER: (float), ändere die Größe der marker der Fehlerbalken
    - CAPS: (float), ändere die Länge der oberen und unteren Striche der Fehlerbalken
    - ELINE: (float), ändere die Dicke der Fehlerbalken
    - MARKERWIDTH: (float), ändere die Dicke der oberen und unteren Striche der Fehlerbalken
    - SHAPE: (string), ändere die Form der Fehlerbalken
        - 's' für Quadrat
        - 'o' für Kreis
        - 'd' für Raute
        - 'x' für x
        - 'v' für Dreieck
- ANCH: (float), ändere die Größe der Infobox
- style: (string oder string-Liste), ändert den Style des Diagramms
- size: (float), ändert die Schriftgrößen im Diagramm
- colors: (4d list [string, stringt, string, string]), ändert die Farben im Diagramm
    - 0: Fehlerbalken
    - 1: Fit-Geraden
    - 2: Fehlerkurven
    - 3: Füllraum
- xlim und ylim: (tupel), setzt die Grenzen der x- oder y-Achse

--Funktionen--
Funktionen gehören zum Objekt linear_fit()

- set_y_error(yerr,var=True): setze den y-Fehler. yerr kann ein Array oder eine Zahl sein. Wenn var==True, dann wird
     varianzgewichtet gerechnet
- set_x_error(xerr): setze den x-Fehler. wird automatisch varianzgewichtet
- make_fit(x_vals,y_vals,r=2,str='', hide=False) wertet die xy-Werte aus. r beschreibt die Nachkommastelle, auf die gerundet wird. Mit 
    str lässt sich zur Übersicht der Name des Fits definieren, hide versteckt die Ergebnisausgabe (nützlich für Multiplot)
- plot(title='title',xlabel='x_Achse',ylabel='y_achse',err=True, save = False, name): 
    bei err=True werden Fehlerbalken eingefügt, bei save=True wird das Diagramm gespeichert, name ist der Name der Datei

----Multi-Plots----

- Damit man mehrere Fits im selben Diagramm plotten kann benutzt man die Klasse multiplot().
hierbei erstellt man erst das Objekt <multi>, gibt die Anzahl der Plots an, wertet alle Geraden-fits mit einer 
for-Schleife aus und gibt diese Werte an das Objekt <multi> mit der Funktion <set_result()> weiter.

Beispiel code:
----------------------------------------- 
multi = multiplot()
multi.plotcount(num)

for i in range(num):
    myfit = linear_fit()
    myfit.set_y_error(yerr)
    result = myfit.make_fit(x, y)
    
    multi.set_result(result,i)
    
multi.plot()
-----------------------------------------

--Variablen--
funktioniert wie bie linear_fit() (siehe oben):
- plotsize: (tupel), bestimme die Größe des Diagramms
- errbar: (4d List [marker, caps, eline, markerwidth]), 4 Parameter die das Aussehen der Fehlerbalken ändern
    - MARKER: (float), ändere die Größe der marker der Fehlerbalken
    - CAPS: (float), ändere die Länge der oberen und unteren Striche der Fehlerbalken
    - ELINE: (float), ändere die Dicke der Fehlerbalken
    - MARKERWIDTH: (float), ändere die Dicke der oberen und unteren Striche der Fehlerbalken
- shapes: (string-list), ordnet jedem Plot eine Form der Markierungen der Fehlerbalken zu (muss selbe Dimension wie Plotanzahl haben)
- style: (string oder string-Liste), ändert den Style des Diagramms
- size: (float), ändert die Schriftgrößen im Diagramm
- color: (string-list), eine Liste, die jedem Plot eine Farbe zuordnet
- label: (string-list), eine Liste mit allen Labelbezeichnungen
- xlim und ylim: (tupel), setzt die Grenzen der x- oder y-Achse

--Funktionen--
- plotcount(num): gibt dem Objekt die Anzahl der Plots an
- set_result(result, i): fügt in ein Array an der Stelle i die Ergebnisse eines Geradenfits ein 
    mit result = linear_fit().make_fit()
- plot(title, xlabel, ylabel, save = False, name): plottet die Graphen, bei save=True wird das Diagramm gespeichert, name ist der Name der 
    Datei

----Konstanten----
mit <monke.constants> kann man Konstanten eingeben 

-- Liste aller Konstanten --
-----------------------------------------
c   # Lichtgeschwindigkeit
q   # Elementarladung
mu0 # Magnetische Feldkonstante
e0  # Elektrische Feldkonstante
kc  # Coulomb-Konstante
h   # Planckes Wirkungsquantum
G   # Gravitationskonstante
m_planck  # Planck Masse
l_planck  # Planck Länge
t_planck  # Planck Zeit
T_planck  # Planck Temperatur
kb    # Boltzmann Konstante
sb    # Stefan Boltzmann Konstante
me    # Elektronenmasse
lc    # Compton Wellenlänge
re    # klassischer Elektronenradius
R_inf # Rydberg konstante
R_c   # Rydberg Frequenz
N_A   # Avogadro Konstante
F     # Faraday Konstante
R     # Gaskonstante
Vm0   # Molares Volumen eines idealen Gases
g     # Erdbeschleunigung
u     # atomare Masseneinheit
-----------------------------------------
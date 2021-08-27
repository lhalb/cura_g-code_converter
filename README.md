# Cura G-Code Konverter
Konvertiert _.gcode_-Dateien aus Cura zu _PATHCODE.MPF_ Dateien.
Der Name der G-Code Datei muss eigegeben werden.

Der erzeugte G-Code wird aus dem Hauptprogramm (s. data/mainprog.MPF) mit einem Sprungziel aufgerufen.
Das Sprungziel ist die Sprungmarke _EB_PATH_xx_, die für jeden Layer erzeugt wird. 
So kann bei einer beliebigen Schicht begonnen werden. 
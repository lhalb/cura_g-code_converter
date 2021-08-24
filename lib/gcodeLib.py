import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def clear_data(path, start=";MESH", end=';TIME_ELAPSED', cut=None):
    """
    
    :param path: Pfad zur G-Code-Datei
    :param start: Teilstring, der den Beginn der Daten markiert (wird übersprungen)
    :param end: Teilstring, der das Ende der Daten markiert
    :param cut: String, der aus den Daten gelöscht werden soll
    :return: Stringliste, die nur G-Code Anweisungen enthält
    """
    # öffne die Datei zeilenweise
    with open(path) as file:
        # entferne die Zeilenumbrüche
        raw_lines = [f.strip('\n') for f in file.readlines()]

    # finde den Startpunkt des G-Codes
    start_idx = [raw_lines.index(i) for i in raw_lines if start in i][0]
    # finde das Ende des G-Codes
    end_idx = [raw_lines.index(i) for i in raw_lines if end in i][0]

    # trimme die Daten
    cut_lines = raw_lines[start_idx+1: end_idx]

    # lösche die Typenbezeichnungen
    if cut is None:
        uncommented_lines = cut_lines
    else:
        uncommented_lines = [i for i in cut_lines if all(c not in i for c in cut)]

    return uncommented_lines


def import_data_pandas(path):
    df = pd.read_csv(path, sep=" ", comment=';', header=None)
    return df


def lines_to_array(lines, z_to_zd=False, r=0, offset=-0.5):
    if z_to_zd:
        z_out = 'ZD'
    else:
        z_out = 'Z'
    possible_axes = {
        'X': 'X',
        'Y': 'Y',
        'Z': z_out,
        'E': 'E'
    }

    output_data = {k: [0]*len(lines) for k in possible_axes.keys()}

    for i, line in enumerate(lines):
        current_line = line.split(' ')
        for string in current_line:
            for key in possible_axes.keys():
                if key in string:
                    value = string.strip(key)
                    output_data[key][i] = value

    df = pd.DataFrame(output_data, dtype='float64')

    for c in df.columns:
        if c != 'F':
            df[f'd{c}'] = np.ediff1d(df[c], to_begin=0)

    df['PHI'] = np.arctan(df['dY']/df['dX'])

    df['SV'] = r * np.sin(df['PHI']) + offset
    df['SU'] = r * np.cos(df['PHI']) + offset

    return df


def inspect_data(data, start=0, stop=-1):
    fig, ax = plt.subplots()
    x = data.index[start:stop]
    y1 = data['dX'][start:stop]
    y2 = data['dY'][start:stop]
    ax.plot(x, y1)
    ax.plot(x, y2, 'g-')
    ax.set_ylabel('dX, dY')

    secax = ax.twinx()
    y3 = data['dG'][start:stop]
    secax.scatter(x, y3, s=2, edgecolor='r')
    secax.set_ylabel('dG')
    secax.set_ylim([-3, 3])

    plt.show()


def plot_points(df):
    fig, ax = plt.subplots()
    ax.plot(df['X'], df['Y'])
    ax.scatter(df['X'], df['Y'])

    plt.show()


def plot_arrows(df, points=None, plot_susv=False):
    fig, axs = plt.subplots(2)
    if points is None:
        pass
    else:
        for x, y in points:
            plt.scatter(x, y, s=50)

    axs[0].quiver(df['X'], df['Y'], df['dX'], df['dY'], angles='xy', scale_units='xy', scale=1, pivot='tip')

    axs[1].scatter(df['SU'], df['SV'], s=30)

    plt.show()


def write_header():
    string = \
    '''
    ;EBA_Cura
    ;Version 1.02
    ;Stand: 17.08.2021
    ;Ersteller: Hengst
    
    ;-------------Programmhinweise-----------------
    ;Programmcode geht vom Modellmittelpunkt aus 
    ;--> aktuelle Tischposition wird Modellmittelpunkt!
    ;Arbeitsfeldbegrenzung beachten! (sollte eigentlich vorausberechnet werden)
    ;Die Verfahrgeschwindigkeiten und die Layerhoehen sind im Cura festzulegen!
    ;Downslope ohne Z-Verfahrbefehl
    
    ;-------------Definitionsbereich---------------
    DEF REAL _SLoff, _v, _UpS, _DoS, _vD ,_Hd, _XSTART, _YSTART 
    DEF REAL _ZSTART, _ZDSTART, _SQb, _vs, _Rueck, _DRueck, _tups, _tdos
    DEF INT  _KWH
    
    DEF BOOL _POSITIONIEREN = 1        ;1 = Positionierung nutzen
    ;_Layer = 0                        ;0 Neustart, 1,2,... Start bei Layer n
    ;ist noch nicht implementiert
    
    ;=================== Prozessparameter ======================
    ;EB-Parameter
    _SQH = 45           ;Strahlstrom  Behandlung [mA]
    _SLH = 1650          ;Linsenstrom  Behandlung [mA]
    _SLoff = 0           ;Linsenoffset Behandlung [mA]
    _vs   = 15           ;wird nicht verwendet!!! Vorschubgeschwindigkeit [mm/s]
    _SWXs= 1             ;Feldgroesse X
    _SWYs= 1             ;Feldgroesse Y
    _UpS = 0             ;Upslope [mm]
    _DoS = 0             ;Downslope [mm]
    _tups= 0.25          ;Ausgleichzeit Upslope [s]
    _tdos= 0.25          ;Ausgleichzeit Downslope [s]
    
    ;Draht-Parameter
    _Hd  = 0.8            ;Hoehedifferenz von Lage zu Lage [mm]
    _vD  = 2.5              ;Vorschubges. Draht [m/min]
    _DRueck = 4           ;Drahtrückzug in [mm] ueber _vD berechnet
    
    ;Beobachten-Parameter
    _SQb = 1              ;Beobachten Strahlstrom [mA]
    _SLb = 1675           ;Beobachten Linsenstrom [mA]
    
    ;Allgemeine-Parameter
    _KWH = 3425           ;Kalibrierwert
    _HV = 60              ;Hochspannung [kV]
    _FP = 20              ;Positionierungsgeschwindigkeit [mm/s]
    
    ;=================== Hauptprogramm ======================
    INITIAL
    KALWERT(_KWH)
    
    ;-- Abarbeiten der Layer--
    ;FOR _LAYERZAHL = 1 TO _LAYER
    ;REPEAT Layer"<<_TEILE<<"
    ;ENDFOR
    
    _Rueck = (_DRueck/1000)/(_vD*60)
    
    ;-------Positionierung des Modelmittelpunktes------------
    IF _POSITIONIEREN == 1
    
    MSG("Mittelpunkt des Modells positionieren und [Cycle Start] druecken!")
    WRT (B_SWX,20,B_SL,_SLb,Auff,1)
    SNS
    
    ELO_EIN(22)
    G4 F0.5
    G0 SQ _SQb) SL _SLb)
    
    HDWS_X
    HDWS_Y
    MSG()
    
    SQ 0)
    ELO_AUS
    
    ENDIF
    
    ;Istwertuebergabe von der aktuellen Position!
    _XSTART=$AA_IM[X]      ;X-Istwertuebernahme
    _YSTART=$AA_IM[Y]      ;Y-Istwertuebernahme
    _ZSTART=$AA_IM[Z]      ;Z-Istwertuebernahme
    _ZDSTART=$AA_IM[ZD]    ;ZD-Istwertuebernahme
    
    M96
    
    ;--------EB-Figur laden------------
    
    ;Parametrieren Hauptfigur
    WRT(S_FIG,7,S_FRQ,3700,S_SWX,_SWXs,S_SWY,_SWYs)
    SNS
    VEKTOR_XY
    
    ;Nullpunktverschiebung
    G17 G55
    TRANS X=_XSTART Y=_YSTART
    
    ;---------------Hauptteil-------------------
    M00
    ;Hier startet das Cura Programm
    
    
    
    '''
    return string


def write_gcode(df):
    return
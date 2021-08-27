import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def clear_data(path, start="M107", end='M82', cut=None):
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
    end_idx = [raw_lines.index(i, start_idx) for i in raw_lines if end in i][0]

    # trimme die Daten
    cut_lines = raw_lines[start_idx+1: end_idx]

    skirts = [i for i, x in enumerate(cut_lines) if x == ';TYPE:SKIRT']
    outer_walls = [i for i, x in enumerate(cut_lines) if x == ';TYPE:WALL-OUTER']

    if skirts:
        print(skirts)
        # falls es mehrere Skirtsa gibt, müsste man die Routine hier anpassen
        del cut_lines[skirts[0]:outer_walls[0]]

    # lösche die Typenbezeichnungen
    if cut is None:
        uncommented_lines = cut_lines
    else:
        uncommented_lines = [i for i in cut_lines if all(c not in i for c in cut)]

    cleared_lines = [l for l in uncommented_lines if l != '']

    return cleared_lines


def import_data_pandas(path):
    df = pd.read_csv(path, sep=" ", comment=';', header=None)
    return df


def lines_to_array(lines, z_to_zd=False, r=0.5, offset=0):
    if z_to_zd:
        z_out = 'ZD'
    else:
        z_out = 'Z'
    possible_axes = {
        'G': 'G',
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

    df['CNC'] = lines

    df['PHI'] = np.arctan(df['dY']/df['dX'])

    df['SV'] = np.round(r * np.sin(df['PHI']) + offset, 3)
    df['SU'] = np.round(r * np.cos(df['PHI']) + offset, 3)

    df = df.fillna(0)

    return df


def inspect_data(data, start=0, stop=-1):
    fig, ax = plt.subplots()
    x = data.index[start:stop]
    y1 = data['dX'][start:stop]
    y2 = data['dY'][start:stop]
    ax.plot(x, y1, label='X-Werte')
    ax.plot(x, y2, 'g-', label='Y-Werte')
    ax.set_ylabel('dX, dY')

    secax = ax.twinx()
    y3 = data['dG'][start:stop]
    secax.scatter(x, y3, s=2, edgecolor='r', label='G-Werte')
    secax.set_ylabel('dG')
    secax.set_ylim([-3, 3])

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = secax.get_legend_handles_labels()

    ax.legend(h1+h2, l1+l2)

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


def get_jumpmarkers(s):
    inds = []
    for i in s.index:
        if s[i] != 0:
            inds.append(i)

    return inds

def write_gcode(outpath, df, slopes=True,
                up_name='REPEAT UPSLOPE ENDLABEL', down_name='REPEAT DOWNSLOPE ENDLABEL',
                marker_name='EB_PATH'):
    def get_string(a, b, c, d, e):
        if e != 0:
            return f'G1 X={a} Y={b} SU={c} SV={d} Z={e}'
        else:
            return f'G1 X={a} Y={b} SU={c} SV={d}'

    stringliste = [get_string(x, y, su, sv, z) for x, y, su, sv, z in zip(df['X'], df['Y'], df['SU'], df['SV'], df['Z'])]
    jump_idx = get_jumpmarkers(df['Z'])
    if slopes:
        slope_pos, slope_label = find_slope_indices(df['E'].values)

        corr_idx = 0
        for idx in df.index:
            for i, s in enumerate(slope_pos):
                if idx == s:
                    if slope_label[i] == 'UP':
                        stringliste.insert(idx + 1 + corr_idx, up_name)
                    else:
                        stringliste.insert(idx + corr_idx, down_name)
                    corr_idx += 1

            for j, z in enumerate(jump_idx):
                if idx == z:
                    if j == 0:
                        stringliste.insert(idx - 1 + corr_idx, f'{marker_name}_{j}:')
                    else:
                        stringliste.insert(idx - 1 + corr_idx, f'RET\n{marker_name}_{j}:')
                    corr_idx += 1

    stringliste.insert(0, 'PROC PATHCODE (INT _DEST)\nGOTOF _DEST')
    stringliste.extend(['\nRET'])
    stringliste.append(codes_for_up_and_downslope())

    with open(outpath, "w") as outfile:
        outfile.write("\n".join(stringliste))

    return stringliste

def codes_for_up_and_downslope():
    txt = """
;---------------Upslope-------------------
UPSLOPE:
MSG("Beginn Layer n mit [Cycle Start]")
M00
MSG("Layer n wird aufgebaut")

;Upslope und Draht foerdern
G0 G90 SQ _SQH) SL _SLH)
M61                    ;Draht ein                       
G0 G90 VD2=(_vD) 
G4 F _tups             ;Upslopefehler ausgleichen

RET

;---------------Downslope-------------------
DOWNSLOPE:
;Draht abstellen und Downslope ohne Z-Verfahrbefehl           

G4 F _tdos             ;Downslopefehler ausgleichen
M62                    ;Draht aus
G0 G90 SQ 0) SL _SLb)  ;Strahlstrom aus

RET
    """
    return txt

def find_slope_indices(s):
    def has_neighbours(liste, el):
        if liste[el] - 1 in liste and liste[el] + 1 in liste:
            return True
        else:
            return False

    all_indices = list(np.where(s == 0)[0])

    to_delete = []

    for i, idx in enumerate(all_indices):
        if has_neighbours(all_indices, i):
            to_delete.append(idx)

    for i in to_delete:
        all_indices.remove(i)

    slope_types = get_up_and_downslope_list(all_indices)

    return all_indices, slope_types

def get_up_and_downslope_list(slopelist):

    if len(slopelist) %2 != 0:
        print(f'Slopes bei: {slopelist}')
        print('Es wird nicht mit einem Downslope geendet!\nDaten prüfen')
        return
    else:
        outlist = ['DOWN'] * len(slopelist)

        even_idx = [i for i in range(len(slopelist)) if (i % 2) == 0]

        for i in even_idx:
            outlist[i] = 'UP'

        return outlist


from lib import gcodeLib as gcL

from math import ceil

if __name__ == '__main__':
    fname = 'data/hex2.gcode'
    # fname = 'data/Kreistest.gcode'

    outname = 'data/PATHCODE.MPF'

    versatz = 1.0

    scale_factor = 0.6

    cleared_nc_code = gcL.clear_data(fname, cut=['TYPE', 'LAYER', 'MESH', 'TIME', 'G92'])

    # print(cleared_nc_code)

    df = gcL.lines_to_array(cleared_nc_code, r=versatz)

    # print(gcL.get_jumpmarkers(df['Z']))

    gcL.write_gcode(outname, df, scaling=scale_factor)

    print('Datei erfolgreich erstellt')

    x_breite = ceil((df["X"].max()-df["X"].min())*scale_factor)
    y_breite = ceil((df["Y"].max()-df["Y"].min())*scale_factor)

    print(f'Das Arbeitsfeld sollte mindestens {x_breite}x{y_breite} mm^2 groß sein')


    # gcL.inspect_data(df)

    # gcL.plot_points(df)

    # interesting_points = [(-13.094, 99.366), (100.255, 106.5), (100.255, 26.051)]

    # gcL.plot_arrows(df, plot_susv=False)

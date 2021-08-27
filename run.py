from lib import gcodeLib as gcL

if __name__ == '__main__':
    fname = 'data/EVT_v4.gcode'
    # fname = 'data/Kreistest.gcode'

    outname = 'data/PATHCODE.MPF'

    versatz = 0.5

    cleared_nc_code = gcL.clear_data(fname, cut=['TYPE', 'LAYER', 'MESH', 'TIME', 'G92'])

    # print(cleared_nc_code)

    df = gcL.lines_to_array(cleared_nc_code, r=versatz)

    # print(gcL.get_jumpmarkers(df['Z']))

    gcL.write_gcode(outname, df)


    # gcL.inspect_data(df)

    # gcL.plot_points(df)

    # interesting_points = [(-13.094, 99.366), (100.255, 106.5), (100.255, 26.051)]

    # gcL.plot_arrows(df, plot_susv=True)

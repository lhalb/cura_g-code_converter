import matplotlib.pyplot as plt

from lib import gcodeLib as gcL

if __name__ == '__main__':
    fname = 'data/Kreistest.gcode'

    versatz = 0.5

    cleared_nc_code = gcL.clear_data(fname, cut=['TYPE', 'LAYER'])

    df = gcL.lines_to_array(cleared_nc_code, r=versatz)

    print(df.head())

    # gcL.inspect_data(df)#, 330, 370)

    # gcL.plot_points(df)

    # interesting_points = [(-13.094, 99.366), (100.255, 106.5), (100.255, 26.051)]

    gcL.plot_arrows(df, plot_susv=True)

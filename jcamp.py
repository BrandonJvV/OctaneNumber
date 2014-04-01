#!/usr/bin/env python

from matplotlib.pylab import *

def read_jcamp(filename):
    d = {}
    endtags = ['XYDATA']
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith('##'):
                tag, value = line[2:].split('=')
                try:
                    d[tag] = float(value)
                except:
                    d[tag] = value
            elif tag not in endtags:
                value += ' ' + line
            if tag in endtags:
                break
        data = loadtxt(f)
        xdata = arange(d['FIRSTX'], d['LASTX']+d['DELTAX'], d['DELTAX'])
        ydata = data[:, 1:].flatten()*float(d['YFACTOR'])
        
        d['XDATA'] = xdata
        d['YDATA'] = ydata
        
        return d

def plotdata(d):
    d = read_jcamp(filename)
    plot(d['XDATA'], d['YDATA'])
    xlabel(d['XUNITS'])
    ylabel(d['YUNITS'])
    title(d['TITLE'])
    xlim([d['MINX'], d['MAXX']])
    ax = gca()
    grid()
    ax.invert_xaxis()


if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:]:
        d = read_jcamp(filename)
        plotdata(d)
        savefig(d['TITLE'] + '.pdf')
        close()

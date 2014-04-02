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
        yvalues = []
        N = int(ceil((d['LASTX'] - d['FIRSTX'])/d['DELTAX']))
        d['XDATA'] = arange(N)*d['DELTAX'] + d['FIRSTX']
        for line in f: # now read the data
            if not line.startswith("#"):
                linevalues = map(float, line.strip().split())
                yvalues += linevalues[1:]
        d['YDATA'] = array(yvalues[:N])*float(d['YFACTOR'])
        assert len(d['XDATA']) == len(d['YDATA']), "X and Y values don't match: %i != %i" % (len(d['XDATA']), len(d['YDATA']))
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
    import os.path
    for filename in sys.argv[1:]:
        print filename
        d = read_jcamp(filename)
        root, ext = os.path.splitext(filename)
        picname = "%s_%s.pdf" % (root, d['TITLE'])
        if not os.path.exists(picname):
            plotdata(d)
            savefig(picname)
            close()

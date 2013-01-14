#! /usr/bin/env python2 

import ConfigParser, sys
import numpy as np
import matplotlib.pyplot as plt

conf = sys.argv[1:]
config = ConfigParser.SafeConfigParser()
config.read(conf)

conv = {0 : lambda a: float(a)/1000}  # Convert first column from mm to m

print config.sections()
for i, section in enumerate(config.sections()):
    plt.subplot(np.ceil(len(config.sections())/2.0), 2, i+1)
    plt.grid(True)

    plt.title(section)
    exp = config.get(section, "exp")
    sim = config.get(section, "sim")
    print "Loading from %s and %s" % (exp, sim)
    
    sim = np.loadtxt(sim, usecols = (0, 2))
    exp = np.loadtxt(exp, converters=conv)

     # Move the first column
    sim[:,0] += config.getfloat(section, "sim_x_offset")

    # Delete values greater than y_max
    y_max = config.getfloat(section, "y_max")
    sim = np.compress(sim[:,0] < y_max, sim, axis=0)
    exp = np.compress(exp[:,0] < y_max, exp, axis=0)

    plt.plot(sim[:,0], sim[:,1])
    plt.plot(exp[:,0], exp[:,1], "-x")

plt.show()
                 

#! /usr/bin/env python2 

import ConfigParser, sys
import numpy as np
import matplotlib.pyplot as plt

class Options : pass

def read_options(config, section):
    o = Options()

    o.exp = config.get(section, "exp") # File with experimental data
    o.sim = config.get(section, "sim") # data from simulation
    
    o.u_exp_col = config.getint(section, "u_exp_column")
    o.z_exp_col = config.getint(section, "z_exp_column")
    o.x_exp_col = config.getint(section, "x_exp_column")

    o.u_sim_col = config.getint(section, "u_sim_column")
    o.z_sim_col = config.getint(section, "z_sim_column")
    
    o.u_exp_norm_col = config.getint(section, "u_exp_norm_column")
    
    o.u_max = config.getfloat(section, "u_max") # Maximum value of the u axis
    o.u_min = config.getfloat(section, "u_min") # Minimum value of the u axis
    o.z_max = config.getfloat(section, "z_max") # Maximum value of the z axis
    o.z_min = config.getfloat(section, "z_min") # Minimum value of the z axis

    o.z_sim_offset = config.getfloat(section, "z_sim_offset")
    
    return o
    
conf = sys.argv[1:]
config = ConfigParser.SafeConfigParser()
config.read(conf)

for i, section in enumerate(config.sections()):
    o = read_options(config, section)

    conv = {o.x_exp_col : lambda a: float(a)/1000,
            o.z_exp_col : lambda a: float(a)/1000}  # Convert first column from mm to m
    
    plt.subplot(np.ceil(len(config.sections())/2.0), 2, i+1)
    plt.grid(True)
    plt.title(section)

    print "Loading from %s and %s" % (o.exp, o.sim)
    sim = np.loadtxt(o.sim, usecols = (o.z_sim_col, o.u_sim_col))
    exp = np.loadtxt(o.exp, usecols = (o.x_exp_col, o.z_exp_col, o.u_exp_col, o.u_exp_norm_col), converters=conv)

    # Filter to have only data of the current x-position
    exp = exp[ exp[:, 0] == float(section) ]

     # Move the first column
    sim[:,0] += o.z_sim_offset

    # Compute u_inf from the last n values of the simulated data
    n = 50
    u_sim_inf = np.average(sim[-n:,1])
    print "u_sim_inf computed from the last %i values: %f" % (n, u_sim_inf)

    # Normalize values
    sim[:,1] = sim[:,1] / u_sim_inf
    exp[:,2] = exp[:,2] / exp[:,3]

    # Delete values greater than z_max
    sim = sim[ sim[:,0] < o.z_max ]
    exp = exp[ exp[:,1] < o.z_max ]

    plt.xlim(o.u_min, o.u_max) 
    plt.plot(sim[:,1], sim[:,0])       
    plt.plot(exp[:,2], exp[:,1], "-x")

    print
    
plt.show()
                 

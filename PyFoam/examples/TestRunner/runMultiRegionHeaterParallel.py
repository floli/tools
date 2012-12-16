#! /usr/bin/env python2

from runMultiRegionHeater import MulitRegionHeater
from PyFoam.Applications.Decomposer import Decomposer

class ParallelMulitRegionHeater(MulitRegionHeater):
    def init(self):
        self.setParameters(parallel=True,
                           nrCpus=2)

if __name__=='__main__':
    ParallelMulitRegionHeater().run()

"""
Application-class that implements pyFoamCloneCase.py
"""

from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Error import error,warning

from os import path

from PyFoam.Basics.GeneralVCSInterface import getVCS

class CloneCase(PyFoamApplication):
    def __init__(self,args=None):
        description="""\
Clones a case by copying the system, constant and 0-directories

If the case is under VCS then the cloning mechanism of the VCS is used
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <source> <destination>",
                                   changeVersion=False,
                                   interspersed=True,
                                   nr=2)

    def addOptions(self):
        what=OptionGroup(self.parser,
                         "What",
                         "Define what should be cloned")
        self.parser.add_option_group(what)

        what.add_option("--chemkin",
                        action="store_true",
                        dest="chemkin",
                        default=False,
                        help="Also copy the Chemkin-directory")
        what.add_option("--add-item",
                        action="append",
                        dest="additional",
                        default=[],
                        help="Add a subdirectory to the list of cloned items (can be used more often than once)")
        what.add_option("--no-pyfoam",
                        action="store_false",
                        dest="dopyfoam",
                        default=True,
                        help="Don't copy PyFoam-specific stuff")
        what.add_option("--latest-time",
                        action="store_true",
                        dest="latest",
                        default=[],
                        help="Add the latest time-step")
        
        behave=OptionGroup(self.parser,
                           "Behaviour")
        self.parser.add_option_group(behave)
        behave.add_option("--parallel",
                          action="store_true",
                          dest="parallel",
                          default=False,
                          help="Clone the processor-directories")
        behave.add_option("--force",
                          action="store_true",
                          dest="force",
                          default=False,
                          help="Overwrite destination if it exists")
        behave.add_option("--follow-symlinks",
                          action="store_true",
                          dest="followSymlinks",
                          default=False,
                          help="Follow symlinks instead of just copying them")
        behave.add_option("--no-vcs",
                          action="store_false",
                          dest="vcs",
                          default=True,
                          help="Do NOT use the VCS-clone mechanism if the case is under source control")

    def run(self):
        if len(self.parser.getArgs())>2:
            error("Too many arguments:",self.parser.getArgs()[2:],"can not be used")
            
        sName=self.parser.getArgs()[0]
        dName=self.parser.getArgs()[1]

        if path.exists(dName):
            if self.parser.getOptions().force:
                warning("Replacing",dName,"(--force option)")
            elif path.exists(path.join(dName,"system","controlDict")):            
                error("Destination",dName,"already existing and a Foam-Case")
            elif path.isdir(dName):
                dName=path.join(dName,path.basename(sName))
                if path.exists(dName) and not self.parser.getOptions().force:
                    error(dName,"already existing")                    
        elif not path.exists(path.dirname(dName)):
            warning("Directory",path.dirname(dName),"does not exist. Creating")
                
        sol=SolutionDirectory(sName,
                              archive=None,
                              paraviewLink=False,
                              parallel=self.opts.parallel)

        if sol.determineVCS()!=None and self.opts.vcs:
            if self.opts.chemkin or self.opts.additional or self.opts.latest:
                self.error("Using an unimplemented option together with VCS")
            
            vcsInter=getVCS(sol.determineVCS(),
                            path=sol.name)
            vcsInter.clone(dName)
            return
        
        if self.parser.getOptions().chemkin:
            sol.addToClone("chemkin")

        if self.parser.getOptions().dopyfoam:
            sol.addToClone("customRegexp")

        for a in self.parser.getOptions().additional:
            sol.addToClone(a)

        if self.parser.getOptions().latest:
            sol.addToClone(sol.getLast())
            
        sol.cloneCase(
            dName,
            followSymlinks=self.parser.getOptions().followSymlinks
            )

        self.addToCaseLog(dName,"Cloned to",dName)
        

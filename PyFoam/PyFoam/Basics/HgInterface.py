#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/HgInterface.py 7885 2012-02-26T19:32:53.603570Z bgschaid  $ 
"""A VCS-interface to Mercurial"""

from PyFoam.Error import warning,error

from GeneralVCSInterface import GeneralVCSInterface

from os import uname
from os import path as opath
from mercurial import commands,ui,hg
from mercurial.node import short

class HgInterface(GeneralVCSInterface):
    """The interface class to mercurial"""
    
    def __init__(self,
                 path,
                 init=False):

        GeneralVCSInterface.__init__(self,path,init)
        
        if init:
            commands.init(ui.ui(),self.path)
            open(opath.join(self.path,".hgignore"),"w").write("syntax: re\n\n")

        self.repo=hg.repository(ui.ui(),self.path)
        self.ui=self.repo.ui

        if init:
            self.addPath(opath.join(self.repo.root,".hgignore"))
            self.addStandardIgnores()
            
    def getRoot(self,path):
        return self.executeWithOuput("hg root --cwd %s" % path)
    
    def addPath(self,
                path,
                rules=[]):
        try:
            if not opath.exists(path):
                error("Path",path,"does not exist")
        except TypeError:
            error(path,"is not a path name")
            
        include=[]
        exclude=[]
        if rules!=[]:
            for inclQ,patt in rules:
                if inclQ:
                    include.append("re:"+patt)
                else:
                    exclude.append("re:"+patt)

        commands.add(self.ui,
                     self.repo,
                     path,
                     include=include,
                     exclude=exclude)

    def clone(self,
              dest):
        commands.clone(self.ui,
                       self.repo,
                       dest)

    def branchName(self):
        return self.repo.dirstate.branch()

    def getRevision(self):
        ctx = self.repo[None]
        parents = ctx.parents()
        return '+'.join([short(p.node()) for p in parents])
                
    def commit(self,
               msg):
        commands.commit(self.ui,
                        self.repo,
                        message=msg)

    def update(self,
               timeout=None):
        ok=True
        if timeout:
            self.ui.setconfig("ui","timeout",timeout);

        try:
            if commands.pull(self.ui,
                             self.repo):
                ok=False
            if commands.update(self.ui,
                               self.repo):
                ok=False
        except IndexError,e:
            #        except Exception,e:
            raise e
            return False

        return ok

    def addGlobToIgnore(self,expr):
        self.addToHgIgnore("glob:"+expr)

    def addRegexpToIgnore(self,expr):
        self.addToHgIgnore("re:"+expr)

    def addToHgIgnore(self,expr):
        open(opath.join(self.repo.root,".hgignore"),"a").write(expr+"\n")

#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/NameFinderLineAnalyzer.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""A line analyzer that generates a list of names"""

import re

from ContextLineAnalyzer import ContextLineAnalyzer

class NameFinderLineAnalyzer(ContextLineAnalyzer):
    """Class that finds names depending on a context"""

    def __init__(self,trigger,analyze,idNr=1,nr=1):
        """
        @param trigger: The regular expression that has to match before data is collected
        @param nr: The number of lines after the match that data is collected
        @param analyze: The regular expression that is used for analysis
        @param idNr: The id of the group that is used for analysis
        """
        ContextLineAnalyzer.__init__(self,trigger,nr=nr)

        self.analyze=re.compile(analyze)
        self.idNr=idNr

        self.names=[]
        
    def doActualAnalysis(self,line):
        m=self.analyze.match(line)
        if m!=None:
            val=m.group(self.idNr)
            if val.find(' ')>=0:
                val="\""+val+"\""
            self.names.append(val)
            self.callOnChange()
            
    def callOnChange(self):
        """
        To be called if the name list changes
        """
        pass

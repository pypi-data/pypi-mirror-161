import contur
import numpy as np
import sys
#from contur.util.utils import hack_journal
import contur.config.config as cfg
import contur.data.static_db as cdb

''' 
Module containing python objects containing data from the DB (beams, analysis etc)
'''

class Pool:
    """ 
    Class to store information about analysis pools
    (ok it is more of struct really)
    """
    def __init__(self, row):
        self.id = row[0]
        self.beamid = row[1]
        self.description = row[2]

class Beam:
    """ 
    Class to store information about beam configurations  
    (ok it is more of struct really)
    """
    def __init__(self, row):
        self.id = row[0]
        self.collider = row[1]
        self.particle_a = row[2]
        self.particle_b = row[3]
        self.energy_a = row[4]
        self.energy_b = row[5]
        self.root_s = np.sqrt((self.energy_a+self.energy_b)**2 - (self.energy_b-self.energy_a)**2)


class Analysis:
    """ 
    Class to store information about an analysis.

    Properties:
    name (full name, including the options string if present)
    short_name (without the options string)
    lumi (the integrated luminosity)
    rivet_analysis (the rivet analysus object)
    poolid (the id of the contur pool it belongs to)

    """
    def __init__(self,row,beamid):
            
        import rivet
        
        self.name, self.lumi_text, self.poolid = row
        self.beamid = beamid
        self.shortname = rivet.stripOptions(self.name)
        self.rivet_analysis = rivet.AnalysisLoader.getAnalysis(self.shortname)
        if self.rivet_analysis is None:
            cfg.contur_log.critical(
                "Could not find {} in your Rivet install. Update Rivet, or add analysis to the data/Rivet directory".format(self.name))
            sys.exit(1)
            
        self.inspireId = self.rivet_analysis.inspireId()
        self._paper_data = None
        self.summary = self.rivet_analysis.summary
        
        try:
            # if the luminosity string in contur is a value float, it overrides rivet.
            self.lumi = float(self.lumi_text)
            if cfg.contur_log is not None:
                cfg.contur_log.info("Rivet integrated lumi will be overwritten with {} for {}.".format(self.lumi,self.name))
        except ValueError: 
            if self.rivet_analysis.luminosityfb()<0:
                raise cfg.ConturError("No integrated luminosity in rivet or contur for {} {}.".format(self.name,self.rivet_analysis.luminosityfb())) from None
            elif self.lumi_text == "fb":
                self.lumi = self.rivet_analysis.luminosityfb()
            elif self.lumi_text == "pb":
                self.lumi = self.rivet_analysis.luminosityfb()*1000.
            elif self.lumi_text == "nb":
                self.lumi = self.rivet_analysis.luminosityfb()*1000000.
            elif self.lumi_text == "ub":
                self.lumi = self.rivet_analysis.luminosityfb()*1000000000.
            elif self.lumi_text == "eventcount":
                self.lumi = 1.0
            else:
                cfg.contur_log.error("Unrecognised instruction in contur DB lumi field: {}.".format(lumi_text))
                raise cfg.ConturError("Unrecognised instruction in contur DB lumi field: {}.".format(lumi_text)) from None

    def get_pool(self):
        """
        return the pool object associated with this analysis.
        """
        return cdb.get_pool(poolid=self.poolid)

    def bibkey(self):
        """
        return the bibtex key of this analysis
        """
        if self._paper_data is None:
            self._paper_data = contur.util.utils.get_inspire(self.inspireId)                
        return self._paper_data['bibkey']

    def bibtex(self):
        """
        return the bibtex of this analysis
        """
        if self._paper_data is None:
            self._paper_data = contur.util.utils.get_inspire(self.inspireId)

        return contur.util.utils.hack_journal(self._paper_data['bibtex'])
    
    def sm(self):
        """
        return a list of the SM theory descriptions associated with this analysis (if any)
        """
        return cdb.get_sm_theory(self.name)


    def toHTML(self,anaindex,adatfiles=[],style="",timestamp="now"):
        """
        Write this analysis to an HTML file called anaindex, with link links to the graphics version
        of the plots in adatfiles. If adatafiles is empty, just write the description etc
        without links to plots.

        opitonal stylesheet and timestamp.

        """
        
        from rivet.util import htmlify
        import os
        
        references = []

        ana = self.rivet_analysis

        summary = htmlify("{}".format(self.summary()))
        references = ana.references()

        description = htmlify(ana.description())

        reflist = []
        inspireurl = "http://inspirehep.net/literature/{}".format(self.inspireId)
        reflist.append('<a href="{}">Inspire record</a>'.format(inspireurl))
        reflist += references

        anaindex.write('<html>\n<head>\n')
        anaindex.write('<title>Pool {} &ndash; {}</title>\n'.format(self.name, self.poolid) )
        anaindex.write(style)
        anaindex.write('</head>\n<body>\n')

        anaindex.write('<h1>{}</h1>\n <h3>{} in analysis pool {}</h3>'.format(summary,self.name,self.poolid))

#        anaindex.write('<h2>{} in pool {}</h2>\n'.format(htmlify(self.name), self.poolid))
        anaindex.write('<p><a href="../../index.html">Back to index</a></p>\n')
        if description:
            try:
                anaindex.write('<p style="max-width:60em;">\n  {}\n</p>\n'.format(description))
            except UnicodeEncodeError as ue:
                print("Unicode error in analysis description for " + self.name + ": " + str(ue))
        else:
            anaindex.write('<p>\n  No description available \n</p>\n')

        anaindex.write('<div>\n')

        anaindex.write('<p>%s</p>\n' % " &#124; ".join(reflist))

#        anaindex.write('  <p><a href="{}">Inspire record</a></p>\n'.format(inspireurl))

        anaindex.write("  </br>\n\n")

        for datfile in sorted(adatfiles):
            obsname = os.path.basename(datfile).replace(".dat", "").rstrip()

            anaindex.write('  <div style="float:left; font-size:smaller; font-weight:bold;">\n')
            contur.plot.html_utils.plot_render_html(anaindex,obsname,self)                
            anaindex.write('  </div>\n')

        anaindex.write('\n<div style="clear:both" />\n')
        anaindex.write('</div>\n')
        anaindex.write('<div>{}</body>\n</html></div>\n'.format(timestamp))
        anaindex.close()

    

class SMPrediction:
    """ 
    Class to store information about SM predictions
    (ok it is more of struct really)
    """
    def __init__(self, row):
        self.a_name  = row[0]
        self.inspids = row[1]
        self.origin  = row[2]
        self.pattern = row[3]
        self.axis    = row[4]
        self.file_name = row[5]
        self.short_description = row[6]
        self.long_description  = row[7]
    

import numpy as np
import contur
import contur.config.config as cfg
import contur.data.static_db as cdb
 
class CovarianceBuilder(object):
    """
    `ao` Yoda AO
    apply_min: apply the minimum number of systematic uncertainties criteria when determining
    whether or not to use the error breakdown for correlations.

    Class to handle retrieval of annotations/errors from YODA objects
    """
    def __init__(self, ao, apply_min=True):
        self.ao=ao
        self.hasBreakdown=self._getBreakdownAttr(apply_min)
        self.readMatrix  =self._getMatrixAttr()
        self.nbins=self.ao.numPoints()
        self.cov=None
        self.uncov=None
        self.errorBreakdown=None
        self.covariance_matrix=None

    def _getBreakdownAttr(self,apply_min):
        """
        return true if this AO has an error breakdown
        """
        if not self.ao.hasValidErrorBreakdown():
            return False
        if apply_min and len(self.ao.variations())<cfg.min_num_sys:
            return False
        return True

    def _getMatrixAttr(self):
        """
        return true if this AO has a covariance matrix stored in another AO. 

        """

        if cfg.diag:
            return False
        
        self._covname =  cdb.get_covariance_name(self.ao.path())
        if self._covname:
            return True
        else:
            return False
    
    def read_cov_matrix(self,aos):
        """
        read the covariance matrix from another AO and return it.
        """
        if not self.readMatrix:
            return None

        if self.covariance_matrix is not None:
            return self.covariance_matrix

        cfg.contur_log.debug("reading matrix {}".format(self._covname))
        
        # read the covariance matrix into an array.
        matrix_ao = aos[self._covname]

        nbins = len(self.ao.xVals()) 
        self.covariance_matrix = np.zeros((nbins,nbins))

        i = 0
        j = 0
        for z in matrix_ao.zVals():
            self.covariance_matrix[i][j] = z
            i=i+1
            if i==nbins:
                i=0
                j=j+1

                
        return self.covariance_matrix

    
    def buildCovFromBreakdown(self,ignore_corrs=False):
        """
        Get the covariance, calculated by YODA from the error breakdown, and return it.
        Also make a list of the correlated uncertainties (ie those not labelled uncor or stat)
        """
        
        return self.ao.covarianceMatrix(ignore_corrs) 

    def buildCovFromErrorBar(self,assume_correlated=False):
        """
        Build the covariance from error bars and return it.
        Note that the "assume correlated" option is very dodgy
        since we have no idea what the stat errors really are.
        """
        
        dummyM = np.outer(range(self.nbins), range(self.nbins))
        covM = np.zeros(dummyM.shape)
        systErrs = np.zeros(self.nbins)
        
        for ibin in range(self.nbins):
            #symmetrize the errors (be conservative - use the largest!)
            systErrs[ibin] = max(abs(self.ao.points()[ibin].yErrs()[0]),abs(self.ao.points()[ibin].yErrs()[1]))
            
        if assume_correlated:
            if self.errorBreakdown is None:
                self.errorBreakdown={}
            self.errorBreakdown['syst']=systErrs
            covM += np.outer(systErrs, systErrs)

        else:
            covM += np.diag(systErrs * systErrs)

        return covM

    def getErrorBreakdown(self):
        """ return the breakdown of uncertainties """

        if self.hasBreakdown:
            if self.errorBreakdown is not None:
                return self.errorBreakdown

            else:
                self.errorBreakdown={}
                # Build the error breakdown from the annotation, applying the relevant conditions.
                errMap_values = {}
                ibin=0
                for point in self.ao.points():
                    try:
                        errMap_values[ibin] = point.errMap()
                    except:
                        # handle occasional messed up entries
                        errMap_values[ibin]=0
                    ibin=ibin+1

                for source in self.ao.variations():
                    if len(source)>0 and not "stat" in source.lower() and not "uncor" in source.lower():
                        systErrs = np.zeros(self.nbins)
                        fracErrs = np.zeros(self.nbins)
                        ibin=0
                        for point in self.ao.points():
                            nomVal = point.y()
                            errMap_single_value = errMap_values[ibin]
                            try:
                                #symmetrize the errors (be conservative - use the largest!)
                                systErrs[ibin]=max(abs(errMap_single_value[source][0]),abs(errMap_single_value[source][1]))
                                if not nomVal==0.0:
                                    fracErrs[ibin] = systErrs[ibin]/nomVal
                                else:                            
                                    fracErrs[ibin] = 0.0
                            except:
                                # handle occasional messed up entries
                                systErrs[ibin]=0
                                fracErrs[ibin]=0
                            ibin=ibin+1
                        if max(fracErrs)> cfg.min_syst:
                            self.errorBreakdown[source] = systErrs

            return self.errorBreakdown
            
        else:
            return {}

            



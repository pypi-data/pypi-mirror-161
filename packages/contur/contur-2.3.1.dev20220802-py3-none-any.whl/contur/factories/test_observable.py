import contur
import rivet
import yoda
import numpy as np
import traceback
import sys
import scipy.stats as spstat

import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.utils as cutil
import contur.factories.likelihood as lh

class Observable(object):
    
    """
        Processes and decorates :class:`YODA.AnalysisObject` to a testable format

        :param ana_obj: ``YODA`` AO to dress
        :type ana_obj: :class:`YODA.AnalysisObject`
        :param xsec:
            _XSEC scatter recording generator cross section in YODA file (*contained in all Rivet run outputs*)
        :type xsec: :class:`YODA.Scatter1D`
        :param nev:
            _EVTCOUNT scatter recording total generated events in YODA file (*contained in all Rivet run outputs*)
        :type nev: :class:`YODA.Scatter1D`

    """

    def __init__(self, ana_obj, xsec, nev):

        from contur.factories.yoda_factories import root_n_errors
        
        # Construct with an input YODA AO list, and a Scatter1D for the cross section and nEv
        self.signal = ana_obj
        self.xsec = xsec
        self.nev = nev

        # Measurement 
        self._ref = None
        # SM theory
        self._thy = None

        self.pool = None

        # check we are using the right HepMC weight (if supplied) and remove it from the path
        self._weight = rivet.extractWeightName(self.signal.path())
        if self._weight != cfg.weight:
            return
        self.signal.setPath(rivet.stripWeightName(self.signal.path()))
        
        # Initialize the public members we always want to access
        self._isRatio = cdb.isRatio(self.signal.path())
        self._isProfile = False
        self._isSearch = cdb.isSearch(self.signal.path())
        self._stack_smbg = yoda.Scatter2D
        self._stack_databg = yoda.Scatter2D

        # these should just be used for plotting, which is not done if writer is silenced (e.g. in gridMode)
        self._refplot = None
        self._sigplot = None
        self._thyplot = None

        self._lumi = 1
        self._isScaled = False
        self._scaleFactorData = 1
        self._scaleFactorSig = 1
        self._conturPoints = []
        self._nev_differential = 1.0
        self._likelihood = None

        self.measured_values = None
        self.bsm_values = None
        self.sm_values = None
        self.expected_values = None
        
        # Call the internal functions on initialization
        # to fill the above members with what we want, these should all be private

        # Get the measurement reference data.
        if not self.__getData():
            return

        # Get the theory reference data, if present, and set the appropriate 
        # convenience flag if successful.
        self.__getThy()        
        self._useTheory = self.sm_values is not None

        self.__getAux()
        if self.pool is None:
            return
        
        self.__getisScaled()

        # build the expected values (SM theory with data uncertainties)
        self.__getExpected()
        
        #cfg.contur_log.debug("Measured: VALS: {} \n COV: {} \n DIAG {} \n ERRS {}".format(
        #    self.measured_values.central_values,self.measured_values.covariance_matrix,
        #    self.measured_values.diagonal_matrix,self.measured_values.err_breakdown))
                             
        # Determine the type of object we have, and build a 2D scatter from it if it is not one already
        # Also recalculate scalefactor, if appropriate
        if self.signal.type() in ['Histo1D', 'Profile1D', 'Counter']:

            self._isProfile = self.signal.type().startswith("Profile")

            if self._isScaled:
                # if the plot is area normalised (ie scaled), work out the factor from number of events and generator xs
                # (this is just the integrated cross section associated with the plot)
                # TODO: should maybe be using effNumEntries to correctly handle weighted events?
                try:
                    self._scaleFactorSig = \
                        float(self.xsec.point(0).x()) * float(self.signal.numEntries()) / float(self.nev.numEntries())


                except Exception as e:
                    cfg.contur_log.warning(
                        "missing info for scalefactor calc", exc_info=e)

            # cfg.contur_log.warning("XXX {} ({}): {:d} bins in hist vs {:d} in scatter".\
            #                                  format(self.signal.path(), self.signal.type(),
            #                                         len(self.signal), len(yoda.mkScatter(self.signal))))
            self.signal = yoda.mkScatter(self.signal)

        # Make sure it is actually a Scatter2D - mkScatter makes Scatter1D from counter.
        if self.signal.type() == 'Scatter1D':
            self.signal = cutil.mkScatter2D(self.signal)

        # if everything we need is available, there will be ref data.
        if self._ref and self.xsec:
            if self._isScaled:
                self.__doScale()
            # include the stat uncertainties on the expected number of events.
            root_n_errors(self.signal,self._isSearch,nx=self._nev_differential,lumi=self._lumi)
            self.__fillBucket()

#        cfg.contur_log.debug("BSM: VALS: {} \n COV: {} \n DIAG {} \n ERRS {}".format(
#            self.bsm_values.central_values,self.bsm_values.covariance_matrix,
#            self.bsm_values.diagonal_matrix,self.bsm_values.err_breakdown))

        if not cfg.silenceWriter:
            # Public member function to build plots needed for direct histogram visualisation
            # avoid calling YODA.clone() unless we have to
            # Must be called before scaling.
            if self._ref:
                self.doPlot()
            else:
                cfg.contur_log.warning("No reference data found for histo: {}".format(self.signal.path()))


    def __getisScaled(self):
        """Internal function to look up Scaling attributes from the contur database, defined in :mod:`contur.data`

        :Built members:
            * *isScaled* (``bool``) --
              True if some scaling has been applied to this histogram
            * *scaleFactorData* (``float``) --
              Factor to scale the ref data by (n count) to undo the normalisation

        """
        self._isScaled, self._scaleFactorData, self._nev_differential = cdb.isNorm(self.signal.path())


    def __getData(self):
        """
        Internal function to look up the refdata

        :Built members:
            * *ref* (:class:YODA.Scatter2D) --
              Reference scatter plot matching path from input signal aos
            * *measured_values* (:class:ObservableValues) --
              central values, covariance etc for the measuremwent
        """

        try:
            self._ref = cfg.refObj["/REF" + rivet.stripOptions(self.signal.path())]
            # extract the bin widths
            self._bin_widths = []
            for xerr in self._ref.xErrs():
                self._bin_widths.append(xerr[0])

        except KeyError:
            return False

        try:
            cov = cfg.refCorr[self._ref.path()].copy()
            nuisErrs = cfg.refErrors[self._ref.path()].copy()
            cfg.contur_log.debug("Attempting to use correlation info for {}".format(self.signal.path()))
        except:
            cfg.contur_log.debug("No correlation info for {}".format(self.signal.path()))
            cov = None
            nuisErrs = None
        try:
            uncov = cfg.refUncorr[self._ref.path()].copy()
        except:
            uncov = None
            return False

        self.measured_values = ObservableValues(bin_widths=self._bin_widths, central_values=self._ref.yVals(), err_breakdown=nuisErrs,
                                                covariance_matrix=cov, diagonal_matrix=uncov )
        return True


    def __getExpected(self):
        """
        Internal function to get the expected values (SM cental values with data uncertainty)

        :Modified members:
            * *expected_values* (:class:YODA.Scatter2D) --
              Reference scatter plot matching path from input signal aos

        """

        # can't do this if we don't have a theory prediction!
        if self.sm_values is None:
            return

        self._expected = self._ref.clone()
        for i in range(0, len(self._expected.points())):
            self._expected.points()[i].setY(self._thy.points()[i].y())


        if self.measured_values.covariance_matrix is not None:
            cov = self.measured_values.covariance_matrix.copy()
            errs = self.measured_values.err_breakdown.copy()
        else:
            cov = None
            errs = None


        self.expected_values = ObservableValues(bin_widths=self._bin_widths, central_values=self.sm_values.central_values.copy(),
                                                err_breakdown=errs, covariance_matrix=cov,
                                                diagonal_matrix=self.measured_values.diagonal_matrix.copy() )
        
    def __getThy(self):
        """
        Internal function to look up the SM theory data

        :Built members:
            * *thy* (:class:YODA.Scatter2D) --
              SM Theory prediction matching path from input signal aos

            * *sm_values* (:class:ObservableValues) --
              correlation matrix, central values etc for the SM theory prediction

        """

        # find whether theory is always required for this histogram
        self._theoryComp = cdb.theoryComp(self.signal.path())

        try:
            self._thy = cfg.thyObj["/THY"+self.signal.path()].clone()

            try:
                thCov = cfg.theoryCorr[self._thy.path()].copy()
                thErrs = cfg.theoryErrors[self._thy.path()].copy()
            except:
                thCov = None
                thErrs = None
            try:
                thUncov = cfg.theoryUncorr[self._thy.path()].copy()
            except KeyError:
                thUncov = None
                # just warn if we can't build theory, it's less important...
                cfg.contur_log.warning(
                    "Could not build any theory error source for %s" % self.signal.path())

            cfg.contur_log.debug(
                    "Using theory for {}".format(self._thy.path()))

            self.sm_values = ObservableValues(bin_widths=self._bin_widths, central_values=self._thy.yVals(), err_breakdown=thErrs,
                                              covariance_matrix=thCov, diagonal_matrix=thUncov )

        except KeyError:
            pass

            
    def doPlot(self):
        """
        Public member function to build yoda plot members for interactive runs

        These are only for displaty, they are not used in any of the statistics calculations.
        """
        
        # see if there are unscaled versions of the histos
        try:
            self._refplot = cfg.plotObj[self._ref.path()]
        except KeyError:
            # otherwise the standard ref should be unscaled
            self._refplot = self._ref.clone()

        # and the same thought process for the background model, and for the theory (even if the
        # theory is not being used as background).

        if self.sm_values is not None:
            try:
                self._thyplot = cfg.plotThObj[self._thy.path()]
            except KeyError:
                self._thyplot = cfg.thyObj[self._thy.path()]

        # build stack for plotting, for histogrammed data
        if not self._isRatio:
            self.__buildStack()
        else:
            self._stack_databg = self.signal.clone()
            self._stack_smbg = self.signal.clone()
        self._sigplot = self.signal.clone()


    def __getAux(self):
        """Internal function to look up auxiliary attributes from the contur database

        :Built members:
            * *pool* (``string``) --
              String for analysis pool looked up from contur database
            * *subpool* (``string``) --
              String for analysis subpool looked up from contur database

        """
        self._lumi, self.pool, self.subpool = cdb.LumiFinder(
            self.signal.path())


    def __buildStack(self):
        """
        Private function to stack the signal on backgrounds for easier visualisation
        """

        if self.signal.type() != "Scatter2D":            
            return False

        bgplot = self._refplot.clone()
        
        self._stack_databg = self.signal.clone()
        if self._stack_databg.numPoints() != bgplot.numPoints():
            cfg.contur_log.warning(
                "%s : stack and background have unequal numbers of points. Skipping." % bgplot.path())
            return False

        for i in range(0, len(self._stack_databg.points())):
            self._stack_databg.points()[i].setY(
                self._stack_databg.points()[i].y() * self._scaleFactorSig / self._scaleFactorData +
                bgplot.points()[i].y())

            # set these to include only the BSM errors, since that is what is used in the test
            self._stack_databg.points()[i].setYErrs(self.signal.points()[i].yErrs()[0] * self._scaleFactorSig / self._scaleFactorData,
                                                    self.signal.points()[i].yErrs()[1] * self._scaleFactorSig / self._scaleFactorData)

        if not self._useTheory:
            return

        try:
            # this only exists for scaled plots.
            bgplot = cfg.plotThObj[self._thy.path()]
        except KeyError:
            bgplot = cfg.thyObj[self._thy.path()]

        self._stack_smbg = self.signal.clone()
        if self._stack_smbg.numPoints() != bgplot.numPoints():
            cfg.contur_log.warning(
                "%s : stack and background have unequal numbers of points. Skipping." % bgplot.path())
            return False

        for i in range(0, len(self._stack_smbg.points())):
            self._stack_smbg.points()[i].setY(
                self._stack_smbg.points()[i].y() * self._scaleFactorSig / self._scaleFactorData +
                bgplot.points()[i].y())

            eu2 = (self.signal.points()[i].yErrs()[0]*self._scaleFactorSig/self._scaleFactorData)**2 + bgplot.points()[i].yErrs()[0]**2
            ed2 = (self.signal.points()[i].yErrs()[1]*self._scaleFactorSig/self._scaleFactorData)**2 + bgplot.points()[i].yErrs()[1]**2
            self._stack_smbg.points()[i].setYErrs(np.sqrt(eu2),np.sqrt(ed2))


    def __doScale(self):
        """Private function to perform the normalisation of the signal
        """

        if self.signal.type() != "Scatter2D":
            return

        for i in range(0, len(self.signal.points())):
            self.signal.points()[i].setY(self.signal.points()[
                i].y() * self._scaleFactorSig)
            self.signal.points()[i].setYErrs(
                map(lambda x: x * self._scaleFactorSig, self.signal.points()[i].yErrs()))


    def __fillBucket(self):
        """Create a block, contains the observables from this histogram and their correlation plus statistical metrics

        :Built members:
            * *block* (:class:`contur.block`) --
              Automatically filled bucket containing statistical test pertaining to this histogram

        """
        if len(self._ref.points()) != len(self.signal.points()):
            cfg.contur_log.critical(
                "Ref data and signal for {} have unequal numbers of points ({} vs {})".format(
                    self.signal.path(), len(self._ref.points()), len(self.signal.points())) )
            raise Exception

        # estimate the stat error on the expected signal.
        # TODO: signal errors are symmetrised here. Does that make any difference? (should not)
        yErrs = self.signal.yErrs()
        serrs = []
        for epair in yErrs:
            # these are the MC stat errors
            serrs.append((abs(epair[0]) + abs(epair[1]))*0.5)
        serrs = np.array(serrs)
        self.bsm_values = ObservableValues(bin_widths=self._bin_widths, central_values=self.signal.yVals(), err_breakdown=serrs)
            
        try:                
            self._likelihood = lh.Likelihood(calculate=True, ratio=self._isRatio,
                                             lumi=self._lumi,
                                             profile=self._isProfile,
                                             sxsec=self.xsec.point(0).x(), #< and uncertainty?
                                             bxsec=self._scaleFactorData, #< TODO: a hack for profiles etc. Improve?
                                             tags=self.signal.path(),
                                             measured_values=self.measured_values,
                                             sm_values=self.sm_values,
                                             bsm_values=self.bsm_values,
                                             expected_values=self.expected_values)
        except AttributeError as ate:
            cfg.contur_log.fatal("This can happen when your yodafile is corrupted: {}".format(ate))
            traceback.print_exc()
            raise

        self._likelihood.pools = self.pool
        self._likelihood.subpools = self.subpool

    def get_sm_pval(self):
        """
        Calculate the pvalue compatibility (using chi2 survival) for the SM prediction and this
        measurement
        """
        ts = self.likelihood.get_ts_s_b(cfg.smbg)
        ndof = self.likelihood.get_ndof(cfg.smbg)
        pval = np.exp(spstat.chi2.logsf(ts,ndof))
        return pval

        
    @property
    def ref(self):
        """
        Reference data, observed numbers input to test, scaled if required

        **type** (:class:`YODA.Scatter2D`)
        """
        return self._ref


    @property
    def thy(self):
        """
        Reference SM theory data, scaled if required

        **type** (:class:`YODA.Scatter2D`)
        """
        return self._thy


    @property
    def stack_smbg(self):
        """Stacked, unscaled Signal+background for plotting (SM as background)

        **type** (:class:`YODA.Scatter2D`)
        """
        return self._stack_smbg

    @property
    def stack_databg(self):
        """Stacked, unscaled Signal+background for plotting (data as background)

        **type** (:class:`YODA.Scatter2D`)
        """
        return self._stack_databg


    @property
    def sigplot(self):
        """Signal for plotting

        **type** (:class:`YODA.Scatter2D`)

        """
        return self._sigplot
    @sigplot.deleter
    def sigplot(self):
        del self._sigplot

    @property
    def refplot(self):
        """Reference data for plotting

        **type** (:class:`YODA.Scatter2D`)

        """
        return self._refplot


    @property
    def thyplot(self):
        """Theory for plotting

        **type** (:class:`YODA.Scatter2D`)

        """
        return self._thyplot


    @property
    def scaled(self):
        """Bool representing if there is additional scaling applied on top of luminosity

        **type** (``bool``)

        """
        return self._isScaled


    @property
    def has_theory(self):
        """Bool representing if a theory prediction was found for the input signal

        **type** (``bool``)

        """
        return (self.sm_values is not None)


    @property
    def signal_scale(self):
        """Scale factor applied to the signal histogram/scatter, derived generally from input nEv and xs

        **type** (``float``)
        """
        return self._scaleFactorSig


    @property
    def data_scale(self):
        """Scale factor applied to the refdata histogram/scatter

        **type** (``float``)


        """
        return self._scaleFactorData


    @property
    def likelihood(self):
        """The instance of :class:`~contur.factories.likelihood.Likelihood` derived from this histogram

        **type** (:class:`~contur.factories.likelihood.Likelihood`)

        """
        return self._likelihood
    @likelihood.setter
    def likelihood(self,lh):
        self._likelihood = lh
        
    def __repr__(self):
        if not self.signal.path():
            tag = "Unidentified Source"
        else:
            tag = self.signal.path()
        return "%s from %s, with %s" % (self.__class__.__name__, tag, self._likelihood)

class ObservableValues(object):
    """
    A book-keeping class to contain all the numerical info (central values, err_breakdown, covariance)
    for a given binned observable.
    """

    def __init__(self, bin_widths=None, central_values=None, err_breakdown=None, covariance_matrix=None, diagonal_matrix=None):
        self.bin_widths = bin_widths
        self.central_values= central_values
        self.err_breakdown = err_breakdown
        self.covariance_matrix = covariance_matrix
        self.diagonal_matrix = diagonal_matrix
        if  err_breakdown is not None and diagonal_matrix is None:
            self.diagonal_matrix = np.diag(err_breakdown * err_breakdown)

            

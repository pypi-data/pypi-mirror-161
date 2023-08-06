"""
The yoda_factories module contains three main components in the middle of the data flow, sitting between the high level steering
in :class:`contur.factories.Depot` class and the lower level statistics in the :class:`contur.factories.Likelihood` class
"""

import os
import re

import contur
import contur.factories.likelihood as lh
import contur.factories.test_observable
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.file_readers as cfr
import contur.util.utils as cutil
from contur.data.build_covariance import CovarianceBuilder

import rivet
import yoda
import numpy

def load_bg_data(path):
    """ 
    load the background (REF and THY data) for all the observables associated with this rivet analysis
    """
    try:
        ana_id, tag = cutil.splitPath(path)
    except ValueError:
        ana_id = path

    analysis_list = cdb.get_analyses(analysisid=ana_id)
    if len(analysis_list) != 1:
        cfg.contur_log.error("{} does not specify a known, unique analysis! Result was: {}".format(path,analysis_list))

    analysis = analysis_list[0]

    if cfg.onlyAnalyses and not (analysis.shortname in cfg.onlyAnalyses):
        return

    if cfg.vetoAnalyses and (analysis.shortname in cfg.vetoAnalyses):
        return
    
    # first the measurement data. This is specified by the shortname, and is all in the same file.    
    # check we haven't got it already
    if not (analysis.shortname in cfg.found_ref):
    
        f = cutil.find_ref_file(analysis)
        cfg.contur_log.debug("Reading data from {}".format(f))
        if len(f)==0:
            cfg.contur_log.error("Cannot find REF data for {}".format(analysis.name))
        else:
            load_aos_from_file(f)
            cfg.found_ref.append(analysis.shortname)

    # now see if there is any SM theory for this. These are specified by the full analysis name including options.
    if not (analysis.name in cfg.found_thy):
        
        f = cutil.find_ref_file(analysis,theory=True)
        cfg.contur_log.debug("Reading theory from {}".format(f))
        if len(f)==0:
            cfg.contur_log.debug("Cannot find SM theory for {}".format(analysis.name))
        else:
            load_aos_from_file(f)
            cfg.found_thy.append(analysis.name)

    
def load_aos_from_file(f):
    """ 
    Load the relevant analysis objects (REF or THY) from the file f. 

    """
                
    aos = yoda.read(f) 
    for path, ao in aos.items():

        if not rivet.isRefPath(path) and not rivet.isTheoryPath(path):
            continue

        load_ao(path, ao, aos)


def load_ao(path, ao, aos):
    """
    Load the ao, with the path=path, into memory, as THY or REF object
    """
    
    # Convert all types to Scatter2D, including Scatter1Ds
    if ao.type() == "Scatter1D":
        ao = cutil.mkScatter2D(ao)
    elif ao.type() == "Scatter3D":
        cfg.contur_log.debug("Skipping Scatter3D {}".format(ao.path()))
        return
    elif ao.type() != "Scatter2D":
        ao = yoda.mkScatter(ao)

    # Find out whether the cross-section has been scaled by some factor (e.g. to area-normalise it)
    # and whether it is a differential in number of events (usually searches), and if so in how many GeV.
    # The latter is only needed if it is an N_events plot with zero uncertainty (again, usually searches),
    # so we can calculate and use the Poisson error from the event number.
    try:
        _isScaled, _scaleFactorData, _nev_differential = cdb.isNorm(ao.path())
    except cdb.InvalidPath:
        raise

    if rivet.isRefPath(path):
                    
        if not _nev_differential==0:
            # root(n) errors on event count histos
            root_n_errors(ao,True,nx=_nev_differential,replace=True)
            

        # object to build the covariance matrix
        cbuilder = CovarianceBuilder(ao)

        if cbuilder.readMatrix:
            # read the covariance matrix from the dictionary of analysis objects
            cfg.refCorr[path] = cbuilder.read_cov_matrix(aos)

        if _isScaled:

            # if we are not running in grid mode, save the original for display purposes only.
            if not cfg.silenceWriter:
                cfg.plotObj[path] = ao.clone()
            scale_scatter_2d(ao, _scaleFactorData)

        cfg.refObj[path] = ao


        if cbuilder.hasBreakdown:
            if not cbuilder.readMatrix:
                cfg.refCorr[path] = cbuilder.buildCovFromBreakdown(ignore_corrs=cfg.diag)

            cfg.refUncorr[path] = cbuilder.buildCovFromErrorBar()
            cfg.refErrors[path] = cbuilder.getErrorBreakdown()
        else:
            # always fill the unCorr case in case we need it later
            cfg.refUncorr[path] = cbuilder.buildCovFromErrorBar()
                
            # NB don't need to scale the errors again because they were already scaled in the "scale_scatter" step.

    if rivet.isTheoryPath(path):

        # Build the covariance object to fill the dictionaries
        # For theory, we will not apply the "minimum number of error sources" criteria.
        # This means the systematics are always assumed correlated, unless the theory
        # correlations switch, or the master correlations switch, turns them off.
        # (or the data has no correlations, in which case we fall back to the single bin method anyway)
        cbuilder = CovarianceBuilder(ao,apply_min=False)

        if _isScaled:
            if not cfg.silenceWriter:
                cfg.plotThObj[path] = ao.clone()
            scale_scatter_2d(ao, _scaleFactorData)
        cfg.thyObj[path] = ao

        if cbuilder.hasBreakdown:
            if cfg.useTheoryCorr:
                cfg.theoryCorr[path] = cbuilder.buildCovFromBreakdown(ignore_corrs=cfg.diag)
            # always fill the unCorr case in case we need it later
            cfg.theoryUncorr[path] = cbuilder.buildCovFromBreakdown(ignore_corrs=True)

        else:
            cfg.theoryUncorr[path] = cbuilder.buildCovFromErrorBar()
            cfg.theoryCorr[path] = cfg.theoryUncorr[path].copy() 

        # NB don't need to scale the errors again because they were already scaled in the "scale_scatter" step.
        cfg.theoryErrors[path] = cbuilder.getErrorBreakdown()


def scale_scatter_2d(ao, sf):
    """
    Apply the scales factor sf to the yoda analysis object ao.
    """
    
    for i in range(0, len(ao.points())):
        ao.points()[i].setY(ao.points()[i].y() * sf)
        cfg.contur_log.debug(
                "Scaling {}: {} SF={}".format(ao.path(),ao.points()[i].yErrs(), sf))
        if ao.hasValidErrorBreakdown():
            for source in ao.variations():
                ao.points()[i].setErrMinus(2,ao.points()[i].errMap()[source][0]*sf, source)
                ao.points()[i].setErrPlus(2,ao.points()[i].errMap()[source][1]*sf, source)
        else:
            ao.points()[i].setYErrs(
                map(lambda x: x * sf, ao.points()[i].yErrs()))
        cfg.contur_log.debug("Scaled: {}".format(ao.points()[i].yErrs()))

        try:
            cfg.refCorr[ao.path()] = cfg.refCorr[ao.path()]*sf
        except KeyError:
            # this just means the covariance will be build from the errors (which we have just scaled...)
            pass
        
        
def root_n_errors(ao, is_evcount, nx=0.0, lumi=1.0, replace=False):
    """Function to include root(number of expected events) errors in the uncertainties of 2D scatter.

    The uncertainty based on the expected events for the relevant integrated luminosity. This is
    not about MC statistics!

    The minimum uncertainty is one event... we are not doing proper low-stat treatment in tails,
    so this is a conservative fudge.

    :arg ao:
           The ``YODA`` analysis object to be manipulated.
    :type: :class:`YODA.AnalysisObject`

    :arg nx: factor needed to convert to number of events for none-uniform bin widths (<0, not used, ==0, do nothing).
    :type: float

    :arg is_evcount:
           True is the plot is in event numbers. Otherwise assumed to be a differential cross section.
    :type: boolean

    :arg lumi:
           Integrated luminosity used to get event counts from differential cross sections
    :type: float

    :arg replace:
           If True replace the uncertainties. If False (default) add them in quadrature.
    :type: bool

    """


    cfg.contur_log.debug("Adding expected signal stat errors for {}. Evtc={},  Lumi={}, replace={}".format(ao.path(),is_evcount,lumi,replace))

    cfg.contur_log.debug("Before: {} : {}".format(ao.yVals(),ao.yErrs()))
    try:
        for point in ao.points():

            yup, ydown = point.yErrs()
            if replace and not (yup==0 and ydown==0):
                cfg.contur_log.warning("Overwriting non-zero uncertainty for {}.".format(ao.path()))

            if is_evcount:
                if nx < 0:
                    # all we need is the square root
                    uncertainty = max(numpy.sqrt(point.y()),1.0)
                else:
                    # plot was presented as a differential number of events with non-constant bin width, need to multiply
                    # by bin width and divide the differential factor.
                    bw = point.xErrs()[0]*2.0
                    if nx > 0:
                        num_events = max(point.y()*bw/nx,1.0)
                        uncertainty = max(nx*numpy.sqrt(num_events)/bw,1.0)
                    else:
                        cfg.contur_log.warning("nx=0 for event count histo {}. Should not happen.".format(ao.path()))

            else:                
                # cross section plots.
                bw = point.xErrs()[0]*2.0
                num_events = max(point.y()*bw*lumi,1.0)
                try:
                    uncertainty = numpy.sqrt(num_events)/(bw*lumi)
                except:
                    cfg.contur_log.error("Divide by zero. {} has bin width {} and lumi {} val {}.".format(ao.path(),bw,lumi,point.x()))
                    uncertainty = 0
                    
            if replace:
                point.setYErrs(uncertainty,uncertainty,"stat")
                point.setYErrs(uncertainty,uncertainty)
            else:
                point.setYErrs(numpy.sqrt(uncertainty**2+yup**2),numpy.sqrt(uncertainty**2+ydown**2),"stat")
                point.setYErrs(numpy.sqrt(uncertainty**2+yup**2),numpy.sqrt(uncertainty**2+ydown**2))

        cfg.contur_log.debug("After: {} : {}".format(ao.yVals(),ao.yErrs()))

    except AttributeError as ate:
        
        cfg.contur_log.error("No points for {}. {}".format(ao.path(),ate))
        raise


class YodaFactory(object):
    """Class controlling Conturs YODA file processing ability

    This class is initialised from an os path to a ``YODA`` file and
    dresses it by iterating through each ao and wrapping that in an instance of
    :class:`~contur.factories.test_observable.Observable` which encapsulates a YODA analysis object and derives the required
    :class:`~contur.factories.likelihood.Likelihood` block for it. This class then contains
    the aggregated information for all of these instances across the entire ``YODA`` file.

    path to output plot objects is detemined by cfg.plot_dir

    :param yodaFilePath: Valid :mod:`os.path` filesystem YODA file location
    :type yodaFilePath: ``string``

    :Keyword Arguments:
        * *noStack* (``bool``) -- Mark true to not stack the signal on background in plotting (*cosmetic*)

    """

    def __init__(self, yodaFilePath, noStack=False):
        self.yodaFilePath = yodaFilePath

        self._likelihood_blocks = []
        self._sorted_likelihood_blocks = {}

        self._full_likelihood = {}
        # set up three versions of the full likelihood, one for each type of stat calculation.
        for stat_type in cfg.stat_types:
            self._full_likelihood[stat_type] = lh.CombinedLikelihood(stat_type)
        
        self._NoStack = noStack

        self.__get_likelihood_blocks()


    def __get_likelihood_blocks(self):
        """
        Private function to collect all of the conturBuckets from a YODA file

        These are not combined, to each block contains all stat_types

        :Built variables:
        * **conturBuckets** (:class:`contur.block`) --
          List of all conturBuckets created from YODA file
        """

        mc_histos, x_sec, nev = cfr.get_histos(self.yodaFilePath)
        if mc_histos is None or len(mc_histos)==0:
            return

        for path, ao in cutil.progress_bar(mc_histos.items(), total=len(mc_histos)):

            if cdb.validHisto(path):

                # now load the REF and SM THY info for this analysis, if not already there. 
                load_bg_data(path)

                observable = contur.factories.test_observable.Observable(ao, x_sec, nev)

                # if we are running on theory only, require it exists.
                if observable._ref is not None:
                    
                    cfg.contur_log.debug(
                        "Processed measurement {}".format(observable.signal.path()))

                    # write out the plot .dat files TODO: what does this really write now?
                    if not cfg.silenceWriter:
                        cutil.write_yoda_dat(observable, nostack=self._NoStack)

                    self._likelihood_blocks.append(observable._likelihood)


                            
        # we cannot pickle yoda objects so we just declare them in this scope when we are scrubbing the yodafile
        del mc_histos, x_sec, nev


    def resort_blocks(self,stat_type,omitted_pools=""):
        """
        Function to sort the :attr:`sorted_likelihood_blocks` list. Used for resorting after a merging exclusively.
        :Keyword Arguments:
        * *stat_type* (``string``) -- which statisic type (default, SM background or expected) is being sorted by.
        """

        self._sorted_likelihood_blocks[stat_type] = lh.sort_blocks(self._sorted_likelihood_blocks[stat_type],stat_type,omitted_pools="")
        self._full_likelihood[stat_type] = lh.build_full_likelihood(self.get_sorted_likelihood_blocks(stat_type),stat_type)

        # cleanup some bulk we don't need  @TODO make this a separate cleanup function.
        if hasattr(self, '_likelihood_blocks'):
            del self._likelihood_blocks
        if hasattr(self, 'yodaFilePath'):
            del self.yodaFilePath
    
    def drop_na_likelihood_blocks(self,stat_type):
        """Method to drop likelihood_blocks with nan for cls of the selected statistic type
        """

        self._likelihood_blocks = [like_ob for like_ob in self._likelihood_blocks
                                   if like_ob.getCLs(stat_type) is not None]


    def get_sorted_likelihood_blocks(self,stat_type):
        """
        The list of reduced component likelihood blocks extracted from the ``YODA`` file, sorted according
        the test statisitic of type `stat_type`.

        **type** ( ``list`` [ :class:`~contur.factories.likelihood.Likelihood` ])

        """
        if stat_type in self._sorted_likelihood_blocks.keys():
            return self._sorted_likelihood_blocks[stat_type]
        else:
            return None
        
    def set_sorted_likelihood_blocks(self, value, stat_type):
        self._sorted_likelihood_blocks[stat_type] = value


    def get_dominant_pool(self,stat_type):
        """returns the likelihood block with the highest confidence level"""
        try:
            tmp = max(self._sorted_likelihood_blocks[stat_type], key=lambda block: block.getCLs(stat_type))
        except ValueError:
            tmp = None
        return tmp


    @property
    def likelihood_blocks(self):
        """The list of all component likelihood blocks extracted from the ``YODA`` file

        This attribute is the total information in the ``YODA`` file, but does not account for potential correlation/
        overlap between the members of the list

        **type** ( ``list`` [ :class:`~contur.factories.likelihood.Likelihood` ])
        """
        return self._likelihood_blocks
    
    @likelihood_blocks.setter
    def likelihood_blocks(self, value):
        self._likelihood_blocks = value


    def get_full_likelihood(self,stat_type):
        """The full likelihood representing the ``YODA`` file in it's entirety

        **type** (:class:`~contur.factories.likelihood.CombinedLikelihood`)
        """
        try:
            return self._full_likelihood[stat_type]
        except TypeError:
            return self._full_likelihood
            
        
    def set_full_likelihood(self, stat_type, value):
        self._full_likelihood[stat_type] = value

    def __repr__(self):
        return "%s with %s blocks, holding %s" % (self.__class__.__name__, len(self.likelihood_blocks), self.likelihood)

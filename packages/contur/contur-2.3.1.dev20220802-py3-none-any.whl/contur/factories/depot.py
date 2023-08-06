"""

The Depot module contains the Depot class. This is intended to be the high level analysis control, 
most user access methods should be implemented at this level

"""

import os
import pickle
import numpy as np

import contur
import contur.factories.likelihood as lh
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.utils as cutil
from contur.factories.yoda_factories import YodaFactory


class Depot(object):
    """ Parent analysis class to initialise

    This can be initialised as a blank canvas, then the desired workflow is to add parameter space points to the Depot using
    the :func:`add_point` method. This appends each considered point to the objects internal :attr:`inbox`

    Path for writing out objects is determined by cfg.plot_dir

    :Keyword Arguments:
        * **noStack** (``Bool``) -- Flag if visual objects should be automatically stacked

    """

    def __init__(self, noStack=False):

        self._inbox = []
        self._NoStack = noStack


    def write(self, outDir):
        """Function to write out a "map" file containing the full pickle of this depot instance

        :param outDir:
            String of filesystem location to write out the pickle of this instance to
        :type outDir: ``string``

        """
        cutil.mkoutdir(outDir)
        path_out = os.path.join(outDir,cfg.mapfile)

        cfg.contur_log.info("Writing output map to : " + path_out)

        with open(path_out, 'wb') as f:
            pickle.dump(self, f, protocol=2)

    def add_custom_point(self, logfile, param_dict):
        """Function to add a custom file, typically read as a string, to the """
        self._inbox.append(ParamYodaPoint(
            yodaFactory=logfile, paramPoint=param_dict))

    def add_point(self, yodafile, param_dict):
        """
        Add yoda file and the corresponding parameter point into the depot
        """

        yFact = YodaFactory(yodaFilePath=yodafile, noStack=self._NoStack)


        for stat_type in cfg.stat_types:

            # get test statistics for each block
            lh.likelihood_blocks_find_dominant_ts(yFact.likelihood_blocks,stat_type)

            # get cls for each block
            lh.likelihood_blocks_ts_to_cls(yFact.likelihood_blocks,stat_type)
                
            # drop blocks with nan for cls value
           # yFact.drop_na_likelihood_blocks(stat_type)

        # combine subpools (does it for all test stats, but has to be done after we have found the dominant bin for each test stat (above)
        lh.combine_subpool_likelihoods(yFact.likelihood_blocks, omitted_pools="")

        for stat_type in cfg.stat_types:
            
            # sort the blocks according to this test statistic
            yFact.set_sorted_likelihood_blocks(lh.sort_blocks(yFact.likelihood_blocks,stat_type),stat_type)

            yFact.set_full_likelihood(stat_type,lh.build_full_likelihood(yFact.get_sorted_likelihood_blocks(stat_type),stat_type))

            if yFact.get_full_likelihood(stat_type) is not None:
                cfg.contur_log.info(
                    "Added yodafile with reported {} exclusion of: {} ".format(stat_type,str(yFact.get_full_likelihood(stat_type).getCLs())))
            else:
                cfg.contur_log.info("No {} likelihood could be evaluated".format(stat_type))
                
        
        self._inbox.append(ParamYodaPoint(
            yodaFactory=yFact, paramPoint=param_dict))

    def resort_points(self):
        """Function to trigger rerunning of the sorting algorithm on all items in the inbox, 
        typically if this list has been affected by a merge by a call to :func:`contur.depot.merge`
        """

        for p in self._inbox:
            for stat_type in cfg.stat_types:
                p.yoda_factory.resort_blocks(stat_type)

    def merge(self, depot):
        """
        Function to merge this conturDepot instance with another.
        
        Points with identical parameters will be combined. If point from the input Depot is not present in this Depot,
        it will be added.

        :param depot:
            Additional instance to conturDepot to merge with this one
        :type depot: :class:`contur.conturDepot`


        """
        new_points = []
        for point in depot.inbox:

            merged = False

            # look through the points to see if this matches any.
            for p in self._inbox:

                if not merged:
                    same = True
                    valid = True
                    for parameter_name, value in p.param_point.items():
                        try:
                            # we don't demand the auxilliary parameters match, since they can be things like
                            # cross secitons, which will depend on the beam as well as the model point.
                            if point.param_point[parameter_name] != value and not parameter_name.startswith("AUX:"):
                                same = False
                                break
                        except KeyError:
                            cfg.contur_log.warning("Not merging. Parameter name not found:" + parameter_name)
                            valid = False

                    # merge this point with an existing one
                    if same and valid:
                        cfg.contur_log.debug("Merging {} with {}".format(point.param_point,p.param_point))
                        for stat_type in cfg.stat_types:
                            cfg.contur_log.debug("Previous CLs: {} , {}".format(point.yoda_factory.get_full_likelihood(stat_type).getCLs(),p.yoda_factory.get_full_likelihood(stat_type).getCLs()))
                            blocks = p.yoda_factory.get_sorted_likelihood_blocks(stat_type)
                            blocks.extend(point.yoda_factory.get_sorted_likelihood_blocks(stat_type))

                        merged = True

            # this is a new point
            if not merged:
                new_points.append(point)
                cfg.contur_log.debug("Adding new point {} with dominant.".format(point.param_point))
                

        if len(new_points)>0:
            cfg.contur_log.debug("Adding {} new points to {}".format(len(new_points),len(self._inbox)))
            self._inbox.extend(new_points)


    def _build_frame(self, include_dominant_pools=False, include_per_pool_cls=False):
        """:return pandas.DataFrame of the inbox points"""
        try:
            import pandas as pd
        except ImportError:
            cfg.contur_log.error("Pandas module not available. Please, ensure it is installed and available in your PYTHONPATH.")

        try:
            frame = pd.DataFrame(
                [param_yoda_point.param_point for param_yoda_point in self._inbox])

            for stat_type in cfg.stat_types:
                frame['CL{}'.format(stat_type)] = [
                    param_yoda_point.yoda_factory.get_full_likelihood(stat_type).getCLs() for param_yoda_point in self._inbox]

                if include_dominant_pools:
                    frame['dominant-pool{}'.format(stat_type)] = [
                        param_yoda_point.yoda_factory.get_dominant_pool(stat_type).pools
                        for param_yoda_point in self._inbox
                    ]
                    frame['dominant-pool-tag{}'.format(stat_type)] = [
                        param_yoda_point.yoda_factory.get_dominant_pool(stat_type).tags
                        for param_yoda_point in self._inbox
                    ]

                if include_per_pool_cls:
                    poolsDict = {}
                    for param_yoda_point in self._inbox:
                       for block in param_yoda_point.yoda_factory.get_sorted_likelihood_blocks(stat_type):
                          poolName = block.pools
                          poolCLS = block.getCLs(stat_type)
                          if not poolName in poolsDict.keys(): poolsDict[poolName] = []
                          poolsDict[poolName] += [poolCLS]
                       maxLen = max([len(v) for k,v in poolsDict.items()])

                       #deal with cases where an entry for a given pool is missing
                       for k,v in poolsDict.items():
                         while len(v) < maxLen:
                            cfg.contur_log.warning("Point {} has no entry for pool {}: padding with 0.".format(self._inbox.index(param_yoda_point), k))
                            v += [0]

                    for  pool, cls_values in sorted(poolsDict.items()):
                      frame[pool+stat_type] = cls_values
            return frame
        except:
#            cfg.contur_log.error("Inbox is empty, add parameter points to depot")
            raise
            
    def export(self, path, include_dominant_pools=True, include_per_pool_cls=False):
        self._build_frame(include_dominant_pools, include_per_pool_cls).to_csv(path, index=False)

    def write_summary_file(self, message):
        """
        Write a brief text summary of a conturDepot, describing the run conditions and results.

        If cfg.gridMode is False, will also write info about the
        most sensitive histograms in each pool, for parsing by contur-mkhtml

        :param message: text (string) message containing the run conditions for this depot

        the name of the directory to write the file into will be determined by cfg.output_dir

        """

        cutil.mkoutdir(cfg.output_dir)
        sumfn = open(os.path.join(cfg.output_dir,cfg.summary_file), 'w')

        if cfg.gridMode:
            sumfn.write(message)
        else:

            # summary function will just read the first entry in the depot inbox
            result = ""
            for stat_type in cfg.stat_types:
                try:
                    result += "\nCombined {} exclusion for these plots is {:15.13f} % ".format(stat_type, self.inbox[0].yoda_factory.get_full_likelihood(stat_type).getCLs() * 100.0)
                except:
                    result += "\nCould not evaluate {} exclusion for these data.".format(stat_type)

            sumfn.write(message + "\n" + result + "\n")
            sumfn.write("\npools")

            yfactory = self.inbox[0].yoda_factory
            for pool in cdb.get_pools():
                pool_summary = "\nPool:{}\n".format(pool)


                got_it = []
                for lhb in yfactory.likelihood_blocks:            
                    if lhb.pools == pool:
                        for stat_type in cfg.stat_types:
                            if yfactory.get_sorted_likelihood_blocks(stat_type) is not None and lhb in yfactory.get_sorted_likelihood_blocks(stat_type):
                                pool_summary+="Exclusion with {}={:.8f}\n".format(stat_type,lhb.getCLs(stat_type))
                                pool_summary+="{}\n".format(lhb.tags)
                                got_it.append(stat_type)

                if len(got_it)>0:
                    for stat_type in cfg.stat_types:
                        if not stat_type in got_it:
                            pool_summary+="No exclusion evaluated for {}\n".format(stat_type,lhb.getCLs(stat_type))
                    sumfn.write(pool_summary)

            cfg.contur_log.info(result)

            sumfn.close()


    def write_text_summary_deprecated(self, message):
        """
        Write a brief text summary of a run, and also write info about the
        most sensitive histograms in each pool
        This doesnt appear to be used, so will be removed in future versions if not.
        """
        cutil.mkoutdir(cfg.output_dir)
        sumfn = open(os.path.join(cfg.output_dir,cfg.grid_summary_file),'w')

        sumfn.write("from depot")
        
        cfg.contur_log.info("Writing summary for grid mode to : {}".format(sumfn.name))

        sumfn.write(message)
        if self.inbox is None:
            sumfn.write("\nParameter point is empty! \n")
        else:
            sumfn.write("Number of parameter points: " + str(len(self.inbox))+"\n")
            # sumfn.write("type: " +str(type(self.inbox)))

        for param_yoda_point in self.inbox:
            sumfn.write("\n**************************************\n")

            if param_yoda_point.yoda_factory.get_full_likelihood(cfg.databg).getCLs() is not None:
                result = " \nCombined exclusion for these plots is %.2f %% \n" % (
                        param_yoda_point.yoda_factory.get_full_likelihood(cfg.databg).getCLs() * 100.0)
            else:
                result = "Could not evaluate exclusion for these data. Try turning off theory correlations?"

            sumfn.write("\n" + result + "\n")
            # write parameter point in the Summary file
            for param, val in param_yoda_point.param_point.items():
                sumfn.write(param + " = " + str(val) + "\n")

            sumfn.write("\npools")
            import rivet
            for x in param_yoda_point.yoda_factory.get_sorted_likelihood_blocks(cfg.databg):
                sumfn.write("\n" + x.pools)
                sumfn.write("\n" + str(x.getCLs(cfg.databg)))
                sumfn.write("\n" + rivet.stripOptions(x.tags))

        sumfn.close()

        
    @property
    def inbox(self):
        """
        The master list of :class:`~contur.factories.depot.ParamYodaPoint` instances added to the Depot instance

        **type** ( ``list`` [ :class:`~contur.factories.depot.ParamYodaPoint` ])
        """
        return self._inbox

    @property
    def frame(self):
        """
        A ``pandas.DataFrame`` representing the CLs interval for each point in :attr:`inbox`

        **type** (``pandas.DataFrame``)
        """
        return self._build_frame()

    def __repr__(self):
        return "%s with %s added points" % (self.__class__.__name__, len(self._inbox))


class ParamYodaPoint(object):
    """
    Book-keeping class relating a parameter point and a yoda factory

    :param paramPoint:
        **key** ``string`` param name : **value** ``float``
    :type paramPoint: ``dict``
    :param yodaFactory:
        yoda_factory object, conturs YODA file reader
    :type yodaFactory: :class:`contur.depot.yoda_factory`

    """

    def __init__(self, paramPoint, yodaFactory):
        self.param_point = paramPoint
        self.yoda_factory = yodaFactory

    def __repr__(self):
        return repr(self.param_point)

""" main model of plotting functions
*TODO* rename functions from CamelCase to under_score
"""

import os
import sys
import warnings

import contur
from contur.plot.axis_labels import get_axis_labels
from contur.factories.depot import Depot
from contur.plot import color_config
import contur.config.config as cfg
import contur.util.utils as cutil


import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from matplotlib.gridspec import GridSpec
from collections import OrderedDict, defaultdict


import scipy

import matplotlib.colors as mcolors

warnings.filterwarnings("ignore")



def color_tint(col, tintfrac):
    """
    Return a colour as rgb tuple, with a fraction tintfrac of white mixed in
    (or pass a negative tintfrac to mix with black, giving a shade rather than tint
    """
    tintfrac = max(-1.0, min(1.0, tintfrac))
    maincol = mpl.colors.to_rgb(col) if type(col) is str else col
    if tintfrac > 0:
        return (1-tintfrac)*np.array(maincol) + tintfrac*np.array([1., 1., 1.])
    elif tintfrac < 0:
        return (1-abs(tintfrac))*np.array(maincol)
    else:
        return maincol


def get_pool_color(pool, tints=True):
    """
    Return the colour for a given analysis pool, optionally tinted
    according to beam energy
    """
    for poolGroupName, poolGroup in color_config.POOLCOLORS.items():
        # find pool group
        pools = poolGroup["pools"]
        if pool not in pools:
            continue
        color = poolGroup["color"]
        tfrac = 0.1*pow(-1, len(pools)) * pools.index(pool) if tints else 0.0
        return color_tint(color, tfrac)

    # if we get here, we didn't find a colour for this pool.
    if cfg.map_colorCycle==None:
        cfg.map_colorCycle = iter(color_config.CONTURCOLORS())
    c = next(cfg.map_colorCycle)["color"]

    cfg.contur_log.warning('No colour found for pool {}. Using {}.'.format(pool,c))
    return c


class ConturPlotBase(Depot):
    """
    ConturPlotBase extends the depot class to dress things nicely for plotting, it also contains all the steering
    functions the default plotting macro needs

    .. todo:: a config file based setup to stop the command line argument bloat in the plotting macro
    """
    
    def __init__(self, conturDepot, outPath, plotTitle="", savePlotFile=False, omittedPools="", iLevel=3,
                 iSigma=0.75, clLevel=0, style="DRAFT", showcls=False, simplecls=False, primary_stat=cfg.smbg,
                 show_secondary=False):

        # extend from a depot class instance
        self.__dict__.update(conturDepot.__dict__)

        # map axis and plot axis are two different objects due to idiosyncracies in pcolormesh
        # mapAxis is the true sampled points
        # plotAxis is the offset values for plotting
        # _bookmapAxis is just for bookkeeping
        self._bookmapAxis = defaultdict(list)
        self._mapAxis = {}
        self._plotAxis = {}
        self._show_secondary = show_secondary
        self._primary_stat = primary_stat
        
        self.build_axes()
                
        self.outputPath = outPath

        self.plotList = []
        self.plotTitle = plotTitle
        self.do_plot_pools = True
        self.doSavePlotfile = savePlotFile
        self.omittedPools = omittedPools
        self.iLevel = iLevel
        self.iSigma = iSigma
        self.clLevel = clLevel
        self.showcls = showcls
        self.style = style.upper()
        self.simplecls = simplecls
        self.made_cbar = False

        if self.doSavePlotfile:
            # tell mpl to not worry if we keep a lot of figures open
            rcParams['figure.max_open_warning'] = 100

        self.external_grids = []
        self.alt_grids = []
        self.external_functions=[]
        self.plot_objects = {}

        # Look up table for some convenient default axis labels
        self.axisLabels = get_axis_labels()


    def dump_plot_objects(self):
        """
        Small function to dump a pickle of the plot objects if requested, this is to allow any mpl image manipulation
        without using the contur package at all
        """
        path_out = os.path.join(self.outputPath, 'contur.plot')
        import pickle
        with open(path_out, 'w') as f:
            pickle.dump(self.plot_objects, f)
        cfg.contur_log.info("Writing output plot dict to:", path_out)

    def dump_color_palette_tex(self):
        """
        Function to dump a .tex file containing a LaTeX legend for the dominant pools plots.
        """
        pools = set() # list with unique elements

        # get pools
        for level, anaNames_level in enumerate(self.poolNames):
            for anaName in anaNames_level:
                for poolGroupName, poolGroup in color_config.POOLCOLORS.items():
                    if anaName in poolGroup["pools"]:
                        pools.add(poolGroupName)

        # print latex commands
        tex_output = r"\documentclass{article}" + "\n\n"
        tex_output += r"\usepackage{tikz}" + "\n\n"
        tex_output += r"\newcommand{\swatch}[1]{\tikz[baseline=-0.6ex]"
        tex_output += r"\node[fill=#1,shape=rectangle,draw=black,thick,minimum width=5mm,rounded corners=0.5pt](){};}" + "\n"
        tex_output += r"\newcommand{\met}{\ensuremath{E_T^{\rm miss}}}" +"\n\n"
        tex_output += r"% color definitions" + "\n"

        # dump color defintions
        for pool in pools:
            colorName = color_config.POOLCOLORS[pool]["color"]
            colorHex = mpl.colors.to_hex(colorName)[1:] # first char is "#"
            tex_output += r"\definecolor{%s}{HTML}{%s}" % (colorName, colorHex.upper()) + "\n"

        # dump pool colors
        num_cols = 4
        tex_output += "\n" + r"\begin{document}" + "\n"
        tex_output += "    % pool-name legend\n"
        tex_output += r"    \begin{tabular}{" + num_cols*"l" + "}\n"

        for num, pool in enumerate(pools):
            colorName = color_config.POOLCOLORS[pool]["color"]
            latexName = color_config.POOLCOLORS[pool]["latexName"]
            tex_output += r"        \swatch{%s}~%s" % (colorName, latexName)
            if num % num_cols == num_cols-1:
                tex_output += r" \\"
            else:
                tex_output += r" &"
            tex_output += "r\n"

        tex_output += r"    \end{tabular}" + "\n"
        tex_output += r"\end{document}"

        path_out = os.path.join(self.outputPath, "dominantPoolsLegend.tex")
        with open(path_out, 'w') as f:
            f.write(tex_output)

    def build_axes_from_grid(self, xarg, yarg, logX=False, logY=False, xlabel=None, ylabel=None):
        """
        Function to build the axes out of the underlying map, creates an AxesHolder instance to store the info and pass
        nicely to the plotting engine

        .. todo:: Refactor how we store the grids in general, should just reuse the initial scanning functions to build the space OTF

        """
        try:
            self.check_args(xarg, yarg)
            self.build_grid(xarg, yarg)
        except cfg.ConturError:
            sys.exit(1)
            
        if xlabel:
            xlabel = xlabel
        elif xarg in self.axisLabels:
            xlabel = self.axisLabels[xarg]
        else:
            xlabel = xarg

        if ylabel:
            ylabel = ylabel
        elif yarg in self.axisLabels:
            ylabel = self.axisLabels[yarg]
        else:
            ylabel = yarg

        self.build_axes()

        self.axHolder = AxesHolder(xAxis=self.map_axis[xarg], xAxisMesh=self.plot_axis[xarg], xLabel=xlabel,
                                   xLog=logX, yAxis=self.map_axis[yarg],
                                   yAxisMesh=self.plot_axis[yarg], yLabel=ylabel, yLog=logY, title=self.plotTitle)


    def plot_figures(self):
        """
        make the various figures
        """
        
        # First the combined
        plotBase = conturPlot(saveAxes=self.doSavePlotfile, plotTitle=self.plotTitle,
                              iLevel=self.iLevel, iSigma=self.iSigma, style=self.style, showcls=self.showcls,
                              primary_stat=self._primary_stat)
        cutil.mkoutdir(self.outputPath)
        cfg.contur_log.info("Starting plotting engine, outputs written to {}".format(self.outputPath))

        plotBase.add_grid(self.conturGrid, "combined",
                          self.outputPath, self.axHolder)
        #if self.external_grids or self.external_functions:
        plotBase.add_external_data_grids(self.alt_grids)
            
        # Plot the heatmap and levels side-by-side
        plotBase.plot_hybrid()
        # Plot the mesh with limit-contour overlays
        plotBase.plot_mesh_overlay()
        # Plot the separated limit contour and mesh plots
        plotBase.plot_mesh(make_cbar=True)
        plotBase.plot_levels()

        # Now plot dominant pools
        for level in range(self.clLevel):
            cfg.contur_log.info("Plotting dominant pools: level %i (%i/%i)" %
                                          (level, level+1, self.clLevel))

            # Simple dpool plot
            levelName = "dominantPools{:d}".format(level)
            plotBase = conturPlot(saveAxes=self.doSavePlotfile, iLevel=self.iLevel,
                                  iSigma=self.iSigma, style=self.style, showcls=self.showcls, primary_stat=self._primary_stat)
            plotBase.add_grid(self.conturGrid, levelName,
                              self.outputPath, self.axHolder)
            #if self.external_grids or self.external_functions:
            plotBase.add_external_data_grids(self.alt_grids)
            plotBase.plot_pool_names(self, level)
            self.plot_objects[levelName] = plotBase.figs

            # Full CLs-info dpool plots
            if not self.simplecls:
                levelName += "CLs"
                plotBase = conturPlot(saveAxes=self.doSavePlotfile, iLevel=self.iLevel,
                                      iSigma=self.iSigma, style=self.style, showcls=self.showcls, primary_stat=self._primary_stat)
                plotBase.add_grid(self.conturGrid, levelName,
                                  self.outputPath, self.axHolder)
                plotBase.plot_pool_CLs(self, level)
                self.plot_objects[levelName] = plotBase.figs

        # dump latex legend for colors
        if self.style == "FINAL":
            self.dump_color_palette_tex()

        # Save the plot data for later cosmetic tweaking
        if self.doSavePlotfile:
            self.plot_objects["combined"] = plotBase.figs

        # Now the individual pools' plots
        if self.do_plot_pools:
            outpath = os.path.join(self.outputPath, "pools")
            cutil.mkoutdir(outpath)

            cfg.contur_log.info("Requested plotting of individual analysis pools, found %s pools to plot" % len(
                self.conturGridPools.keys()))

            for idx, (title, grid) in enumerate(self.conturGridPools.items()):
                cfg.contur_log.info("plot %s (%d/%d done)" %
                                              (title, idx+1, len(self.conturGridPools.keys())))
                plotBase = conturPlot(saveAxes=self.doSavePlotfile, iLevel=self.iLevel,
                                      iSigma=self.iSigma, style=self.style, showcls=self.showcls, primary_stat=self._primary_stat)
                plotBase.add_grid(grid, title, outpath, self.axHolder)
                plotBase.plot_levels()
                plotBase.plot_mesh(make_cbar=False)
                if self.doSavePlotfile:
                    self.plot_objects[title] = plotBase.figs

    def set_output_path(self, outputpath):
        """Convenience switch to set the output path name for the PlotBase instance"""
        self.outputPath = outputpath

    def check_args(self, xarg, yarg):
        """Function to call to check the requested arguments of what to plot are compatible with what is in the map"""
        # for now lets just check against the first point in the list, this should be properly declared from the input file
        try:
            if not all([x in self.inbox[0].param_point.keys() for x in (xarg, yarg)]):
                cfg.contur_log.critical("Arguments for plotting do not match the available parameters in this map, ensure the parameters are from: {}".format(self.inbox[0].param_point.keys()))

                raise cfg.ConturError("Arguments for plotting do not match the available parameters in this map, ensure the parameters are from: {}".format(self.inbox[0].param_point.keys()))
        except IndexError as e:
            cfg.contur_log.error(
                'Exception raised: {}. Is it possible this is an empty map file?'.format(e))
            sys.exit(1)

    def add_external_grids(self, ExternalGrids):
        """Switch to provide the external exclusion grid files to the PlotBase instance"""
        self.external_grids = ExternalGrids

    def add_external_functions(self, ExternalFunctions):
        """Switch to provide the external exclusion function files to the PlotBase instance"""
        self.external_functions = ExternalFunctions

    def build_grid_from_grid(self, xarg, yarg):
        """
        Build a plotting grid from the supplied external grids
        Assumes the keys for the parameters are the same for all points and grabs them from first point
        :param xarg: the x-axis variable name
        :param yarg: the y-axis variable name

        """

        paramkeys = self.inbox[0].param_point.keys()


        for fn_name, fn in self.external_grids:

            store = []
            try:
                store  = fn(paramkeys)
            except TypeError:
                cfg.contur_log.critical("Error parsing extrnal grid in {}. Did you mean to treat this as a function instead? (-ef)".format(fn_name))
                sys.exit(1)

            if store[0] is not None:
                new_grid = grid()
                new_grid.fill = store[2]
                new_grid.color = store[3]
                xaxis = list(np.unique([i[xarg] for i in store[0]]))
                yaxis = list(np.unique([i[yarg] for i in store[0]]))
              
                new_grid.axes = AxesHolder(xaxis, 0, xarg, 0, yaxis, 0, yarg, 0, self.plotTitle)
                new_grid.label = fn_name
                new_grid.grid = np.zeros((len(xaxis), len(yaxis)))                
                for p, v in zip(store[0], store[1]):
                    xpos = xaxis.index(p[xarg])
                    ypos = yaxis.index(p[yarg])
                    new_grid.grid[xpos][ypos] = v
                self.alt_grids.append(new_grid)
                cfg.contur_log.info("Loaded data grid {}".format(fn_name))

    def build_grid_from_data(self, stat_type, xarg, yarg):
        """
        Build a plotting grid from the expected and secondary statistics
        Assumes the keys for the parameters are the same for all points and grabs them from first point
        :param xarg: the x-axis variable name
        :param yarg: the y-axis variable name

        """

        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]

        new_grid = grid()
        new_grid.grid = np.zeros((len(xaxis), len(yaxis)))
        new_grid.label = str(stat_type)
        new_grid.fill = False
        new_grid.color = cfg.contour_colour[stat_type]
        new_grid.axes = AxesHolder(xaxis, 0, xarg, 0, yaxis, 0, yarg, 0, self.plotTitle)
        new_grid.styles = [cfg.contour_style[stat_type]]
        
        
        for point in self.inbox:
            missing_pools=False
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))
            if self.omittedPools:
                point.yoda_factory.resort_blocks(self.omittedPools)

            new_grid.grid[xpos][ypos] = point.yoda_factory.get_full_likelihood(stat_type).getCLs()

        self.alt_grids.append(new_grid)
            
    def build_grid_from_functions(self, xarg, yarg):
        """
        Builds the grid to pointwise evaluate external function on
        :param xarg: the x-axis variable name
        :param yarg: the y-axis variable name

        """

        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]
        paramkeys = self.inbox[0].param_point.keys()

        # Just a bit of book keeping to ensure the theory functions defined are always in alphabetical order
        # Can't remember why I thought this was necessary?
        _temp = {k: np.zeros((len(xaxis), len(yaxis))) for k, v in [t for t in self.external_functions]}
        contur_grid_theory = OrderedDict(
            sorted(_temp.items(), key=lambda v: (v[0].upper(), v[0].islower())))

        theory_axes = AxesHolder(xaxis, 0, xarg, 0, yaxis,
                                 0, yarg, 0, self.plotTitle)

        fills = {}
        colors = {}
        for point in self.inbox:
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))

            for k, v in self.external_functions:
                try:
                    contur_grid_theory[k][xpos][ypos], fills[k], colors[k] = v(point.param_point)
                except KeyError as ke:
                    cfg.contur_log.critical(
                        "Could not parse the parameters requested by {}. \nThe known parameters are {}. The exception was:{}".format(
                            k, point.param_point.keys(),ke))

                    sys.exit(1)

        for k,v in contur_grid_theory.items():
            new_grid = grid()
            new_grid.grid = v
            new_grid.label = k
            new_grid.axes = theory_axes
            new_grid.fill = fills[k]
            new_grid.color = colors[k]

            cfg.contur_log.info("Built theory grid")


    def build_special_grid(self, xarg, yarg):
        """
        build_special_grid allows us to build an empty grid from the sampled points dictionary, this is used for adding custom
        functions to evaluate on the grid. For example see the log-read snippets prepared for the BL paper
        """

        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]
        self.conturGrid = np.zeros((len(xaxis), len(yaxis)))
        for point in self.inbox:
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))
            self.conturGrid[xpos][ypos] = point.yoda_factory

    def get_pool_name_from_ID(self, currID):
        """
        return the name of the analysis pool, given the ID number
        """
        return list(self.conturGridPools.keys())[currID]

    def build_grid(self, xarg, yarg):
        """
        Build the grid in the style mpl needs to make it easy to plot, converts the unordered dictionary of paramPoints into
        a structured numpy array

        .. todo:: revive ND capabilities, might need a total overhaul of how we do this
        """
        # for now we will just scope all the grids we need in the projection
        # fix signs if necessary
        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]

        self.conturGrid = np.zeros((len(xaxis), len(yaxis)))
        # again we will just scope the whole grid off the first entry, this should be encoded as a master record in the depot
        self.conturGridPools = {key: np.zeros((len(xaxis), len(yaxis))) for key in
                                [p.pools for p in self.inbox[0].yoda_factory.get_sorted_likelihood_blocks(self._primary_stat)]}
        # It would be nicer to reuse the sampled grid but that isn't high enough resolution
        if self.external_grids:
            self.build_grid_from_grid(xarg, yarg)
        if self.external_functions:
            self.build_grid_from_functions(xarg,yarg)


        if self._show_secondary:
            # add stats other than the primary one

            if self._primary_stat==cfg.databg: 
                self.build_grid_from_data(cfg.smbg,xarg,yarg)

            if self._primary_stat==cfg.smbg: 
                self.build_grid_from_data(cfg.databg,xarg,yarg)

            self.build_grid_from_data(cfg.expected,xarg,yarg)

        elif self._primary_stat==cfg.smbg:
            # if primary stat is smbg, we always want to plot the expected.
            self.build_grid_from_data(cfg.expected,xarg,yarg)
            
        self.poolIDs = np.full((len(xaxis), len(yaxis), len(
            self.conturGridPools.keys())), -1, dtype=int)
        self.poolCLs = np.full((len(xaxis), len(yaxis), len(
            self.conturGridPools.keys())), -1, dtype=float)

        for point in self.inbox:
            missing_pools=False
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))
            if self.omittedPools:
                point.yoda_factory.resort_blocks(self.omittedPools)

            self.conturGrid[xpos][ypos] = point.yoda_factory.get_full_likelihood(self._primary_stat).getCLs()

            for zpos, p in enumerate(point.yoda_factory.get_sorted_likelihood_blocks(self._primary_stat)):
                try:
                    self.conturGridPools[p.pools][xpos][ypos] = p.getCLs(self._primary_stat)
                    try:
                        self.poolIDs[xpos][ypos][zpos] = list(self.conturGridPools.keys()).index(
                            p.pools)
                        self.poolCLs[xpos][ypos][zpos] = p.getCLs(self._primary_stat) * 100  # in %

                    except IndexError as ie:
                        missing_pools=True

                except KeyError:
                    KeyError("Could not find pool %s for point %s, grid might be malformed" % (
                        p, point.param_point))

                if missing_pools:
                    cfg.contur_log.warning("Missing pools for {}".format(point.param_point))

        if not self.clLevel > 0:
            return  # nothing to do anymore if clLevel plots are not printed

        # sort by CLs: get sorting index from poolCLs, z-axis; reverse order by "-"
        index = np.argsort(-self.poolCLs, axis=2)

        # sort poolGrids
        try:
            self.poolIDs = np.take_along_axis(self.poolIDs, index, axis=2)
            self.poolCLs = np.take_along_axis(self.poolCLs, index, axis=2)
        except Exception as e:
            cfg.contur_log.error(e)
            cfg.contur_log.error(
                "The problem may be you have numpy older than 1.15.0. Upgrade, or set --num-dpools 0")
            sys.exit(1)

        # remove unneccessary entries
        self.poolIDs = self.poolIDs[:, :, :self.clLevel]
        self.poolCLs = self.poolCLs[:, :, :self.clLevel]

        self.poolNames = [[]]
        numAvailLevels = self.poolCLs.shape[2]
        if self.clLevel > numAvailLevels:
            cfg.contur_log.warning("The number of requested levels of dominant pools (%i) is larger than the number of available dominant pools (%i)." % (
                self.clLevel, numAvailLevels))
            cfg.contur_log.warning(
                "Setting number of requested levels to number of available pools (%i)." % numAvailLevels)
            self.clLevel = numAvailLevels
        for level in range(self.clLevel):
            # make lists out of 2D arrays
            listCLs = self.poolCLs[:, :, level].flatten()
            listIDs = self.poolIDs[:, :, level].flatten()

            # sort IDs by CLs
            listIDs = np.take_along_axis(listIDs, np.argsort(-listCLs), axis=0)

            # remove duplicates
            distinctListIDs = []
            for currID in listIDs:
                if not currID in distinctListIDs:
                    distinctListIDs.append(currID)

            # find up to max_pools-1/ max_pools highest-CLs pools
            usefulKeys = []
            max_pools = 20
            # we have exactly max_pools or less contributing pools, which our colormap can support
            if len(distinctListIDs) <= max_pools:
                usefulKeys = distinctListIDs
            else:  # select only up to max_pools-1 leading pools so we can add one pool "others"
                usefulKeys = distinctListIDs[:max_pools-1]

            # create shortlist of pool names
            self.poolNames.append([])
            for entry in usefulKeys:
                self.poolNames[level].append(self.get_pool_name_from_ID(entry))

            # sort poolKeys and poolNames
            sort_by_hue = True
            if sort_by_hue:  # get sort index for hue sort
                import matplotlib.colors as mcolors
                poolhsvs = []
                for poolName in self.poolNames[level]:
                    poolhsvs.append(tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(
                        get_pool_color(poolName)))))  # < TODO: tint control
                sort_index = np.argsort(poolhsvs, axis=0)[:, 0]
            else:  # get sort index for alphabetical sort
                poolInfo = np.array(
                    [np.array([x.split("_")[0], x.split("_")[2]]) for x in self.poolNames[level]])
                poolEnergies = np.array([int(x.split("_")[1])
                                         for x in self.poolNames[level]])
                sort_index = np.lexsort((poolInfo[:, 1], poolEnergies, poolInfo[:, 0]))[
                    ::-1]  # get sort index, [::-1] for reverse order

            self.poolNames[level] = list(np.take_along_axis(
                np.array(self.poolNames[level]), sort_index, axis=0))  # sort by given index
            usefulKeys = list(np.take_along_axis(
                np.array(usefulKeys), sort_index, axis=0))  # sort by given index

            # insert dummy for all other pools if not <=max_pools contributing pools
            if not len(distinctListIDs) <= max_pools:
                # need to add to usefulKeys as well so that indices match
                usefulKeys.insert(0, -1)
                self.poolNames[level].insert(0, "other")

            # change IDs in poolIDs to shorter ID list
            otherPools = []
            # loop over all entries of 3D matrix, allowing for modifications
            with np.nditer(self.poolIDs[:, :, level], op_flags=['readwrite']) as it:
                for entry in it:
                    if entry >= 0:
                        try:
                            newID = usefulKeys.index(entry)
                        except ValueError:  # pool is not important enough for shorter index; list as "other"
                            poolName = self.get_pool_name_from_ID(entry)
                            if not poolName in otherPools:
                                otherPools.append(poolName)
                            newID = -1
                        entry[...] = newID


    def build_axes(self):
        """Function to build the axis dictionaries used for plotting, parameter space points are otherwise stored unordered

        :Built variables:
            * **mapAxis** (``dict``)
            * **plotAxis** (``dict``)

        @TODO should seperate the data structures from the plotting.

        """
        # hack 
        self._bookmapAxis['AUX:Zp']=[]

        for i in self._inbox:
            for k, v in i.param_point.items():
                if (k=="AUX:Zp"):
                    width = float(i.param_point['AUX:Zp'])
                    mass = float(i.param_point['mZp'])
                    ratio = str(width/mass)
                    self._bookmapAxis[k].append(ratio)
                else:
                    self._bookmapAxis[k].append(v)

        # Pcolormesh (which we use for visualisation) centres grid in bottom left corner of a cell, we need to shift the axis
        # this is a pain but we will truncate at the original max/min anyway so a guess is fine
        # first build the true axes
        for k, v in self._bookmapAxis.items():
            try:
                self._mapAxis[k] = np.unique(np.array(v, dtype=float))
                self._plotAxis[k] = (
                    self._mapAxis[k][1:] + self._mapAxis[k][:-1]) / 2
                # now the ugly offset
                if self._plotAxis[k].any():
                    try:
                        self._plotAxis[k] = np.insert(self._plotAxis[k], 0, self._plotAxis[k][0] - self._plotAxis[k][
                            1])  # -self.mapAxis[k][0])
                        self._plotAxis[k] = np.append(self._plotAxis[k], self._mapAxis[k][-1] + (
                            self._mapAxis[k][-1] - self._plotAxis[k][-1]))
                    except:
                        self._plotAxis[k] = self._mapAxis[k]
                else:
                    self._plotAxis[k] = self._mapAxis[k]
            except ValueError:
                # some parameters are not numeric, so we can't build an axis. But this is fine.
                pass
                    
    @property
    def map_axis(self):
        """Dictionary of the sampled values in each axis

        **type** (``dict``) --
        **key** -- Parameter name (``string``),
        **value** -- (:class:`numpy.ndarray`)
        """
        return self._mapAxis

    @map_axis.setter
    def map_axis(self, value):
        self._mapAxis = value

    @property
    def plot_axis(self):
        """Dictionary of the offset midpoints in each axis, for colormesh purposes

        **type** (``dict``) --
        **key** -- Parameter name (``string``),
        **value** -- (:class:`numpy.ndarray`)
        """
        return self._plotAxis

    @plot_axis.setter
    def plot_axis(self, value):
        self._plotAxis = value

            
class AxesHolder(object):
    """
    Data structure to keep things legible in the code, holds the Axes scoped from the map file and information about
    how we visualise it. Just used for book keeping
    """

    def __init__(self, xAxis, xAxisMesh, xLabel, xLog, yAxis, yAxisMesh, yLabel, yLog, title):
        self.xAxis = xAxis
        self.xAxisMesh = xAxisMesh
        self.xLabel = xLabel
        self.xLog = xLog
        self.yAxis = yAxis
        self.yAxisMesh = yAxisMesh
        self.yLabel = yLabel
        self.yLog = yLog
        self.title = title


class grid(object):
    """
    A grid of values which can be plotted (as a heatmap or a contour)
    """
    def __init__(self):
        self.label = None
        self.grid  = None
        self.axis  = None
        self.fill  = None
        self.color = None
        self.styles = ["dashed", "solid"]

class conturPlot(object):
    """conturPlot is the engine that interacts with the matplotlib.pyplot plotting library"""

    def __init__(self, saveAxes=False, plotTitle="", iLevel=3, iSigma=0.75, style="DRAFT", showcls=False, simplecls=False, primary_stat=cfg.smbg):
        # Initialise the basic single plot style
        self.style = style.upper()
        self.load_style_defaults()
        self.figs = []
        self.saveAxes = saveAxes
        self.plotTitle = plotTitle
        self.iLevel = iLevel
        self.iSigma = iSigma
        self.showcls = showcls
        self.simplecls = simplecls
        self.cmap = plt.cm.viridis
        self.alt_grids = []
        self._primary_stat = primary_stat

    def add_limits(self, ax, level=3, sigma=0.75):
        "Add the overlaid extra limit contours"

        for grid in self.alt_grids:

            grid.axes.xAxisZoom = scipy.ndimage.zoom(grid.axes.xAxis, level)
            grid.axes.yAxisZoom = scipy.ndimage.zoom(grid.axes.yAxis, level)
            gZoom = scipy.ndimage.zoom(grid.grid, level)
            gZoom = scipy.ndimage.gaussian_filter(gZoom, sigma*level)
            if grid.fill:
                ax.contourf(gird.axes.xAxisZoom, grid.axes.yAxisZoom, gZoom.T, colors=grid.color, levels=[0.95,10.0], alpha=0.3)  # , snap=True)
            ax.contour(grid.axes.xAxisZoom, grid.axes.yAxisZoom, gZoom.T, colors=grid.color, levels=[0.95], linestyles=grid.styles)
    
        # .. todo:: The contur/plot directory has a file LabelMaker to define
        # labels to add here, in future we could replicate
        #  the theory function file input to give a label input from file?
        # LabelMaker.BLCaseDE(self.axes[0])
        # LabelMaker.BLCaseA(self.axes[0])
        # LabelMaker.BLCaseB(self.axes[0])
        # LabelMaker.BLCaseC(self.axes[0])
        # LabelMaker.DM_LF(self.axes[0])


    def plot_hybrid(self):
        """
        Build the default contur output for combined limit, a hybrid plot showing both a colormesh of the underlying
        exclusion and the derived 1 and 2 sigma confidence intervals from this space
        Makes the file combinedHybrid.pdf.
        """

        cfg.contur_log.info("Plotting combined hybrid: heatmap and contours side-by-side.")
        
        self.fig, self.axes = plt.subplots(nrows=1, ncols=3, figsize=self.fig_dims_hybrid,
                                           gridspec_kw={"width_ratios": [1, 1, 0.08]})
        self.axes[1].set_title(
            label=r"\textsc{Contur}" + str(self.plotTitle), loc="right")  # \textsc{Contur}

        im0 = self.axes[1].pcolormesh(self.xAxisMesh, self.yAxisMesh, self.grid.T, cmap=self.cmap, vmin=0, vmax=1,
                                      snap=True)

        path_out = os.path.join(self.destination, self.label + "Hybrid")
        if self.xLog:
            self.axes[1].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.axes[1].set_yscale("log", nonpositive='clip')
        self.axes[0].set_ylabel(self.yLabel)
        self.axes[1].set_xlabel(self.xLabel)

        self.interpolate_grid(self.iLevel, self.iSigma)

        self.axes[0].contourf(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, cmap=self.cmap,
                              levels=[0.68, 0.95, 10], vmin=0.0, vmax=1.0)  # , alpha=0.6)  # , snap=True)
        self.axes[0].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[self._primary_stat],
                             levels=[0.68, 0.95, 10], vmin=0.0, vmax=1.0)

        # add theory/previous experiment limits
        colorCycle = iter(color_config.CONTURCOLORS())
        self.add_limits(self.axes[0],level=self.iLevel,sigma=self.iSigma)

        if self.xLog:
            self.axes[0].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.axes[0].set_yscale("log", nonpositive='clip')
        self.axes[0].set_ylabel(self.yLabel)
        self.axes[0].set_xlabel(self.xLabel)

        self.axes[0].set_ylim(top=max(self.yaxisZoom),
                              bottom=min(self.yaxisZoom))
        self.axes[0].set_xlim(right=max(self.xaxisZoom),
                              left=min(self.xaxisZoom))
        self.axes[1].set_ylim(top=max(self.yaxisZoom),
                              bottom=min(self.yaxisZoom))
        self.axes[1].set_xlim(right=max(self.xaxisZoom),
                              left=min(self.xaxisZoom))

        # self.axes[0].set_ymin(min(self.yaxisZoom))
        # self.axes[0].set_ymax(max(self.yaxisZoom))

        # self.axes[1].get_shared_y_axes().join(self.axes[0], self.axes[1])
        # the shares axes are being a bugger
        self.axes[1].set_yticklabels([])
        # self.axes[1].set_yticks(self.axes[0].get_yticks())
        cbar = self.fig.colorbar(im0, cax=self.axes[2])
        cbar.set_label(r"CL$_{s}$")

        if self.showcls:
            self.induce_CLs_grid(self.axes[1], self.grid)

        try:
            self.fig.tight_layout(pad=0.32)
            self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
        except Exception as e:
            cfg.contur_log.error("Failed to make combinedHybrid plot. This may be due to the interpolation step. Try a different iLevel?")
            cfg.contur_log.error(e)
            sys.exit()

    def plot_levels(self):
        """
        Make an individual levels plot, currently just used for compatibility to show the individual pools
        Makes the file combinedLevels.pdf
        .. todo:: Derive these from the main hybrid plot
        """

        cfg.contur_log.info("Plotting levels: contours without heatmap")

        
        # make a styled blank canvas
        self.make_canvas()

        # interpolate the meshgrid to make things smoother for a levels plot
        self.interpolate_grid(self.iLevel, self.iSigma)
        self.ax0.contourf(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, cmap=self.cmap,
                          levels=[0.68, 0.95, 10], vmin=0.0, vmax=1.0)  # , alpha=0.6)  # , snap=True)
        self.ax0.contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[self._primary_stat],
                         levels=[0.68, 0.95, 10], vmin=0.0, vmax=1.0)

        path_out = os.path.join(self.destination, self.label + "Levels")
        if self.xLog:
            self.ax0.set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0.set_yscale("log", nonpositive='clip')
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))

        self.ax0.set_ylabel(self.yLabel)
        self.ax0.set_xlabel(self.xLabel)

        self.figs.append(self.fig)
        self.fig.tight_layout(pad=0.1)
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

    def plot_mesh(self, make_cbar):
        """
        Make an individual colormesh plot, currently just used for compatibility to show the individual pools
        .. todo:: Derive these from the main hybrid plot
        Makes the file combinedMesh.pdf
        """

        cfg.contur_log.info("Plotting mesh: heatmap without contours")

        # make a styled blank canvas
        self.make_canvas()
        self.ax0.pcolormesh(self.xAxisMesh, self.yAxisMesh,
                            self.grid.T, cmap=self.cmap, vmin=0, vmax=1, snap=True)

        path_out = os.path.join(self.destination, self.label + "Mesh")
        if self.xLog:
            self.ax0.set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0.set_yscale("log", nonpositive='clip')
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylabel(self.yLabel)
        self.ax0.set_xlabel(self.xLabel)

        if self.showcls:
            self.induce_CLs_grid(self.ax0, self.grid)

        self.figs.append(self.fig)
        self.fig.tight_layout(pad=0.1)
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

            # make (one!) separate fig colorbar
        if make_cbar:
            self.fig_cbar = plt.figure(figsize=self.fig_dims_cbar)  # _cbar)
            self.axcbar = self.fig_cbar.add_subplot(1, 1, 1)
            norm = mpl.colors.Normalize(vmin=0, vmax=1)
            cb1 = mpl.colorbar.ColorbarBase(
                self.axcbar, cmap=self.cmap, norm=norm, orientation="vertical")  # ,orientation="vertical")
            cb1.set_label(r"CL$_{s}$")
            self.fig_cbar.tight_layout(pad=0.1)
            self.fig_cbar.savefig(path_out + "cbar.pdf", format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
                plt.close(self.fig_cbar)

    def plot_mesh_overlay(self, make_cbar=False):
        """
        Make an individual colormesh plot with overlaid limit contours
        Makes the file combinedOverlay.pdf
        """

        cfg.contur_log.info("Plotting combined overlay: heatmap with contours.")

        self.make_canvas()

        # draw the mesh
        self.ax0.pcolormesh(self.xAxisMesh, self.yAxisMesh,
                            self.grid.T, cmap=self.cmap, vmin=0, vmax=1, snap=True)
        if self.xLog:
            self.ax0.set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0.set_yscale("log", nonpositive='clip')
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylabel(self.yLabel)
        self.ax0.set_xlabel(self.xLabel)

        # interpolate the meshgrid to make things smoother for a levels plot
        self.interpolate_grid(self.iLevel, self.iSigma)
        self.ax0.contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[self._primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)



        if self.showcls:
            self.induce_CLs_grid(self.ax0, self.grid)

        # add theory/previous experiment limits WHY DOESNT THIS WORK?
        colorCycle = iter(color_config.CONTURCOLORS())
        self.add_limits(self.ax0,level=self.iLevel,sigma=self.iSigma)

        self.figs.append(self.fig)
        self.fig.tight_layout(pad=0.1)

        path_out = os.path.join(self.destination, self.label + "Overlay")
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

        # make a separate fig colorbar
        if make_cbar:
            self.fig_cbar = plt.figure(figsize=self.fig_dims_cbar)  # _cbar)
            self.axcbar = self.fig_cbar.add_subplot(1, 1, 1)
            norm = mpl.colors.Normalize(vmin=0, vmax=1)
            cb1 = mpl.colorbar.ColorbarBase(
                self.axcbar, cmap=self.cmap, norm=norm, orientation="vertical")  # ,orientation="vertical")
            cb1.set_label(r"CL$_{s}$")
            self.fig_cbar.tight_layout(pad=0.1)
            self.fig_cbar.savefig(path_out + "cbar.pdf", format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
                plt.close(self.fig_cbar)


    def induce_CLs_grid(self, axis, grid, inPercent=False):
        """  show the bin contents as text """
        for i in range(len(self.xAxis)):
            for j in range(len(self.yAxis)):
                z = "%.2f" % grid[i, j]
                if inPercent:
                    z = "%.1f" % grid[i, j]
                axis.text(self.xAxis[i], self.yAxis[j], z, color="w",
                          ha="center", va="center", fontsize="4")

    def prepare_axis(self, axis):
        if self.xLog:
            axis.set_xscale("log", nonpositive='clip')
        if self.yLog:
            axis.set_yscale("log", nonpositive='clip')
        axis.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        axis.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        axis.set_ylabel(self.yLabel)
        axis.set_xlabel(self.xLabel)



    def plot_CLs(self, gridSpecs, grid, title, extend='neither'):
        """ plot a mesh of the grid with CLs values """

        axis = self.fig.add_subplot(gridSpecs[0])
        axisCbar = self.fig.add_subplot(gridSpecs[1])
        axis.set_title(title)

        vmin = 0
        cmap = self.cmap
        if extend == 'min':
            vmin = -1
            newcolors = self.cmap(np.linspace(0, 1, num=255))
            np.insert(newcolors, 0, [0, 0, 0, 1])
            newcolors[0, :] = np.array([0, 0, 0, 1])
            cmap = mpl.colors.ListedColormap(newcolors)

        plot = axis.pcolormesh(self.xAxisMesh, self.yAxisMesh,
                               grid.T, cmap=cmap, vmin=vmin, vmax=100, snap=True)
        self.prepare_axis(axis)

        cbarTotal = self.fig.colorbar(plot, cax=axisCbar, extend=extend)
        cbarTotal.set_label(r"CL$_{s}$")

        if self.showcls:
            self.induce_CLs_grid(axis, grid, inPercent=True)

    def plot_pool_CLs(self, cpb, level):
        """Make a 2D plot of the pools' CLs"""
        diff = 0.07
        widthRatios = [1, 0.04]
        hspace = 0.4
        top = 0.95
        gsL = GridSpec(2, 2, width_ratios=widthRatios,
                       right=0.5-diff, hspace=hspace, top=top)
        gsR = GridSpec(2, 2, width_ratios=widthRatios,
                       left=0.5+diff, hspace=hspace, top=top)
        self.fig = plt.figure(figsize=self.fig_dims_cls)
        axisLeading = self.fig.add_subplot(gsR[2])
        axisLeadingCbar = self.fig.add_subplot(gsR[3])

        # ==================================================================
        # CLs meshs
        # ==================================================================
        # total CLs
        gridTotal = self.grid*100
        self.plot_CLs([gsL[0], gsL[1]], gridTotal, "total CLs")

        # leading CLs
        self.plot_CLs([gsR[0], gsR[1]], cpb.poolCLs[:, :, level],
                     "(sub)$^"+str(level)+"$ leading CLs")

        # diff CLs
        self.plot_CLs([gsL[2], gsL[3]], gridTotal - cpb.poolCLs[:, :, level],
                     "total CLs - (sub)$^"+str(level)+"$ leading CLs", 'min')

        # ==================================================================
        # leading CLs: pool names
        # ==================================================================
        axisLeading.set_title("(sub)$^"+str(level)+"$ leading CLs: pool names")
        # TODO: can we somehow get a more semantically ordered pool list, e.g. using the POOLCOLORS dict order?
        nColors = len(cpb.poolNames[level])
        colorCycle = iter(color_config.CONTURCOLORS())  # < this thing is horrible to use...

        #usetints = (self.style == "FINAL")
        # always use tints for this detailed plot.
        usetints = True
        #plotHighest = axisLeading.pcolormesh(self.xAxisMesh, self.yAxisMesh, cpb.poolIDs[:,:,level].T, snap=True, cmap=plt.get_cmap("tab20", nColors), vmin=0, vmax=nColors)
        poolcmap = plt.matplotlib.colors.ListedColormap(
            [get_pool_color(pool, usetints) for pool in cpb.poolNames[level]])
        plotHighest = axisLeading.pcolormesh(
            self.xAxisMesh, self.yAxisMesh, cpb.poolIDs[:, :, level].T, snap=True, cmap=poolcmap, vmin=0, vmax=nColors)
        self.prepare_axis(axisLeading)

        if self.showcls:
            self.induce_CLs_grid(
                axisLeading, cpb.poolCLs[:, :, level], inPercent=True)

        bounds = np.linspace(0, nColors, num=nColors+1)
        ticks = [x+0.5 for x in bounds[:-1]]
        labels = []
        for pool in cpb.poolNames[level]:
            # have to escape underscores
            labels.append(pool.replace("_", r"\_"))

        cbar = self.fig.colorbar(
            plotHighest, cax=axisLeadingCbar, boundaries=bounds, ticks=ticks)
        cbar.ax.set_yticklabels(labels)
        cbar.ax.tick_params(labelsize=4)

        # ==================================================================
        # clean up
        # ==================================================================
        self.figs.append(self.fig)
        path_out = os.path.join(self.destination, self.label)  # + "PoolCLs")
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

    def plot_pool_names(self, cpb, level):
        """Make a 2D plot of the dominant pool names and their CLs values"""
        self.make_canvas(dims=self.fig_dims_dp)
        path_out = os.path.join(self.destination, self.label)

        # Plot styling
        showtitle = (self.style == "DRAFT")
        showcbar = (self.style == "DRAFT")

        # Painstakingly assemble a nice title
        if showtitle:
            title = "Leading CLs analysis pools"
            if level > 0:
                suffix = "th"
                if level < 3:
                    suffix = "st" if level == 1 else "nd"
                title = "{lev:d}{suff}-subleading-CLs analysis pools".format(
                    lev=level, suff=suffix)
            self.ax0.set_title(title)

        # TODO: can we somehow get a more semantically ordered pool list, e.g. using the POOLCOLORS dict order?
        nColors = len(cpb.poolNames[level])

        usetints = not (self.style == "FINAL")
        # plotHighest = self.ax0.pcolormesh(self.xAxisMesh, self.yAxisMesh, cpb.poolIDs[:,:,level].T, snap=True, cmap=plt.get_cmap("tab20", nColors), vmin=0, vmax=nColors)
        poolcmap = plt.matplotlib.colors.ListedColormap(
            [get_pool_color(pool, usetints) for pool in cpb.poolNames[level]])
        plotHighest = self.ax0.pcolormesh(
            self.xAxisMesh, self.yAxisMesh, cpb.poolIDs[:, :, level].T, snap=True, cmap=poolcmap, vmin=0, vmax=nColors)
        self.prepare_axis(self.ax0)

        self.interpolate_grid(self.iLevel, self.iSigma)
        self.ax0.contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[self._primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)

        # Add theory/previous experiment limits
        colorCycle = iter(color_config.CONTURCOLORS())
        self.add_limits(self.ax0,level=self.iLevel,sigma=self.iSigma)


        if self.showcls:
            self.induce_CLs_grid(self.ax0, self.grid)

        # Colour bar
        bounds = np.linspace(0, nColors, num=nColors+1)
        ticks = [x+0.5 for x in bounds[:-1]]
        labels = []
        for pool in cpb.poolNames[level]:
            # have to escape underscores
            labels.append(pool.replace("_", r"\_"))

        if showcbar:
            # self.fig.savefig(path_out + "nocbar.pdf", format=cfg.plot_format) #< save before adding the cbar
            cbar = self.fig.colorbar(
                plotHighest, boundaries=bounds, ticks=ticks)
            cbar.ax.set_yticklabels(labels)
            
            cbar.ax.tick_params(labelsize=4)

        # Tidy the presentation
        self.figs.append(self.fig)
        self.fig.tight_layout(pad=0.1)

        # Save fig and cbar
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)

        # Clean up
        if not self.saveAxes:
            plt.close(self.fig)

    def make_canvas(self,dims=None):
        """Convenience function for the individual plots"""
        if dims is None:
            dims=self.fig_dims
        self.fig = plt.figure(figsize=dims)
        self.ax0 = self.fig.add_subplot(1,1,1)

    def add_grid(self, numpyGrid, label, dest, axHolder):
        """Main access method to give the plot all the attributes it needs in a numpy format that feeds directly into mpl"""
        self.grid = numpyGrid
        self.label = label
        self.destination = dest
        self.__dict__.update(axHolder.__dict__)

        self.interpolate_grid(self.iLevel)

    def add_external_data_grids(self, external_data_grids):
        """
        Add the alternative data grids, this is a workaround for now
        .. todo:: Revisit the implementation of smoothing using scipy's interpolator here
        """

        self.alt_grids.extend(external_data_grids)


    def interpolate_grid(self, level=3, sigma=0.75):
        """Use scipy's interpolators to create smoothed & zoomed versions of the grids and axes"""
        import scipy.ndimage
        self.gridZoom = scipy.ndimage.zoom(self.grid, level)
        self.gridZoom = scipy.ndimage.gaussian_filter(self.gridZoom, sigma*level)
        self.xaxisZoom = scipy.ndimage.zoom(self.xAxis, level)
        self.yaxisZoom = scipy.ndimage.zoom(self.yAxis, level)

    def load_style_defaults(self):
        """Some core common styling such as figure dimensions, and rcParams"""
        WIDTH = 454.0
        FACTOR = 1.0 / 2.0
        figwidthpt = WIDTH * FACTOR
        inchesperpt = 1.0 / 72.27
        golden_ratio = (np.sqrt(5) - 1.0) / 2.0

        figwidthin = figwidthpt * inchesperpt  # figure width in inches
        figheightin = figwidthin * golden_ratio + 0.6  # figure height in inches
        self.fig_dims = [figwidthin, figheightin]  # fig dims as a list
        self.fig_dims_hybrid = [figwidthin * 1.8, figheightin]
        self.fig_dims_cls = [figwidthin * 3., 2.1*figheightin]
        self.fig_dims_cbar = [figwidthin * 0.2, figheightin]
        if self.style == "DRAFT":
            self.fig_dims_dp = [figwidthin * 1.7, figheightin*1.5]
        else:
            self.fig_dims_dp = self.fig_dims

        document_fontsize = 10
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['Computer Modern Roman']
        rcParams['font.size'] = document_fontsize
        rcParams['axes.titlesize'] = document_fontsize
        rcParams['axes.labelsize'] = document_fontsize
        rcParams['xtick.labelsize'] = document_fontsize
        rcParams['ytick.labelsize'] = document_fontsize
        rcParams['legend.fontsize'] = document_fontsize
        rcParams['text.usetex'] = True
        rcParams['interactive'] = False
        rcParams['axes.prop_cycle'] = color_config.CONTURCOLORS


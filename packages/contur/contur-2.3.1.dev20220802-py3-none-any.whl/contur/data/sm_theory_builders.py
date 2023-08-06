import contur
import yoda
import numpy
import scipy.stats
import os
import contur.config.config as cfg


def do_ATLAS_2016_I1457605(prediction):
    """ 
    Photon+jet NNLO Calculation from arXiv:1904.01044
    Xuan Chen, Thomas Gehrmann, Nigel Glover, Marius Hoefer, Alexander Huss
    """

    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2016_I1457605"
    yoda_name = a_name+".yoda"

    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    splitter = " "
    dataFiles = {a_name+"/d01-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin1_ATLAS.dat",
                 a_name+"/d02-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin2_ATLAS.dat",
                 a_name+"/d03-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin3_ATLAS.dat",
                 a_name+"/d04-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin4_ATLAS.dat"
                 }

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)

    for path, ao in aos.items():
        filename = dataFiles.get(path[5:])
        ao.setPath("/THY/"+path[5:])
        cfg.contur_log.debug("Reading", filename)

        with open(filename, "r+") as f:
            data = f.readlines()  # read the text file
            binNum = 0
            nBins = len(ao.points())
            cfg.contur_log.debug(nBins, " bins")
            for line in data:
                # get a list containing all the entries in a line
                allNums = line.strip().split(splitter)
                # check they're actually numbers
                numberLine = True
                for num in allNums:
                    try:
                        val = float(num)
                    except ValueError:
                        numberLine = False
                        break
                if numberLine:
                    tmplist = [float(allNums[3]), float(allNums[5]), float(allNums[7]), float(
                        allNums[9]), float(allNums[11]), float(allNums[13]), float(allNums[15])]
                    upper = max(tmplist)
                    lower = min(tmplist)
                    uncertainty = (upper - lower)/2000.0
                    mean = (upper + lower)/2000.0
                    if binNum < nBins:
                        point = ao.point(binNum)
                        binNum = binNum + 1
                        point.setY(mean)
                        point.setYErrs(uncertainty, uncertainty)

            ao.setTitle(prediction.short_description)
            #ao.setAnnotation("Title", "NNLO QCD arXiv:1904.01044")
            anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2017_I1645627(prediction):

    anaObjects = []
    indir = cfg.input_dir

    # Photon+jet NNLO Calculation from arXiv:1904.01044
    # Xuan Chen, Thomas Gehrmann, Nigel Glover, Marius Hoefer, Alexander Huss
    a_name = "ATLAS_2017_I1645627"
    splitter = " "
    dataFiles = {a_name+"/d01-x01-y01": indir+"/NNLO-Photons/Fig11/NNLO_pt_NNPDF31_hybIso.Et_gam_ATLAS.dat",
                 a_name+"/d02-x01-y01": indir+"/NNLO-Photons/Fig12/NNLO_pt_NNPDF31_hybIso.ptj1_ATLAS.dat",
                 a_name+"/d03-x01-y01": indir+"/NNLO-Photons/Fig14/NNLO_pt_NNPDF31_hybIso.dphi_gam_j1_ATLAS.dat",
                 a_name+"/d04-x01-y01": indir+"/NNLO-Photons/Fig13/NNLO_pt_NNPDF31_hybIso.m_gam_j1_ATLAS.dat",
                 a_name+"/d05-x01-y01": indir+"/NNLO-Photons/Fig15/NNLO_pt_NNPDF31_hybIso.abs_costhetastar_gam_j1_ATLAS.dat"
                 }

    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():
        filename = dataFiles.get(path[5:])
        ao.setPath("/THY/"+path[5:])
        cfg.contur_log.debug("Reading {}".format(filename))

        with open(filename, "r+") as f:
            data = f.readlines()  # read the text file
            binNum = 0
            nBins = len(ao.points())
            cfg.contur_log.debug("nBins= {}".format(nBins))
            for line in data:
                # get a list containing all the entries in a line
                allNums = line.strip().split(splitter)
            # check they're actually numbers
                numberLine = True
                for num in allNums:
                    try:
                        val = float(num)
                    except ValueError:
                        numberLine = False
                        break
                if numberLine:
                    tmplist = [float(allNums[3]), float(allNums[5]), float(allNums[7]), float(
                        allNums[9]), float(allNums[11]), float(allNums[13]), float(allNums[15])]
                    upper = max(tmplist)
                    lower = min(tmplist)
                    uncertainty = (upper - lower)/2000.0
                    mean = (upper + lower)/2000.0
                    if binNum < nBins:
                        point = ao.point(binNum)
                        binNum = binNum + 1
                        point.setY(mean)
                        point.setYErrs(uncertainty, uncertainty)

        ao.rmAnnotation("ErrorBreakdown")
                        
        #ao.setAnnotation("Title", "NNLO QCD arXiv:1904.01044")
        ao.setTitle(prediction.short_description)
        anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

        
def do_ATLAS_2012_I1199269(prediction):
    """
         ATLAS 7TeV diphotons, 2gamma NNLO prediction read from paper
         S. Catani, L. Cieri, D. de Florian, G. Ferrera, and M. Grazzini,
         Diphoton production at hadron colliders: a fully-differential QCD calculation at NNLO,
         Phys. Rev. Lett. 108 (2012) 072001, [arXiv:1110.2375].
    """

    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2012_I1199269"
    splitter = ", "
    dataFiles = {a_name+"/d01-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5a.txt",
                 a_name+"/d02-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5b.txt",
                 a_name+"/d03-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5c.txt",
                 a_name+"/d04-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5d.txt"
                 }
    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():
        filename = dataFiles.get(path[5:])
        if filename:
            ao.setPath("/THY/"+path[5:])
            cfg.contur_log.debug("Reading {}".format(filename))

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:
                        uncertainty = float(allNums[2])
                        mean = float(allNums[1])
                        if binNum < nBins:
                            point = ao.point(binNum)
                            binNum = binNum + 1
                            point.setY(mean)
                            point.setYErrs(
                                uncertainty, uncertainty)

            ao.setTitle(prediction.short_description)
            #ao.setAnnotation("Title", "1802.02095, Catani et al")
            ao.rmAnnotation("ErrorBreakdown")
            anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2017_I1591327(prediction):
    """
     ATLAS 8TeV diphotons, Matrix prediction prediction read from
     Predictions for the isolated diphoton production through NNLO in QCD and
     comparison to the 8 TeV ATLAS data
     Bouzid Boussaha, Farida Iddir, Lahouari Semlala arXiv:1803.09176
     2gamma from
     S. Catani, L. Cieri, D. de Florian, G. Ferrera, and M. Grazzini,
     Diphoton production at hadron colliders: a fully-differential QCD calculation at NNLO,
     Phys. Rev. Lett. 108 (2012) 072001, [arXiv:1110.2375].
    """
    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2017_I1591327"
    splitter = ", "
    dataFiles = {a_name+"/d02-x01-y01": indir+"/"+a_name+"/Matrix_Mass.txt",
                 a_name+"/d03-x01-y01": indir+"/"+a_name+"/2gammaNNLO_pt.txt"
                 }
    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():
        filename = dataFiles.get(path[5:])
        if filename:
            ao.setPath("/THY/"+path[5:])

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:
                        uncertainty = float(allNums[2])
                        mean = float(allNums[1])
                        if binNum < nBins:
                            point = ao.point(binNum)
                            binNum = binNum + 1
                            point.setY(mean)
                            point.setYErrs(
                                uncertainty, uncertainty)

            if "Matrix" in filename:
                ao.setAnnotation("Title", "1803.09176 (Matrix)")
            else:
                ao.setAnnotation("Title", "2gamma NNLO")

            ao.rmAnnotation("ErrorBreakdown")
            anaObjects.append(ao)

        yoda.write(anaObjects, a_name+"-Theory.yoda")


def do_ATLAS_2016_I1467454(prediction):
        
    indir = cfg.input_dir

    anaObjects_el = []
    anaObjects_mu = []


    # ATLAS 8TeV HMDY mass distribution
    # Predictions from the paper, taken from the ll theory ratio plot (Born) but applied
    # to the dressed level ee & mm data as mult. factors.
    a_name_mu  = "ATLAS_2016_I1467454:LMODE=MU"
    a_name_el  = "ATLAS_2016_I1467454:LMODE=EL"
    short_name = "ATLAS_2016_I1467454"

    splitter = ", "
    dataFiles = {"d18-x01-y01": indir+"/"+short_name+"/dy1.txt",
                 "d29-x01-y01": indir+"/"+short_name+"/dy1.txt",
                 }
    analysis_mu = contur.data.get_analyses(analysisid=a_name_mu,filter=False)[0]
    analysis_el = contur.data.get_analyses(analysisid=a_name_el,filter=False)[0]

    # This finds the REF file, which is common to _mu and _el versions.
    yodaf = contur.util.utils.find_ref_file(analysis=analysis_mu)

    for histo, filename in dataFiles.items():

        aos = yoda.read(yodaf, patterns=histo)
        ao = next(iter(aos.values()))  

        mu = ("d29" in histo)
        el = ("d18" in histo)
                
        if mu:
            ao.setPath("/THY/{}/{}".format(a_name_mu,histo))
        elif el:
            ao.setPath("/THY/{}/{}".format(a_name_el,histo))
                       
        with open(filename, "r+") as f:
            data = f.readlines()  # read the text file
            binNum = 0
            nBins = len(ao.points())
            for line in data:
                # get a list containing all the entries in a line
                allNums = line.strip().split(splitter)
                # check they're actually numbers
                numberLine = True
                for num in allNums:
                    try:
                        val = float(num)
                    except ValueError:
                        numberLine = False
                        break
                if numberLine:
                    uncertainty = float(allNums[2])
                    mean = float(allNums[1])
                    if binNum < nBins:
                        point = ao.point(binNum)
                        uncertainty = uncertainty*point.y()
                        point.setYErrs(
                            uncertainty, uncertainty)
                        point.setY(point.y()*mean)
                        binNum = binNum + 1

        ao.setTitle(prediction.short_description)

        if el:
            anaObjects_el.append(ao)
        elif mu:
            anaObjects_mu.append(ao)

    yoda.write(anaObjects_el, analysis_el.name+"-Theory.yoda")
    yoda.write(anaObjects_mu, analysis_mu.name+"-Theory.yoda")


def do_CMS_2017_I1467451(prediction):
    """
    CMS 8TeV H->WW pT distribution
     Predictions from the paper
    """
    
    indir = cfg.input_dir
    anaObjects = []

    a_name = "CMS_2017_I1467451"
    splitter = ", "
    dataFiles = {a_name+"/d01-x01-y01": indir +
                 "/"+a_name+"/hpt.txt"}
    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():
        filename = dataFiles.get(path[5:])
        if filename:
            ao.setPath("/THY/"+path[5:])

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:
                        uncertainty = float(allNums[2])
                        mean = float(allNums[1])
                        if binNum < nBins:
                            point = ao.point(binNum)
                            point.setYErrs(
                                uncertainty, uncertainty)
                            point.setY(mean)
                            binNum = binNum + 1

            ao.setTitle(prediction.short_description)

            anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2015_I1408516(prediction):
    """
    ATLAS 8TeV Drell-Yan phi* and pT distributions
    Predictions from Bizon et al arXiv:1805.05916
    """
        
    indir = cfg.input_dir

    anaObjects_el = []
    anaObjects_mu = []

    a_name_mu = "ATLAS_2015_I1408516:LMODE=MU"
    a_name_el = "ATLAS_2015_I1408516:LMODE=EL"
    short_name = "ATLAS_2015_I1408516"

    analysis_mu = contur.data.get_analyses(analysisid=a_name_mu,filter=False)[0]
    analysis_el = contur.data.get_analyses(analysisid=a_name_el,filter=False)[0]

    splitter = " "
    dataFiles = {"d02-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_0.8.dat",
                 "d03-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.8_1.6.dat",
                 "d04-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_1.6_2.4.dat",
                 "d05-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d06-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d07-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d08-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d09-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d10-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d11-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_0.8.dat",
                 "d12-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.8_1.6.dat",
                 "d13-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_1.6_2.4.dat",
                 "d14-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d15-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d16-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_2.4.dat",
                 "d17-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d18-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d19-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d20-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d21-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d22-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d26-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d27-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d28-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_116_150_0.0_2.4.dat",
                 
                 "d02-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_0.8.dat",
                 "d03-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.8_1.6.dat",
                 "d04-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_1.6_2.4.dat",
                 "d05-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d06-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d07-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d08-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d09-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d10-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d11-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_0.8.dat",
                 "d12-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.8_1.6.dat",
                 "d13-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_1.6_2.4.dat",
                 "d14-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d15-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d16-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_2.4.dat",
                 "d17-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d18-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d19-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d20-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d21-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d22-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d26-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d27-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d28-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_116_150_0.0_2.4.dat"
                 }

    # This finds the REF file, which is common to _mu and _el versions.
    f = contur.util.utils.find_ref_file(analysis=analysis_mu)
    aos = yoda.read(f)
    for path, ao in aos.items():
        el = False
        mu = False
        filename = dataFiles.get(ao.name())
        if filename:

            el = ("y01" in path)
            mu = ("y04" in path)
           
            if mu:
                ao.setPath("/THY/{}/{}".format(a_name_mu,ao.name()))
            elif el:
                ao.setPath("/THY/{}/{}".format(a_name_el,ao.name()))
                           
            cfg.contur_log.debug("Reading {}".format(filename))

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                # now we want to get the born-to-dressed corrections
                if "y01" in path:
                    # this is an electron plot
                    dpath = path[:len(path)-1]+"2"
                    dplot = aos[dpath]
                elif "y04" in path:
                    # this is a muon plot
                    dpath = path[:len(path)-1]+"5"
                    dplot = aos[dpath]

                bornpath = path[:len(path)-1]+"6"
                bornplot = aos[bornpath]

                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:

                        uncertainty = numpy.abs(
                            (float(allNums[2])-float(allNums[3]))/2.0)
                        mean = float(allNums[1])
                        if binNum < nBins:
                            corr = dplot.point(binNum).y(
                            )/bornplot.point(binNum).y()
                            point = ao.point(binNum)
                            point.setYErrs(
                                uncertainty*corr, uncertainty*corr)
                            point.setY(mean*corr)
                            binNum = binNum + 1

        ao.setTitle(prediction.short_description)

        ao.rmAnnotation("ErrorBreakdown")

        if el:
            anaObjects_el.append(ao)
        elif mu:
            anaObjects_mu.append(ao)

    yoda.write(anaObjects_el, analysis_el.name+"-Theory.yoda")
    yoda.write(anaObjects_mu, analysis_mu.name+"-Theory.yoda")



def do_ATLAS_2019_I1725190(prediction):
    """
    ATLAS 13 TeV DY Run 2 search
    Fit to SM from the paper.
    """
    anaObjects = []

    a_name = "ATLAS_2019_I1725190"
    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    def atlas_fit(mass,muon):

        # return the result of the ATLAS fit to dilepton mass, 13 TeV
        # electron if not muon

        rootS = 13000.0
        mZ = 91.1876
        gammaZ = 2.4952

        x = mass/rootS

        if muon:
            # dimuon channel:
            c = 1.0/3.0
            b = 11.8
            p0 = -7.38
            p1 = -4.132
            p2 = -1.0637
            p3 = -0.1022
        else:
            # electron
            c = 1.0
            b = 1.5
            p0 = -12.38
            p1 = -4.295
            p2 = -0.9191
            p3 = -0.0845

        val = scipy.stats.cauchy.pdf(mass, mZ, gammaZ) * numpy.power((1-numpy.power(x,c)),b) * numpy.power(x, p0 + p1*numpy.log(x) + p2*numpy.log(x)**2 + p3*numpy.log(x)**3)
        return val


    a_muon = 138700
    a_elec = 178000

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():

        if "d01-x01-y01" in path:
            muon = False
            norm = 178000.0
        elif "d02-x01-y01" in path:
            muon = True
            norm = 138700.0
        else:
            continue

        ao.setPath("/THY/"+path[5:])
        sum_n = 0
        for point in ao.points():
            mass = point.x()
            point.setY(atlas_fit(mass,muon))
            bw=point.xErrs()[0]*2.0
            sum_n+=point.y()*bw


        norm = 10.*norm/sum_n
        # now another loop to set the normalisation.
        for point in ao.points():
            point.setY(point.y()*norm)
            bw=point.xErrs()[0]*2.0
            # uncertainty set to root of the number of events, then scaled to error on events per ten GeV ie sqrt(n=y*10)/10
            num_events = point.y()*bw/10.0
            uncertainty = 10.0*numpy.sqrt(num_events)/bw
            point.setYErrs(uncertainty,uncertainty)



        ao.setAnnotation("Title", "fit to data")
        anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")
    
def do_ATLAS_2021_I1852328(prediction):
    """
    ATLAS 13 TeV WW+jet
    the prediction is for the b-veto, so we need to scale it for the difference (taken from the difference in the data)
    y05 multiplied by the ratio y02/y01
    """

    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2021_I1852328"
    yoda_name = a_name+".yoda"

    analysis = contur.data.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)

    for path, ao in aos.items():
        
        if "y05" in path:
            aob = aos[path[:-1]+"2"]
            aoi = aos[path[:-1]+"1"]
            for points in zip(ao.points(),aob.points(),aoi.points()):
                points[0].setY(points[0].y()*points[1].y()/points[2].y())

            ao.setTitle(prediction.short_description)
            ao.setPath(ao.path()[:-1]+"2")
            ao.setPath("/THY/"+ao.path()[5:])
            anaObjects.append(ao)


    yoda.write(anaObjects, a_name+"-Theory.yoda")
    

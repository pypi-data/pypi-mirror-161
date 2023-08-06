
import contur
from contur.run.arg_utils import setup_common, valid_beam_arg
from contur.util.utils import hack_journal, mkoutdir, get_inspire
import contur.config.config as cfg
import contur.data as cdb
import rivet
import os
import subprocess

def main(args):
    """
    Main programme to build the bibliography for the web pages.
    args should be a dictionary
    """

    # Set up / respond to the common argument flags and logger config
#    cfg.setup_logger(filename=args['LOG'])
    setup_common(args) 
    print("Writing log to {}".format(cfg.logfile_name))

    if args["OUTPUTDIR"] is not None:
        web_dir = args["OUTPUTDIR"]
        mkoutdir(web_dir)
    else:
        web_dir = os.getenv('CONTUR_WEBDIR')
        if web_dir == None:
            web_dir = ""

    cfg.contur_log.info("Writing bibliography to {}".format(web_dir))
        
    # get the analyses. Unless --all is set, the default filters will be applied for analysis types.
    if  args["USEALL"]:
        anas = cdb.static_db.get_analyses(filter=False)
    else:
        anas = []
        beams = valid_beam_arg(args)
        for beam in beams:
            anas.extend(cdb.static_db.get_analyses(beam=beam))
            
    found_keys=[]
    found_texs=[]
    missing_either=[]
    th_info = []
        
    cite_file = "contur-bib-cite.tex"
    bib_file = os.path.join(web_dir,"contur-anas.bib")
    missing_file = "contur-bib-missing.txt"

    for a in anas:
        sm_theory=a.sm()
        cfg.contur_log.info("Updating bibtex info for {}".format(a.name))
        print(a.bibkey())
        try:
            if not a.bibkey() in found_keys:
                found_keys.append(a.bibkey())
                found_texs.append(a.bibtex())
        except:
            missing_either.append(a.name)

        if sm_theory:
            for sm in sm_theory:
                for inspid in sm.inspids.split(','):
                    try:
                        pub_info=get_inspire(inspid)
                    except cfg.ConturError as e:
                        cfg.contur_log.warning("Could not find bibtex key for inspire ID {} in {}: {}".format(insp_id,ana.name,e))
                    if (pub_info is not None) and not (pub_info['bibtex'] in th_info) and not (str(inspid) in a.name):
                        th_info.append((hack_journal(pub_info['bibtex'])))

    print(found_keys)
    keystr=b'\cite{'
    for s in set(found_keys):
        keystr+=s.encode('utf8', errors='backslashreplace')+b","
    keystr=keystr[:-1]+b'}'

    texstr=b''
    for t in set(found_texs):
        texstr+=t+b"\n"
    for t in set(th_info):
        texstr+=t+b"\n"

    with open(cite_file,"wb") as f:
        f.write(keystr)
    with open(bib_file,"wb") as f:
        f.write(texstr)
    with open(missing_file, "w") as f:
        f.write(str(missing_either))

    cfg.contur_log.info("Wrote {} for cite command, \n{} for bibtex entries,\nand {} for RivetIDs that could not be matched".format(cite_file,bib_file,missing_file))


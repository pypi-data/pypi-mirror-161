import contur.data.static_db as cdb
import os

def plot_render_html(file,obsname,analysis,vis=False,size="300"):
    '''
    Constructs an html snippet linking a rivet/contur plot. Writes in to the open file

    arguments:
    :param file: an opened file to write to
    :param obsname: the name of the histogram (last part of the yoda path)
    :param analysis: the analysis the histogram belongs to.
    :type analysis: :class:`contur.data.Observable`
    
    '''

    pngfile = obsname + ".png"
    vecfile = obsname + ".pdf"
    srcfile = obsname + ".dat"
    try:
        hname = obsname.split("/")[2]
    except:
        hname = obsname
        
    if vis:
        file.write('    <a href="{{  url_for(\'static\', filename=\'point/%s-%s\')  }}">&#9875;</a><a href="{{  url_for(\'static\', filename=\'point/%s\')  }}">&#8984</a> %s:<br/>\n' %
                    (analysis.poolid+"/"+analysis.name, obsname, srcfile, os.path.splitext(vecfile)[0]))
        file.write('    <a name="%s-%s"><a href="{{  url_for(\'static\', filename=\'point/%s\')  }}">\n' % (analysis.poolid+"/"+analysis.name, obsname, vecfile))
        file.write('      <img src="{{  url_for(\'static\', filename=\'point/%s\')  }}">\n' % pngfile)
    else:

        # anchor link to dat file
        file.write('<a href="{}">{}</a><br/>\n'.format(srcfile,hname))
        # img link to PDF.
        file.write('<a href="{}"> <img width="{}" src="{}"></a>\n'.format(vecfile,size,pngfile))

            
def write_summary(index, summary, vis, patterns, unpatterns):
    """
    Write the summary of the contur run, including the most significant plots, to the index file
    Return list of the plots contributing to the exclusion.
    """

    reduced_list_of_plots = []
    index.write("<div style=\"border:1px solid black; background-color:beige;\">\n")

    heading = True
    while heading == True:
        text = summary.readline()
        if "pools" in text:
            heading = False
            continue
        
        if "Run Information" in text:
            index.write("<h2>Information about this Contur run</h2>\n")
        elif "Contur is running" in text:
            words = text.split(" ")
            index.write("<p>\n")
            index.write("Contur ran in {} ".format(words[4]))
        elif "Sampled at" in text:
            index.write("<h4>The model parameters were:</h4>")
        else:
            index.write("{}\n </br>\n".format(text))
            

    index.write("</div>\n")
    
    index.write("<h2>In each analysis pool, these plots contributed:</h2>\n")

    cl = None
    current_stat=None
    current_pool=None
    index.write("<div>")
    for line in summary:
        # ignore blank/space only lines
        if len(line.rstrip())==0:
            continue
        if line[:5]=="Pool:":
            index.write("</div>\n<br>\n")
            current_pool = cdb.get_pool(poolid=line[5:].rstrip("\n"))            
            index.write('<div class="pool">\n')
            index.write("<h3>Pool {}: {}</h3>\n".format(current_pool.id, current_pool.description))
        elif line[0]!="/":
            # This is a line identifying the statistics type and CLs.
            index.write('<div class="stattype">\n')

            if line[:2]=="No":
                if "SMBG" in line:
                    index.write("<h4>{}</h4>".format("No exclusion evaluated using SM as background."))
                elif "EXP" in line:
                    index.write("<h4>{}</h4>".format("No expected exclusion evaluated."))
                    
                index.write('</div>\n')

            else:
                parts = line.split("=")
                # this is the cl for this pool
                cl = float(parts[1])
                current_stat = "Unknown type of exclusion"
                if "DATABG" in parts[0]:
                    current_stat="Exclusion with data as background" 
                elif "SMBG" in parts[0]:
                    current_stat="Exclusion with SM as background" 
                elif "EXP" in parts[0]:
                    current_stat="Expected exclusion" 
                    
                index.write("<h4>{} from this pool: {:5.2f}% </h4>\n".format(current_stat,100*cl))
        else:
            # This is a line identifying histograms
            first=True
            names = line.split(",")
            if len(names)>1:
                index.write("Subpool with {} histograms.<br>\n".format(len(names)))
                size = "150"
            else:
                size = "300"

            for name in names:
                parts=name.split("/")
                obsname = current_pool.id + name.rstrip()
                datname = name.rstrip() + ".dat"
                if not datname in reduced_list_of_plots:
                    reduced_list_of_plots += [datname]
                analysis = cdb.get_analyses(analysisid=str(parts[1]),poolid=current_pool.id,filter=False)[0]
                if first:
                    inspireurl = "http://inspirehep.net/literature/{}".format(analysis.inspireId)
                    index.write("Most sensitive analysis is <a href=\"{}\">{}</a> <br/>\n".format(inspireurl, analysis.name))
                if analysis.name in unpatterns or (patterns and analysis.name not in patterns):
                    if first:
                        index.write("<div>Plot(s) not rendered</div>\n") 
                else:
                    index.write('<div class="plot">\n')
                    plot_render_html(index,obsname,analysis,vis,size=size)
                    index.write('</div>\n')

                first=False

            # close for this stattype
            index.write('</div>\n')

    summary.close()
    index.write('</div>\n')

    return reduced_list_of_plots


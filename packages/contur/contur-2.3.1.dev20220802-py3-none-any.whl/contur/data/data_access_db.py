import sqlite3 as db
import contur
import contur.config.config as cfg
import contur.scan.grid_tools as cgt
import os
import re

INIT_MDB  = False
INIT_DADB = False
GENERATE_MODEL_DATA = False
EXCLUSION_THRESHOLD = 0.2


def init_mdb():
    """
    Initialise the model database
    """
    
    try:
        conn = db.connect(cfg.models_dbfile)
    except db.OperationalError:
        cfg.contur_log.error("Failed to open result DB file: {}".format(cfg.models_dbfile))
        raise
                
    c = conn.cursor()

    _create_model_and_parameter_tables(c)
        
    conn.commit()
    conn.close()

    global INIT_MBD
    INIT_MDB = True

    return

    
def init_dadb():
    """
    initialise the local results database
    """
    try:
        conn = db.connect(cfg.results_dbfile)
    except db.OperationalError:
        cfg.contur_log.error("Failed to open result DB file: {}".format(cfg.results_dbfile))
        raise
        
        
    c = conn.cursor()

    _create_model_and_parameter_tables(c)
    
    c.execute('''create table if not exists model_point
                   (id integer primary key AUTOINCREMENT,
                   model_id  integer     not null,
                   yoda_files text,
                   foreign key(model_id) references model(id) on delete cascade on update cascade);''')

    # parameter_value with the same model_point_id is in the same parameter_point
    c.execute('''create table if not exists parameter_value
                   (id integer primary key AUTOINCREMENT,
                   model_point_id  integer     not null,
                   parameter_id  integer,
                   name varchar(255) not null,
                   value  double    not null,
                   foreign key(model_point_id) references model_point(id) on delete cascade on update cascade,
                   foreign key(parameter_id) references parameter(id) on delete cascade on update cascade);''')

    # run contur command multiple times, then we'll have multiple map data
    c.execute('''create table if not exists map
                    (id integer primary key AUTOINCREMENT,
                    name varchar(255));''')

    # different run with different model_point will produce different exclusion results
    c.execute('''create table if not exists run
               (id integer primary key AUTOINCREMENT,
               map_id integer     not null,
               model_point_id  integer  not null,
               events_num   integer  not null,
               combined_exclusion double not null,
               foreign key(model_point_id) references model_point(id) on delete cascade on update cascade,
               foreign key(map_id) references map(id) on delete cascade on update cascade);''')

    c.execute('''create table if not exists exclusions
                   (id integer primary key AUTOINCREMENT,
                   run_id  integer     not null,
                   pool_name  varchar(255)   not null,
                   exclusion  double not null,
                   histos  text not null,
                   foreign key(run_id) references run(id) on delete cascade on update cascade);''')

    conn.commit()
    conn.close()

    global INIT_DABD
    INIT_DADB = True

def generate_model_and_parameter(model_db=False):
    """
    Create the model and parameter tables and populate them

    if model_db is True, they are written to the central model database, otherwise they are written to the local 
    results db (and the other tables will also be created, empty)

    """
    if model_db:
        if not INIT_MDB:
            init_mdb()
        conn = db.connect(cfg.models_dbfile)
    else:
        if not INIT_DADB:
            init_dadb()
        conn = db.connect(cfg.results_dbfile)

    c = conn.cursor()

    default_contur_url = "https://gitlab.com/hepcedar/contur/-/tree/master/data/Models"
    default_version = "0"

    croot = os.getenv("CONTUR_USER_DIR")

    models_path = os.path.join(croot, "data", "Models")
    if models_path is None:
        raise Exception("CONTUR_USER_DIR not defined")

    for root, dirs, files in sorted(os.walk(models_path)):
        # reach the bottom most directory
        if len(dirs) == 0:
            model_dir_name = os.path.basename(root)
            location = root[re.search("Models", root).end():]

            exist_log_file = False
            exist_source_file = False

            # first search for source.txt files
            for file in files:
                if file == "source.txt":
                    exist_source_file = True
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        name = re.findall(r"name=(.*)\n", content)[0]
                        if name != model_dir_name:
                            cfg.contur_log.warning(
                                "Model name in the source.txt should be the same as the model's directory name!")
                        version = re.findall(r"version=(.*)\n", content)[0] if re.findall(r"version=(.*)\n",
                                                                                          content) else "0"
                        url = re.findall(r"url=(.*)\n", content)[0] if re.findall(r"url=(.*)\n", content) else None
                        contur_url = re.findall(r"contur_url=(.*)\n", content)[0] if re.findall(r"contur_url=(.*)\n",
                                                                                                content) else None
                        author = re.findall(r"author=(.*)\n", content)[0] if re.findall(r"author=(.*)\n",
                                                                                        content) else None
                        reference = re.findall(r"reference=(.*)\n", content)[0] if re.findall(r"reference=(.*)\n",
                                                                                              content) else None
                        if contur_url is not None:
                            contur_web_url = contur_url[:re.search("/data/Models", contur_url).end()]
                            location = contur_url[re.search("/data/Models", contur_url).end():]

                    c.execute("insert into  model (id,name,version,author,original_source,contur_url,location,reference) \
                                              values (?,?,?,?,?,?,?,?);",
                              (None, name, version, author, url, contur_web_url, location, reference))
                    break

            # source.txt file not exists, search for log file
            if not exist_source_file:
                for file in files:
                    # store model data if log file exists
                    if file.endswith(".log") and model_dir_name in file:
                        exist_log_file = True
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            version = re.findall(r"\d+\.(?:\d+\.)*\d+", content)[0]
                        c.execute("insert into  model (id,name,version,contur_url,location) \
                          values (?,?,?,?,?);", (None, model_dir_name, version, default_contur_url, location))
                        break

            if not exist_log_file and not exist_source_file:
                c.execute("insert into  model (id,name,version,contur_url,location) \
                    values (?,?,?,?,?);", (None, model_dir_name, default_version, default_contur_url, location))

            model_id = c.execute("select id from model order by id desc").fetchone()[0]

            # after store model data, search for parameter data
            for file in files:
                # store parameter data
                if file == "parameters.py":
                    with open(os.path.join(root, file), 'r') as f:
                        parameters = f.read().split("Parameter")[2:]
                        for parameter in parameters:
                            parameter_name = re.findall(r"name = \'(\w+)*\'", parameter)[0]
                            parameter_type = re.findall(r"type = \'(\w+)*\'", parameter)[0]
                            parameter_value = re.findall(r"value = \'?([^\',]+)\'?", parameter)[0]
                            parameter_texname = re.findall(r"texname = \'?([^\']+)\'?", parameter)[0]

                            c.execute("insert into  parameter (id,model_id,name,texname,type,value) \
                                values (?,?,?,?,?,?);", (
                                None, model_id, parameter_name, parameter_texname, parameter_type, parameter_value))
    conn.commit()
    conn.close()

    global GENERATE_MODEL_DATA
    GENERATE_MODEL_DATA = True


def get_model_version(dir):
    """
    for a model somewhere in the tree below dir, get its version
    """
    exist_log_file = False
    exist_source_file = False
    for root, _, files in sorted(os.walk(dir, topdown=False)):
        for file in files:
            if file == "source.txt":
                exist_source_file = True
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    version = re.findall(r"version=(.*)\n", content)[0]

        if not exist_source_file:
            for file in files:
                if file.endswith(".log") and os.path.basename(dir) in file:
                    exist_log_file = True
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        version = re.findall(r"\d+\.(?:\d+\.)*\d+", content)[0]
        if not exist_source_file and not exist_log_file:
            version = "0"
    return version


def get_model_id(run_info_path):
    """
    check the model database to see if the model in run_info_path is present.
    if so, return its id (-1 if not found).
    """
    conn = db.connect(cfg.models_dbfile)
    c = conn.cursor()

    model_id = -1
    for root, dirs, _ in sorted(os.walk(run_info_path)):
        for dir in dirs:
            # search for model's name and version
            version = get_model_version(os.path.join(root,dir))
            res = c.execute("select id from  model where name = ? and version = ?;", (dir, version)).fetchone()

            if res is None:
                continue
            else:
                model_id = res[0]
                cfg.contur_log.info("Found matching mode with ID {}".format(model_id))
                break
    if model_id == -1:
        cfg.contur_log.warning("No matching model found for the model in {}".format(run_info_path))
        cfg.contur_log.warning("If you want this to be added, copy the sources files into the contur Models area.")

    # do we want to write this model and parameters to the local db too? probs not.
    conn.close()
    return model_id


def write_grid_data(runname, conturDepot):
    """
    populate the local database with information about this run.

    """

    # @TODO store all the stat types.
    stat_type = cfg.databg

    
    # see if this model is in the DB already 
    run_info_path = os.path.join(os.path.abspath("."), cfg.run_info)
    try:
        model_id = get_model_id(run_info_path)
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)
        
    if conturDepot.inbox is None:
        return False

    # now open the local results file for writing.
    if not INIT_DADB:
        init_dadb()
    conn = db.connect(cfg.results_dbfile)
    c = conn.cursor()
       
    c.execute("insert into  map (id,name) \
         values (?,?);", (None, runname))

    # each run will have the same map id and the same events_num
    map_id = c.execute("select id from map order by id desc;").fetchone()[0]

    events_num = 0
    batch_log_file_path = "contur_batch.log"

    if os.path.exists(batch_log_file_path):
        batch_log_file = open(batch_log_file_path, 'r')
        events_log = batch_log_file.read().strip().split('\n')[0]
        try:            
            events_num = re.match(r'.*events: (\d*)\Z', events_log).group(1)
        except AttributeError:
            events_num = cfg.default_nev
            cfg.contur_log.warning("Could not find event number in {}. Assuming default {}.".format(batch_log_file_path,events_num))
    else:
        events_num = cfg.default_nev
        cfg.contur_log.warning("Could not find {}. Assuming default number of events {}.".format(batch_log_file_path,events_num))

            
    for param_yoda_point in conturDepot.inbox:
        # write information for parameter points
        if param_yoda_point.yoda_factory.get_full_likelihood(stat_type).getCLs() is not None:
            # match parameter point with yoda files TODO I suspect we can do this more efficiently
            # by using info from the map file?
            fileList = [os.path.abspath(cfg.grid)]
            yodaFiles = cgt.find_param_point(fileList, cfg.tag, param_yoda_point.param_point)

            # generate model_point data
            c.execute("insert into model_point (id, model_id, yoda_files) \
                     values (?,?,?);", (None, model_id, str(yodaFiles)))
            model_point_id = c.execute("select id from model_point order by id desc").fetchone()[0]

            for param, val in param_yoda_point.param_point.items():
                res = c.execute("select id from parameter where model_id = ? and name = ?;",
                                (str(model_id), param,)).fetchone()

                # this parameter is not original from contur model
                if res is None:
                    c.execute("insert into parameter_value (id,model_point_id,name,value)\
                                              values (?,?,?,?);", (None, model_point_id, param, val))
                else:
                    parameter_id = res[0]
                    c.execute("insert into parameter_value (id,model_point_id,parameter_id,name,value)\
                          values (?,?,?,?,?);", (None, model_point_id, parameter_id, param, val))

            c.execute("insert into run (id,map_id,model_point_id,events_num,combined_exclusion) \
                 values (?,?,?,?,? )",
                      (None, map_id, model_point_id, events_num, param_yoda_point.yoda_factory.get_full_likelihood(stat_type).getCLs()))

            run_id = c.execute("select id from run order by id desc;").fetchone()[0]

            for x in param_yoda_point.yoda_factory.get_sorted_likelihood_blocks(stat_type):
                c.execute("insert into exclusions (id,run_id,pool_name,exclusion,histos) \
                         values (?,?,?,?,?);", (None, run_id, x.pools, x.getCLs(stat_type), x.tags))

    conn.commit()
    conn.close()
    cfg.contur_log.info("Writing summary for grid mode into database: {}".format(cfg.results_dbfile))


def find_model_point_by_params(paramList):
    params = {}
    model_points = {}

    # parse the parameter list
    # turn the values into floats if possible
    for pair in paramList:
        temp = pair.split('=')
        try:
            params[temp[0]] = float(temp[1])
        except ValueError:
            params[temp[0]] = temp[1]
        model_points[temp[0]] = []

    cfg.contur_log.info('Looking for the closest match to these parameter values: {}'.format(params))

    try:
        conn = db.connect(cfg.results_dbfile)
        c = conn.cursor()
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)
   
    for param, val in params.items():
 
        search_sql = "select min(value) from parameter_value where value >= {} and name=\'{}\';".format(val,param)
        near_val = c.execute(search_sql).fetchone()[0]
        if near_val is None:
            raise db.OperationalError("No values found in DB for parameter {}".format(param))
        
        search_sql = "select model_point_id from parameter_value where name = \'{}\' and value ={}".format(param,near_val)
        model_ids = c.execute(search_sql).fetchall()

        # TODO: this might not actually be closest, since we only look from below.
        
        for model_id in model_ids:
            model_points[param].append(model_id[0])

    # now look for a model point which is in the "closest" list for all parameters
    new_model_points = []

    iterP = next(iter(params))
    for model_point in model_points[iterP]:
        inAll = True
        for points in model_points.values():
            if model_point not in points:
                inAll = False

        if inAll:
            new_model_points.append(model_point)

    return new_model_points

def search_yoda_file(model_points):
    conn = db.connect(cfg.results_dbfile)
    c = conn.cursor()

    search_yoda_sql = "select yoda_files from model_point where id in (" + ','.join(map(str, model_points)) + ");"
    yoda_file_res = c.execute(search_yoda_sql).fetchall()
    yoda_file_list = []
    for yoda_file_str in yoda_file_res:
        yoda_files=yoda_file_str[0].split(",")
        for file in yoda_files:
            yoda_file_list.append(file.strip("[").strip("]").replace("'","").strip())

    conn.commit()
    conn.close()
    return yoda_file_list

def find_param_point_db(fileList, paramList):
    if len(paramList) == 0:
        return fileList

    try:
        model_points = find_model_point_by_params(paramList)
        yoda_files = search_yoda_file(model_points)
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)
        
    cfg.contur_log.info('These files have been identified as the nearest match: {}'.format(yoda_files))

    return yoda_files


def show_param_detail_db(fileList, paramList):
    if len(paramList) == 0:
        return fileList

    try:
        conn = db.connect(cfg.results_dbfile)
        c = conn.cursor()
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)

    model_points = find_model_point_by_params(paramList)
    yoda_files = search_yoda_file(model_points)

    for model_point_id in model_points:
        search_sql = "select name,value from parameter_value where model_point_id = " + str(model_point_id) + ";"
        res = c.execute(search_sql).fetchall()
        cfg.contur_log.info("********************************")
        cfg.contur_log.info("Parameters for this run are:")
        for params in res:
            cfg.contur_log.info("{}: {}".format(params[0], params[1]))

        search_sql = "select yoda_files from model_point where id =" + str(model_point_id) + ";"
        yoda_file = c.execute(search_sql).fetchone()[0]
        cfg.contur_log.info("Files identified as the nearest match: {}".format(yoda_file))

        search_sql = "select id,events_num,combined_exclusion from run where model_point_id = " + str(
            model_point_id) + ";"
        run_res = c.execute(search_sql).fetchone()
        run_id = run_res[0]
        events_num = run_res[1]
        combined_exclusion = run_res[2]
        cfg.contur_log.info(
            "Combined exclusion and number of events: {}, {}".format(combined_exclusion, events_num))

        cfg.contur_log.info("Histograms contributed to the combined exclusion (exclusion>0.5):")
        search_sql = "select pool_name,exclusion,histos from exclusions where run_id = " + str(
            run_id) + " and exclusion > " + str(EXCLUSION_THRESHOLD) + ";"
        exclusion_res = c.execute(search_sql).fetchall()
        for exclusion in exclusion_res:
            cfg.contur_log.info(
                "pool:{}, exclusion:{}, histograms:{}".format(exclusion[0], exclusion[1], exclusion[2]))

    return yoda_files



def _create_model_and_parameter_tables(c):
    """
    Make the model table and the parameter table on connection c.
    """

    c.execute('''create table if not exists model
                   (id integer primary key AUTOINCREMENT,
                   name  varchar(255)    not null,
                   version  varchar(255)   not null,
                   author  varchar(255),
                   original_source   varchar(255),
                   contur_url  varchar(255),
                   location  varchar(255),
                   reference  varchar(255));''')

    # TODO: Comment it out temporarily to avoid exceptions
    # c.execute('''create unique index if not exists model_version on model (name, version);''')

    c.execute('''create table if not exists parameter
                   (id integer primary key AUTOINCREMENT,
                   model_id  integer     not null,
                   name  varchar(255)    not null,
                   texname varchar(255)    not null,
                   type  varchar(50)    not null,
                   value  varchar(50)    not null,
                   foreign key(model_id) references model(id) on delete cascade on update cascade);''')

    return


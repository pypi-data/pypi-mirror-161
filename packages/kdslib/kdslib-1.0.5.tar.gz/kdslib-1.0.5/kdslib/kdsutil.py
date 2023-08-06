# module level doc-string
__doc__ = """
General logging utility module for KDS

@author: Manoj Bonam
Created on Thu Mar 11 14:57:55 2021

DEBUG: Detailed information, typically of interest only when diagnosing problems.
INFO: Confirmation that things are working as expected.
WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
ERROR: Due to a more serious problem, the software has not been able to perform some function.
CRITICAL: A serious error, indicating that the program itself may be unable to continue running.

################################################# INSTRUCTIONS #########################################################
# In your program always import the entire kdsutil module first, to properly set the local variables.                  #
# from kdslib import kdsutil                                                                                           #
# The main class can be instantiated like this: loggingutil = kdsutil.Generate_Logger(**kwargs)                        #
# The class variables can be accessed in this format: loggingutil.logger.info('Hello World')                           #
# The class methods can be accessed in this format: loggingutil.log_info('Hello World')                                #
########################################################################################################################

Library: https://docs.python.org/3/library/logging.html

"""

import os, logging, yaml, sys, glob, json, traceback, shutil, math
from pathlib import Path
import datetime, time
import teradata, teradatasql #teradatasqlalchemy
import urllib.parse as urllib
from urllib.parse import quote_plus as quote_plus
import pyodbc, pandas as pd
from functools import wraps
from sqlalchemy import create_engine

# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage


#================================================================
# Check if environment variable is set
#================================================================
try:
    if os.name == 'nt': # This is for windows
        _env = os.environ['kds-python-config']
    else: # This is for mac
        _env = os.environ['kds_python_config']
    print("User's Environment variable:" + str(_env))
except:
    print("Configuration file _env variable is not set.")
    print("set kds-python-config variable")
    sys.exit(1)


    
#===============================================================
# If environment variable is set then read the config yaml file
#===============================================================
with open(_env,"r") as yamlConfig:
    cfg = yaml.safe_load(yamlConfig)

#################################################################
# Generate a logger 
#################################################################
class Generate_Logger:  
    """
    When instantiated, creates a logging object.
    
    """    
    #Main constructor of the Generate_Logger class.
    def __init__(self,*args, **kwargs):
        self.logger = logging.getLogger(__name__)
        
        if kwargs.get('jobFrequency') is None:
            self.timeStampObj = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        elif kwargs.get('jobFrequency').lower().strip() == 'high':
            self.timeStampObj = datetime.datetime.now().strftime('%Y%m%d')
        else:
            self.timeStampObj = datetime.datetime.now().strftime('%Y%m%d%H%M%S') 
            
        self.programName = kwargs.get('programName')
        
        if kwargs.get('nestedDirName') is None:
            self.fileName = cfg.get('KDS_LOG').get('log_loc') + self.timeStampObj + "_" + self.programName + ".log"
        else:
            self.fileName = Path(cfg.get('KDS_LOG').get('log_loc') + '\\' + kwargs.get('nestedDirName') + '\\' + self.timeStampObj + "_" + self.programName + ".log")
            
        self.appname = kwargs.get('appname')
        self.loglevel= cfg.get(self.appname).get('log_level')
        
        if self.loglevel.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif self.loglevel.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif self.loglevel.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        elif self.loglevel.lower() == "error":
            self.logger.setLevel(logging.ERROR)

        if self.logger.handlers:
            self.logger.handlers = []
   
        self.file_handler = logging.FileHandler(self.fileName)
        self.formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s')

        self.file_handler.setFormatter(self.formatter)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)
        
    # Class methods that can be accessed using the class instance.
    def log_info(self, msg):
       self.logger.info(msg)
       
    def log_warning(self, msg):
        self.logger.warning(msg)        
    
    def log_error(self, msg):
        self.logger.error(msg)
    
    def log_debug(self, msg):
        self.logger.debug(msg)  
     
    # This method cleans up the logging object/handlers and exits the log file.
    def delete(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.flush()
            handler.close()
            self.logger.removeHandler(handler)   


#################################################################
# Templates for database connections
# Depending on the type of connection, proper key word arguments 
# must be passed to get the connection variable.
#################################################################

def get_kds_teradata_conn(**kwargs):
    
    trycntr = 1
    stoptrying = False
    
    while not stoptrying:

        try:   
            udaExec = teradata.UdaExec (appName='kds', version="2", configureLogging=False, logConsole = False)
            conn = udaExec.connect(DSN=kwargs.get('ODBC_name'),method="odbc")
            stoptrying = True
        except Exception as e:            
            if trycntr >= 3:
                print('Unable to connect to EDW: ' + str(e))
                conn = e
                stoptrying = True
                
            trycntr += 1
            time.sleep(3)

    return conn


def get_sqlalchemy_teradata_engine(**kwargs):

    if  kwargs.get('username') is not None:
        user_ = kwargs.get('username')
    elif kwargs.get('userid') is not None:
        user_ = kwargs.get('userid')
    elif kwargs.get('user') is not None:
        user_ = kwargs.get('user')
        
        
    if os.name == 'posix': # This is a mac
        edw_engine = create_engine("teradatasql://{host}/?logmech=LDAP&username={username}&password={password}"
                                   .format(host = quote_plus(kwargs.get('server')),
                                           username = quote_plus(user_),
                                           password = quote_plus(kwargs.get('password')))).connect()
        
    else:
        params_str = urllib.quote("""DRIVER={driver};DBCNAME={host};UID={username};PWD={password};authentication=LDAP;"""
                           .format(driver = quote_plus(kwargs.get('driver')),
                                   host = quote_plus(kwargs.get('server')),
                                   username = quote_plus(user_),
                                   password = quote_plus(kwargs.get('password'))))  
        
        conn_str = 'mssql+pyodbc:///?odbc_connect={params_str}'.format(params_str=params_str)
        
        edw_engine = create_engine(conn_str, fast_executemany=True)        

    return edw_engine


def get_pyodbc_windowsauth_conn(**kwargs):
   
    params_str = urllib.quote("""Driver={driver};Server={server};Database={database};Trusted_Connection=yes;""".format(driver=kwargs.get('driver'),
                                                   server=kwargs.get('server'),
                                                   database=kwargs.get('database')))
    conn_str = 'mssql+pyodbc:///?odbc_connect={params_str}'.format(params_str=params_str)    
    
    return conn_str


def get_pyodbc_windowsauth_sa_engine(**kwargs):
   
    params_str = urllib.quote("""Driver={driver};Server={server};Database={database};Trusted_Connection=yes;""".format(driver=kwargs.get('driver'),
                                                   server=kwargs.get('server'),
                                                   database=kwargs.get('database')))
    conn_str = 'mssql+pyodbc:///?odbc_connect={params_str}'.format(params_str=params_str)
    
    sqlsaengine = create_engine(conn_str, fast_executemany=True)
    
    return sqlsaengine


def get_pyodbc_windowsauth_cnxn(**kwargs):

    params_str = ("Driver={driver};Server={server};Database={database};Trusted_Connection={trusted_connection};").format(
        driver=kwargs.get('driver'),
        server=kwargs.get('server'),
        database=kwargs.get('database'),
        trusted_connection="yes")
        
    conn = pyodbc.connect(params_str)   
    
    return conn    


def get_pyodbc_credentials_conn(**kwargs):
    
    if  kwargs.get('username') == None:
        user_ = kwargs.get('user')
    else:
        user_ = kwargs.get('username')
    
    params_str = ("Driver={driver};Server={server};Database={database};Uid={user};Pwd={password};").format(
                                            driver=kwargs.get('driver'),
                                            server=kwargs.get('server'),
                                            database=kwargs.get('database'),
                                            user=user_,
                                            password=kwargs.get('password'))
    
    conn = pyodbc.connect(params_str)
    
    return conn


def get_pyodbc_credentials_sa_engine(**kwargs):
    
    if  kwargs.get('username') == None:
        user_ = kwargs.get('user')
    else:
        user_ = kwargs.get('username')
    
    params_str = urllib.quote("""Driver={driver};Server={server};Database={database};Uid={user};Pwd={password};""".format(
                                                   driver=kwargs.get('driver'),
                                                   server=kwargs.get('server'),
                                                   database=kwargs.get('database'),
                                                   user=user_,
                                                   password=kwargs.get('password')
                                                   ))
    conn_str = 'mssql+pyodbc:///?odbc_connect={params_str}'.format(params_str=params_str)
   
  
    
    sqlACEngine = create_engine(conn_str, fast_executemany=True)
    
    return sqlACEngine


def get_pyodbc_azure_ad_auth_conn(**kwargs):
    params_str = ("Driver={driver};Server={server};Database={database};Authentication={auth};").format(
        driver=kwargs.get('driver'),
        server=kwargs.get('server'),
        database=kwargs.get('database'),
        auth=kwargs.get('auth'))
    
    conn = pyodbc.connect(params_str)
    
    return conn

    
def get_pyodbc_azure_credentials_conn(**kwargs):
    
    if  kwargs.get('username') == None:
        user_ = kwargs.get('user')
    else:
        user_ = kwargs.get('username')
        
    params_str = ("Driver={driver};Server={server};Database={database};Uid={username};Pwd={password};").format(
        driver=kwargs.get('driver'),
        server=kwargs.get('server'),
        database=kwargs.get('database'),
        username=user_,
        password=kwargs.get('password'))
    
    conn = pyodbc.connect(params_str)
    
    return conn   


def get_sqlalchemy_sql_credentials_engine(**kwargs):

    if  kwargs.get('username') is not None:
        user_ = kwargs.get('username')
    elif kwargs.get('userid') is not None:
        user_ = kwargs.get('userid')
    elif kwargs.get('user') is not None:
        user_ = kwargs.get('user')
        
    if os.name == 'posix': # This is a mac
        sql_engine = create_engine("mssql+pymssql://{username}:{password}@{host}/{database}".format(host=quote_plus(kwargs.get('server')),
                                                                                                    database=quote_plus(kwargs.get('database')),
                                                                                                    username=quote_plus(user_),
                                                                                                    password=quote_plus(kwargs.get('password')))).connect()            
    else:
        params_str = urllib.quote("""Driver={driver};Server={server};Database={database};Uid={user};Pwd={password};""".format(
                                                       driver=quote_plus(kwargs.get('driver')),
                                                       server=quote_plus(kwargs.get('server')),
                                                       database=quote_plus(kwargs.get('database')),
                                                       user=quote_plus(user_),
                                                       password=quote_plus(kwargs.get('password'))))
               
        conn_str = 'mssql+pyodbc:///?odbc_connect={params_str}'.format(params_str=params_str)      
        
        sql_engine = create_engine(conn_str, fast_executemany=True)
       
    return sql_engine

    
def senderroremail(**kwargs):
    
    programName_ = kwargs.get('programName')

    msg = EmailMessage()
    msg.set_content("There was an error running " + programName_ + os.linesep + kwargs.get('errStackTrace'))
    msg['Subject'] = 'Error executing ' + programName_
    msg['From'] = cfg.get('EMAIL').get('reply')
    msg['To'] = cfg.get(kwargs.get('appName')).get('support_email')
    
    # Send the message via our own SMTP server.
    if  cfg.get('EMAIL').get('SMTP') is not None:
        s = smtplib.SMTP(cfg.get('EMAIL').get('SMTP'))
    else:
        s = smtplib.SMTP(cfg.get('EMAIL').get('smtp'))

    s.send_message(msg)
    s.quit()
    
    return

    
def emaillogfile(**kwargs):
    
    programName_ = kwargs.get('programName')
    fileName_ = kwargs.get('fileName')

    msg = EmailMessage()
    msg.set_content("Please find the attached file for  " + programName_ + ".py's latest log.")
    msg['Subject'] = 'Log for ' + programName_ + '.py'
    msg['From'] = cfg.get('EMAIL').get('reply')
    msg['To'] = cfg.get(kwargs.get('appName')).get('support_email')
    try:
        msg.add_attachment(open(fileName_, "r").read(), filename=fileName_.split('\\')[-1])
    except Exception as e:
        msg.set_content("The KDSutil was unable to not find the log file for  " + programName_ + ".py's latest run.")
        
    # Send the message via our own SMTP server.
    s = smtplib.SMTP(cfg.get('EMAIL').get('SMTP'))
    s.send_message(msg)
    s.quit()
    
    return


def sendemailnotification(**kwargs):
    
    programName_ = kwargs.get('programName')

    msg = EmailMessage()
	
    if  kwargs.get('emailContent') is not None:
        emailContent_ = kwargs.get('emailContent')
    else:
        emailContent_ = 'This is the requested email for '	+ programName_

    msg['From'] = cfg.get('EMAIL').get('reply')
    msg['To'] = cfg.get(kwargs.get('appName')).get('support_email')
    msg.set_content(emailContent_)
    msg['Subject'] = 'Email Notification For ' + programName_ + '.py'
	
    # Send the message via our own SMTP server.
    s = smtplib.SMTP(cfg.get('EMAIL').get('SMTP'))
    s.send_message(msg)
    s.quit()
    
    return


def read_parquet_files(path, match_pattern=None):    
    listOfParquetFiles = glob.glob(path + "/*.parquet") if match_pattern is None else glob.glob(path + f"/*{match_pattern}*.parquet")
    df = [pd.read_parquet(f) for f in listOfParquetFiles]
    df_all = pd.concat(df,ignore_index=True)
    df_all.reset_index(inplace=True, drop=True)

    return df_all


def create_folder(folder, DeleteIfExists):
    if DeleteIfExists:
        if Path(folder).is_dir():
            shutil.rmtree(folder)
            os.makedirs(folder)
    else:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
    return


def generate_metadata(*args):
    
    file = args[0]
    script = args[1]
    version = args[2]
    source = args[3]
    source_sql = args[4]
    description = args[5]
    df = args[6]    

    file = file.replace('\\','/')
    script = script.replace('\\','/')
    file_name = file.rsplit('/',1)[1]
    path = file.replace(file_name,'')
    path = path[:-1] if path[-1]=='/' else path
    json_str = '''{
    
                "file": "''' + file_name + '''",
                "path": "''' + path + '''",
                "version": "''' + version + '''",
                "source": "''' + source + '''",
                "source_sql": ''' + json.dumps(source_sql) + ''',
                "description": "''' + description + '''",
                "created on": "''' + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + '''",
                "created by": "''' + script + '''",
                "data_structure": [ '''
    for ind, column in enumerate(df.columns):
        json_str = json_str + '{' + f' "position": "{ind+1}", "column": "{column}", "dtype": "' + df.dtypes[column].name + '"},'
    json_str = json_str[:-1] if json_str[-1]==',' else json_str
    json_str = json_str + ''']
    
    }'''
                                   
    json_file = file.replace('.parquet','') + '.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json.loads(json_str), f, ensure_ascii=False, indent=4)

    return

#This decorator function adds timer to your functions
# can be called by adding the below at the top of your function
# @kdsutil.fn_execution_timer(logutilobj)
def fn_execution_timer(_loggerobj):
    def decorator(orig_func):
        @wraps(orig_func)
        def wrapper(*args, **kwargs):
            t1 = time.time()
            result = orig_func(*args, **kwargs)
            t2 = time.time() - t1
            print('{} ran in: {} seconds'.format(orig_func.__name__, t2))
            _loggerobj.log_info('{} ran in: {} seconds'.format(orig_func.__name__, t2))
            
            return result    
        return wrapper
    return decorator

#Pass in the Database name, Table name  and your dataframe to load it to the table eg: kdsutil.load_df_to_edw('EDW_PRD_SB_KDS','MX_TABLE',df)
#An optional kwarg is available in case it's not a kill and fill table eg: kdsutil.load_df_to_edw('EDW_PRD_SB_KDS','MX_TABLE',df, purge='N)

def load_df_to_edw(*args, **kwargs):    
    db  = args[0]
    table = args[1]
    df = args[2]

    if  kwargs.get('purge') is not None:
        if kwargs.get('purge').upper() == 'N' or  kwargs.get('purge').upper() == 'NO':
            purge = False
    else:
        purge = True

    df.drop_duplicates(inplace=True)
    numcols = df.shape[1]
    df_lst = [tuple(x) for x in df.values]
    nRows = len(df)
    nRowsPerBatch = 2500 if numcols < 50 else 500
    nBatchCount = math.ceil(nRows/nRowsPerBatch)
    sTableName = db + '.' + table
    
    start = 0
    finish = nRowsPerBatch
    
    conn_edw = get_kds_teradata_conn(**cfg.get('edw'))
    
    if purge:   
        del_str = f"""DELETE FROM {sTableName};"""
        cursor = conn_edw.cursor()
        cursor.execute(del_str)            
    
    qstr = '?,'
    itr = 1
    
    for q in range(numcols-1):  
        if itr == numcols-1:
            qstr += '?'
            break
        qstr += '?,'     
        itr += 1
            
    with conn_edw as session:
        for batch in range(0, nBatchCount):
            session.executemany(f"""INSERT INTO {sTableName} VALUES ({qstr})"""
                                , df_lst[start:finish], batch=True)
            start = start + nRowsPerBatch
            finish = finish + nRowsPerBatch
            
    return 
 
#################################################################
# Main function equivalent. 
# Only gets executed when this file is run independently  
#################################################################
if __name__ == '__main__':          
    
   _filename = sys.argv[0].split(os.path.sep)[-1].split('.')[0]
   print(_filename)
   
   loggerdetails= {'appname':'KDS_UTIL'}
   #Create a logging instance of the Generate_Logger class.
   logutilobj = Generate_Logger(**loggerdetails)
   
   try:
       #Invoke the log_info class method for the logutilobj.
       logutilobj.log_info('Main function test begin.')
       result = 10/0
    
   except:
       err = sys.exc_info()[0]
       #Invoke the log_error class method for the logutilobj.
       logutilobj.log_error('Tried to divide by zero')
       errStackTrace = traceback.format_exc(limit=None, chain=True)
       #Invoke the log_error class method for the logutilobj.
       logutilobj.log_error(errStackTrace)
       logutilobj.delete() 
       print('completed the except section')
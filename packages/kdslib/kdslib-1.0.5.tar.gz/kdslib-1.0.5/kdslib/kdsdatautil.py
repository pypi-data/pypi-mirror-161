# module level doc-string
__doc__ = """
General data request utility module for KDS

@author: Himanshu Gadgil
Created on Fri Jun 24 09:47:44 2022

# Functionality: Returns a dataset (in a pandas dataframe format) by combining #
#                parquet files in the KDS datalake for various classifications #
#                & datasets.                                                   #

"""

import os, yaml, sys, traceback
import datetime
import pandas as pd
import random
import inspect, socket
from kdslib import kdsutil

#================================================================
# Check if environment variable is set
#================================================================
try:
    if os.name == 'posix': # This is a mac
        v_env = os.environ['kds_python_config']
    else:
        v_env = os.environ['kds-python-config']
except:
    print("Configuration file env variable is not set.")
    print("set kds-python-config variable")
    sys.exit(1)
    
#===============================================================
# If environment variable is set then read the config yaml file
#===============================================================
with open(v_env,"r") as yamlConfig:
    cfg = yaml.safe_load(yamlConfig)

#################################################################
# Get the current file name
#################################################################
programName = os.path.basename(__file__)
appConfigName = "KDS_LOG"
ExecMode = cfg.get('PYTHON_EXEC_MODE').get('INTERACTIVE')

kds_data_root = cfg.get('KDS_DATA').get('data_lake_root')
kds_data_de = cfg.get('KDS_DATA').get('data_eng')
kds_data_ds = cfg.get('KDS_DATA').get('data_sci')
kds_de_data_root = kds_data_root + '/' + kds_data_de
kds_data_wrapper = kds_de_data_root + '/DATA_WRAPPER/DataWrapper_DataSets.json'
kds_data_wrapper_log_dir = kds_de_data_root + '/DATA_WRAPPER/EXEC_LOG/'
df_dl_wrapper = pd.read_json(kds_data_wrapper) 

#################################################################
# Generate a logger to log info
#################################################################
logutilobj = kdsutil.Generate_Logger(appname=appConfigName, programName=programName)

def get_data(data_classification_, data_set_list_):
    
    #separate the main and other datasets into individual dataframes so we can process them
    df_dl_wrapper_data = df_dl_wrapper[df_dl_wrapper['DataClassification'].str.lower() == data_classification_.lower()]
    df_dl_wrapper_main = df_dl_wrapper_data[df_dl_wrapper_data['IsMain'] == 1]
    df_dl_wrapper_other= df_dl_wrapper_data[df_dl_wrapper_data['IsMain'] == 0]

    #Get the main data parquet location and replace the constant values with config values
    data_file = df_dl_wrapper_main['ParquetFileAndLocation'].iloc[0]
    data_file = data_file.replace(r'{KDS_DL_ROOT}',kds_data_root)
    if (r'{KDS_DE_DATA}' in data_file):
        data_file = data_file.replace(r'{KDS_DE_DATA}',kds_data_de)
    if (r'{KDS_DS_DATA}' in data_file):
        data_file = data_file.replace(r'{KDS_DS_DATA}',kds_data_ds)
    #Also get the columns that we need to return from the main dataframe.
    main_columns = df_dl_wrapper_main['ReturnColumn'].iloc[0]
    main_dataset_name = df_dl_wrapper_main['DataSet'].iloc[0]
    #Read the main data parquet into a dataframe
    main_df = pd.read_parquet(data_file)
    #change all the column names to lowercase so we have conformity
    main_df.columns = main_df.columns.str.lower()
    #Get the last modified datetime so we can log it
    file_TimeStamp = datetime.datetime.fromtimestamp(os.stat(data_file).st_mtime).strftime("%m/%d/%Y %H:%M:%S")
    row_count = len(main_df)
    log_df = pd.DataFrame({'data_classification': [data_classification_], 
                           'data_set': [main_dataset_name], 
                           'is_main': [1], 
                           'join_criteria': ['nan'],
                           'as_of_datetime': [file_TimeStamp],
                           'row_count': [row_count]
                          })

    if main_columns != r'*':
        #If the column list was specific and not a * then only return the columns that were asked for
        main_column_list = main_columns.replace('[','').replace(']','').replace(' ','').split(',')
        main_column_list = list(set(main_column_list))
        main_df = main_df[main_df.columns.intersection(main_column_list)]
    
    #df dataframe will be our holding dataframe that will then be joined and eventually returned to the calling app
    df = main_df
    
    #Get the list of datasets that we need to join into a dataframe
    #data_set_list_ = [x.lower() for x in data_set_list_]
    ds_df = pd.DataFrame(columns=['dataset_name','join_criteria'])
    for ds in data_set_list_:
        join_criteria = 'left'
        if ':' in ds:
            join_criteria = ds.split(':')[1]
            data_set_name = ds.split(':')[0]
            join_criteria = join_criteria.lower()
            data_set_name = data_set_name.lower()
        else:
            data_set_name = ds
        df2 = pd.DataFrame({'dataset_name': [data_set_name], 'join_criteria': [join_criteria]})
        ds_df = pd.concat([ds_df,df2], ignore_index=True)
    ds_df['dataset_name'] = ds_df['dataset_name'].str.lower()
    ds_df['join_criteria'] = ds_df['join_criteria'].str.lower()
    
    #Process each of the other data files in the same data classification and join if asked for
    for index, row in df_dl_wrapper_other.iterrows():
        dataset_name = row['DataSet']
        dataset_name = dataset_name.lower()
        dataset_name_df = ds_df[ds_df['dataset_name'] == dataset_name]
        if (len(dataset_name_df) > 0):
            dataset_name = dataset_name_df['dataset_name'].iloc[0]
            join_criteria = dataset_name_df['join_criteria'].iloc[0]
            #Get the parquet file location for the data that we need to join
            data_file = row['ParquetFileAndLocation']
            data_file = data_file.replace(r'{KDS_DL_ROOT}',kds_data_root)
            if (r'{KDS_DE_DATA}' in data_file):
                data_file = data_file.replace(r'{KDS_DE_DATA}',kds_data_de)
            if (r'{KDS_DS_DATA}' in data_file):
                data_file = data_file.replace(r'{KDS_DS_DATA}',kds_data_ds)
            #read the data parquet into a dataframe
            df_tmp = pd.read_parquet(data_file)
            #change the column names to lowercase
            df_tmp.columns = df_tmp.columns.str.lower()
            file_TimeStamp = datetime.datetime.fromtimestamp(os.stat(data_file).st_mtime).strftime("%m/%d/%Y %H:%M:%S")
            row_count = len(df_tmp)
            log_df = pd.concat([log_df,
                                pd.DataFrame({'data_classification': [data_classification_], 
                                              'data_set': [dataset_name], 
                                              'is_main': [0], 
                                              'join_criteria': [join_criteria],
                                              'as_of_datetime': [file_TimeStamp],
                                              'row_count': [row_count]
                                             })
                               ], ignore_index=True)

            #Get the columns that we need to return back to the calling app            
            columns = row['ReturnColumn'].lower()

            #Get the columns that we need to join on
            join_column = row['JoinColumn'].replace('[','').replace(']','').replace(' ','').lower().split(',')
            #for each of the columns that we have in the join if the column is of type string 
            #then lets convert it to lower case and create a new column that we will use for the join
            #after the join is done we will drop these columns before we send the data back to the app
            new_join_column_l = []
            new_join_column_r = []
            org_join_col = []
            for org_col in join_column:
                #Generate the new column name for the left and right side of the join
                new_col_l = org_col + '_4join_l'
                new_col_r = org_col + '_4join_r'
                #Store the original join column list so we can remove it from the right side of the dataframes before the merge
                #this avoids having column names with _x or _y in the result set.
                org_join_col += [org_col]
                #Add the new column name to the list
                new_join_column_l += [new_col_l]
                new_join_column_r += [new_col_r]
                #Create a new column in the main dataframe and the new dataframe
                #use try/catch to not break the code if the datatype of the column is not string
                #Can check the dtype since datetime also return dtype as object
                try:
                    df_tmp[new_col_r] = df_tmp[org_col].str.lower()
                except:
                    df_tmp[new_col_r] = df_tmp[org_col]

                try:
                    df[new_col_l] = df[org_col].str.lower()
                except:
                    df[new_col_l] = df[org_col]
                    

            if columns != r'*':
                column_list = columns.replace('[','').replace(']','').replace(' ','').split(',')
                column_list = column_list + new_join_column_r
                column_list = list(set(column_list))
                df_tmp = df_tmp[df_tmp.columns.intersection(column_list)]

            #Remove the join columns from the right side dataframe so we don't get the _x or _y columns
            for col in org_join_col:
                if col in df_tmp.columns:
                    del df_tmp[col]
            
            #Now merge the 2 dataframes
            df = df.merge(df_tmp, left_on=new_join_column_l, right_on=new_join_column_r, how=join_criteria, copy=True)
            
            #Now drop the join columns that we used so as to return the original column list back to the calling app
            remove_join_columns = new_join_column_l + new_join_column_r
            df = df.drop(columns=remove_join_columns)
            
    return df, log_df
    
def filter_data(df, data_filter):
    lst_filter_ = data_filter.split(':')
    lst_col=[]
    for f in lst_filter_:
        lst_f=f.split('=')
        col_name = lst_f[0][0:].lower()
        lst_col=lst_col + [col_name]
        values_ = lst_f[1][0:]
        lst_values_ = values_.split(',')
        df=df[df[col_name].isin(lst_values_)]
    
    return df
    
def get_info(): return pd.read_json(kds_data_wrapper)
    
def get_dl_data(**kwargs):
    """
    joins the various requested datasets and also filters them if needed.
    

    Parameters
    ----------
    **kwargs : 
        data_classification: str, required
            This is request what collection/class of data is being requsted.
            eg: data_classification = 'project'
        data_set_list: list[str], optional
            This is an optional parameter containing names of various datasets that need to be joined and how to join them
            There can be 2 parts to this string seperated by a ':' (optional)
            if no ':' is supplied then the string is the dataset name and the type of join is 'left'
            if ':' is supplied then the left side of the string is the dataset name and right is how to join
            eg: data_set_lst = ['climate','population']
        data_used_for: str, required
            This is a string that is passed in to let the call know what this data is going to be used for.
        data_filter: str, optional
            This is an optional paramter that specifies the filters to be applied. This string is a name value pair seperated by 
            '='. If more than 1 filter need to be applied and then multiples can be passed by separating them by ':'
            eg: data_filter = 'PROJECT_Number=103066,103057,101417:INDUSTRY=Power'
    Raises
    ------
    ValueError
        If required parameters were not supplied value error is raised.

    Returns
    -------
    ret_df_ : pandas.DataFrame
        dataframe containing joined and filtered data

    """

    #Get the calling script name
    frame_ = inspect.stack()[1]
    module_ = inspect.getmodule(frame_[0])
    try:
        filename_ = module_.__file__
    except:
        filename_ = 'no script probably jupiter notebook'
    computer_name_ = socket.gethostname()
    
    data_classification_ = None
    data_set_list_ = ''
    data_used_for_ = None
    data_filter_ = None
    ret_df_ = pd.DataFrame()
    user_ = os.getlogin()
    curr_date_ = datetime.datetime.now()
    
    if kwargs.get('data_classification') is not None:
        data_classification_ = kwargs.get('data_classification')
    if kwargs.get('data_set_list') is not None:
        data_set_list_ = kwargs.get('data_set_list')
    if kwargs.get('data_used_for') is not None:
        data_used_for_ = kwargs.get('data_used_for')
    if kwargs.get('data_filter') is not None:
        data_filter_ = kwargs.get('data_filter')
    
    if data_classification_ is None:
        raise ValueError("data_classification parameter wasn't passed to the call")
    if (data_used_for_ is None) or (len(data_used_for_) == 0):
        raise ValueError("data_used_for parameter wasn't passed to the call")
    
    logutilobj.log_info(f"data_classification={data_classification_}~~data_set_list={data_set_list_}~~user={user_}~~exec_dt={curr_date_}")
    
    ret_df_,log_df = get_data(data_classification_, data_set_list_)
    
    if data_filter_ is not None:
        ret_df_ = filter_data(ret_df_, data_filter_)
        
    log_df['user'] = user_
    log_df['dataset_list'] = ','.join(data_set_list_)
    log_df['data_used_for'] = data_used_for_
    log_df['data_filter'] = data_filter_
    log_df['data_request_datetime'] = curr_date_.strftime("%m/%d/%Y %H:%M:%S")
    log_df['calling_script'] = filename_
    log_df['calling_computer'] = computer_name_
    log_file_name = kds_data_wrapper_log_dir + curr_date_.strftime("%Y%m%d_%H%M%S_%f_") + f'{random.randrange(1, 10**3):03}.parquet'
    log_df.to_parquet(log_file_name)
    
    return ret_df_

#################################################################
# Main function equivalent. 
# Only gets executed when this file is run independently  
#################################################################
if __name__ == '__main__':          
    
   _filename = sys.argv[0].split(os.path.sep)[-1].split('.')[0]
   print(_filename)
   
   try:
       #Invoke the log_info class method for the logutilobj.
       logutilobj.log_info('Main function test begin.')
       data_classification = 'project'
       data_set_lst = ['climate:inner','population']
       data_used_for = 'HG_Testing_1.0'
       #data_filter = 'PROJECT_Number=103066,103057,101417:INDUSTRY=Power' #data_filter=data_filter, 
       x = get_dl_data(data_classification=data_classification, data_set_list=data_set_lst, data_used_for=data_used_for)
    
   except:
       err = sys.exc_info()[0]
       errStackTrace = traceback.format_exc(limit=None, chain=True)
       #Invoke the log_error class method for the logutilobj.
       logutilobj.log_error(errStackTrace)
       logutilobj.delete() 
       print('completed the except section')

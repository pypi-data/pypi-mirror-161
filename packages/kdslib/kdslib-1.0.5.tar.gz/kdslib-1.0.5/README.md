kdslib is an internal project for KDS and is distributed under GNU Lesser General Public License v3 or later (LGPLv3+)

The purpose of this project is to help standardize coding styles and provide basic utilities to all Python developers across KDS.

kdsutil's callable modules include:

-> Logger (for all levels)

-> Teradata Connector

-> SQL database connector (using either windows auth or credentials)

-> Azure SQL database connector (using either windows auth or credentials)

-> Exception emailer

-> Log file emailer

-> Notification emailer

-> Parquet reader (reads all parquet files in a location and returns a Pandas dataframe)

-> Metadata generator (generates a JSON file that contains metadata of a parquet file)

-> Function execution timer (decorator function).

kdsfunctionalutil's callable modules include:

-> Power BI On-demand refresh

-> IICS informatica job refresh

Installation:
  pip install kdslib
 
Subsequent updates:
  pip install kdslib --upgrade

Dependencies:

kdslib requires:
  Python (>= 3.7)
  Pandas (>= 1.4.0)
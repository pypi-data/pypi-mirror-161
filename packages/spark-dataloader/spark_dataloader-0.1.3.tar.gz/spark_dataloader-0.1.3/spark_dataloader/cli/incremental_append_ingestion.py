"""
    Import table from JDBC into Hive using Spark2

    To execute: 

    spark-submit jdbc_loader_spark2.py
"""
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from argparse import ArgumentParser
import random
import string
import glob
import os
import logging
import sys
import copy
from datetime import datetime
from ..rdbms_ingestion import incremental_append_ingestion, conn_from_args, parse_args
from ..rdbms_ingestion import add_common_arguments

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('jdbc-loader-spark2')


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = ArgumentParser()
    add_common_arguments(parser)
    
    parser.add_argument('-r', '--incremental-column')
    parser.add_argument('-R', '--last-value')

    args = parse_args(parser, argv)
    if not args.incremental_column:
        print("-r/--incremental-column is required")
        sys.exit(1)
 
    from pyspark.shell import spark
   
    conn = conn_from_args(spark, args)

    db, tbl = (args.hive_table or args.dbtable).split('.')
    
    # load data from source
    df = conn.load()
    
    source_count = copy.copy(conn).option('pushDownAggregate',
            'true').load().count()
    
    output_partitions = []
    if args.output_partition_columns:
        output_partitions = args.output_partition_columns.split(',')
    
    ingested_count = incremental_append_ingestion(spark, df, db, tbl, 
            args.incremental_column, 
            args.last_value, 
            args.storageformat,
            output_partitions=output_partitions)
    
    dest_count = spark.sql('select * from %s.%s' % (db, tbl)).count()
    
    log.info("Source rows = %s" % source_count)
    log.info("Ingested rows = %s" % ingested_count)
    log.info("Destination rows = %s" % dest_count)
    
if __name__ == '__main__':
    main()

"""
    Import table from JDBC into Hive using Spark2

    To execute: 

    spark-submit jdbc_loader_spark2.py
"""

from pyspark.sql import functions as F
from argparse import ArgumentParser
import glob
import os
from argparse import ArgumentParser
import logging
import sys
import copy
from ..rdbms_ingestion import full_ingestion, conn_from_args, parse_args
from ..rdbms_ingestion import add_common_arguments

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('jdbc-loader-spark2')

def main(argv=None):
    argv = argv or sys.argv[1:]

    parser = ArgumentParser()
    add_common_arguments(parser)
    args = parse_args(parser, argv)

    from pyspark.shell import spark

    conn = conn_from_args(spark, args)
    df = conn.load()
    db, tbl = (args.hive_table or args.dbtable).split('.')
    
    source_count = copy.copy(conn).option('pushDownAggregate',
            'true').load().count()
    
    output_partitions = []
    if args.output_partition_columns:
        output_partitions = args.output_partition_columns.split(',')
    
    ingested_count = full_ingestion(spark, df, db, tbl, args.overwrite,
            args.storageformat, output_partitions=output_partitions)
    
    dest_count = spark.sql('select * from %s.%s' % (db, tbl)).count()
    
    log.info("Source rows = %s" % source_count)
    log.info("Ingested rows = %s" % ingested_count)
    log.info("Destination rows = %s" % dest_count)


if __name__ == '__main__':
    main()

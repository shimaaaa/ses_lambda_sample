import os
import sys
from operator import add
from random import random

import pyspark
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType, TimestampType

os.environ[
    "PYSPARK_SUBMIT_ARGS"
] = "--packages com.amazonaws:aws-java-sdk:1.10.34,org.apache.hadoop:hadoop-aws:2.6.0 pyspark-shell"


def main():
    testColumn = StructType(
        [
            StructField("eventType", StringType(), False),
            StructField(
                "mail",
                StructType(
                    [
                        StructField("messageId", StringType(), False),
                        StructField("timestamp", TimestampType(), False),
                    ]
                ),
                False,
            ),
        ]
    )

    spark = SparkSession.builder.appName("test").getOrCreate()

    sc = spark.sparkContext

    hadoopConf = sc._jsc.hadoopConfiguration()
    hadoopConf.set("fs.s3.impl", "org.apache.hadoop.fs.s3.S3FileSystem")
    hadoopConf.set("fs.s3n.impl", "org.apache.hadoop.fs.s3native.NativeS3FileSystem")
    hadoopConf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    hadoopConf.set("fs.s3.awsAccessKeyId", os.environ["AWS_ACCESS_KEY_ID"])
    hadoopConf.set("fs.s3.awsSecretAccessKey", os.environ["AWS_SECRET_ACCESS_KEY"])
    hadoopConf.set("fs.s3.buffer.dir", "/tmp")
    hadoopConf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    df = spark.read.json(
        "s3n://seslogtest/ses_message/logs/payloads/date=2020-12-31/*/*.json",
        schema=testColumn,
    )
    df = df.select(
        "eventType",
        F.col("mail.messageId").alias("messageId"),
        F.col("mail.timestamp").alias("timestamp"),
    )
    df.write.parquet("s3n://seslogtest/ses_message/logs/converted/date=2020-12-31/")
    df.show()


if __name__ == "__main__":
    main()

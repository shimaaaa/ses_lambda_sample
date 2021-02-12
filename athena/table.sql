CREATE EXTERNAL TABLE `ses_event_log`(
  `eventtype` string,
  `complaint` struct<arrivaldate:string,
                     complainedrecipients:array<struct<emailaddress:string>>,
                     complaintfeedbacktype:string,
                     feedbackid:string,
                     timestamp:string,useragent:string
                     >,
  `bounce` struct<bouncedrecipients:array<struct<action:string,diagnosticcode:string,emailaddress:string,status:string>>,
                  bouncesubtype:string,
                  bouncetype:string,
                  feedbackid:string,
                  reportingmta:string,
                  timestamp:string
                   >,
  `mail` struct<timestamp:string,
                source:string,
                sourceArn:string,
                sendingAccountId:string,
                messageId:string,
                destination:string,
                headersTruncated:boolean,
                headers:array<struct<name:string,value:string>>,
                commonHeaders:struct<`from`:array<string>,to:array<string>, messageId:string,subject:string>,
                tags:struct<ses_configurationset:string,ses_source_ip:string,ses_outgoing_ip:string,ses_from_domain:string,ses_caller_identity:string>
                >,
  `send` string,
  `delivery` struct<processingtimemillis:int,recipients:array<string>,reportingmta:string,smtpresponse:string,timestamp:string>,
  `click` struct<ipaddress:string,link:string,linktags:string,timestamp:string,useragent:string>,
  `open` struct<ipaddress:string,timestamp:string,userAgent:string>,
  `mail_timestamp` string,
  `mail_destination` string,
  `mail_message_id` string,
  `mail_title` string
)
PARTITIONED BY ( 
  `dt` string
)
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://seslogtest/kinesis'
TBLPROPERTIES (
  'has_encrypted_data'='false', 
  'transient_lastDdlTime'='1611068201',
  'projection.enabled'='true',
  'projection.dt.type'='date',
  'projection.dt.range'='NOW-3YEARS,NOW',
  'projection.dt.format'='yyyy-MM-dd',
  'projection.dt.interval'='1',
  'projection.dt.interval.unit'='DAYS'
)
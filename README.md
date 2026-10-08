# Web Server Anomaly Detection System

A production-oriented Big Data pipeline for processing large Nginx
access logs, generating behavioral features with Hadoop/Spark, detecting
anomalies with robust statistical analysis, storing analytical results
in MongoDB, and serving dashboard-ready REST APIs through FastAPI.

> **Project focus:** Big Data engineering + distributed processing +
> explainable statistical anomaly detection.\
> **Anomaly types:** Traffic Spike, HTTP Error Rate, URL/Resource
> Access.

------------------------------------------------------------------------

## 1. Project Overview

Web servers continuously generate access logs. At millions of records,
manually inspecting these logs is impractical and simple threshold-based
scripts become difficult to maintain.

This project builds an end-to-end system that transforms:

``` text
Raw Nginx Logs
      ↓
Streaming Parser
      ↓
Structured Parquet
      ↓
HDFS Distributed Storage
      ↓
Apache Spark Processing
      ↓
5-Minute IP-Level Behavioral Features
      ↓
Historical Robust Statistical Baselines
      ↓
Anomaly Detection
      ↓
MongoDB Analytical Store
      ↓
FastAPI REST APIs
      ↓
React Dashboard
```

The system does **not** depend on a trained ML model. Instead, it uses
an IP-specific historical baseline based on the previous five
observations, median, Median Absolute Deviation (MAD), robust Z-score,
and explicit fallback rules for zero-MAD cases.

------------------------------------------------------------------------

# 2. Problem Statement

The input is a large Nginx web-server access log containing millions of
HTTP requests.

Important information includes:

-   client IP
-   timestamp
-   HTTP method
-   URL/resource
-   protocol
-   status code
-   response size
-   referer
-   user agent

The challenge is to build a scalable system that can:

1.  Parse the raw text safely.
2.  Preserve malformed records.
3.  Store structured data efficiently.
4.  Distribute the dataset through HDFS.
5.  Process millions of records using Spark.
6.  Convert raw requests into useful behavioral windows.
7.  Detect unusual client behavior.
8.  Store the results for fast application queries.
9.  Expose those results through APIs.
10. Visualize the results through a dashboard.

------------------------------------------------------------------------

# 3. Main Objectives

-   Process a large real-world web-server dataset.
-   Demonstrate distributed storage using HDFS.
-   Demonstrate distributed computation using Apache Spark.
-   Build reusable five-minute IP-level features.
-   Implement explainable anomaly detection.
-   Avoid global thresholds that ignore individual IP behavior.
-   Use robust statistics suitable for highly skewed web traffic.
-   Persist analytical results in MongoDB.
-   Provide a clean service-oriented FastAPI backend.
-   Provide a dashboard-ready React frontend architecture.
-   Containerize the distributed Hadoop/Spark environment.
-   Keep the project reproducible and Git-friendly.

------------------------------------------------------------------------

# 4. Anomaly Types

## 4.1 Traffic Spike

Detects an IP whose request volume becomes unusually high compared with
its own recent behavior.

Primary metric:

``` text
request_count
```

------------------------------------------------------------------------

## 4.2 HTTP Error Rate

Detects an IP whose HTTP error rate becomes unusually high compared with
its historical behavior.

Primary metrics:

``` text
total_requests
error_requests
error_rate
```

------------------------------------------------------------------------

## 4.3 URL / Resource Access

Detects an IP that suddenly accesses an unusually large number of
distinct resources.

Primary metric:

``` text
unique_url_count
```

------------------------------------------------------------------------

# 5. High-Level Architecture

``` text
                         ┌─────────────────────┐
                         │  Kaggle Nginx Logs  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Streaming Parser   │
                         │ Python + PyArrow    │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                 Valid Parquet          Parser Error Log
                         │
                         ▼
              ┌───────────────────────┐
              │       HDFS Cluster    │
              │                       │
              │ NameNode              │
              │   ├── DataNode        │
              │   └── DataNode        │
              └───────────┬───────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │      Spark Cluster     │
              │                        │
              │ Spark Master           │
              │   ├── Worker 1         │
              │   └── Worker 2         │
              └───────────┬────────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
     Traffic          Error Rate        URL Access
   Aggregation       Aggregation       Aggregation
          │               │                │
          └───────────────┼────────────────┘
                          ▼
               Statistical Detection
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Traffic       Error         URL
          Detector     Detector      Detector
             │            │            │
             └────────────┼────────────┘
                          ▼
                    ┌───────────┐
                    │ MongoDB   │
                    └─────┬─────┘
                          ▼
                    ┌───────────┐
                    │ FastAPI   │
                    └─────┬─────┘
                          ▼
                    ┌───────────┐
                    │ React UI  │
                    └───────────┘
```

------------------------------------------------------------------------

# 6. Complete Data Lifecycle

The project can be divided into these phases:

``` text
Phase 1  → Raw ingestion
Phase 2  → Streaming parsing
Phase 3  → Parquet conversion
Phase 4  → HDFS storage
Phase 5  → Spark aggregation
Phase 6  → Statistical analysis
Phase 7  → Anomaly classification
Phase 8  → MongoDB migration
Phase 9  → FastAPI serving
Phase 10 → React visualization
```

Each phase has a clearly separated responsibility.

------------------------------------------------------------------------

# 7. Technology Stack

  Layer                    Technology
  ------------------------ -------------------
  Input                    Nginx access logs
  Parser                   Python
  Columnar storage         Apache Parquet
  Parquet engine           PyArrow
  Distributed storage      Hadoop HDFS
  Distributed processing   Apache Spark
  Spark API                PySpark
  Containers               Docker
  Analytical database      MongoDB
  Backend                  FastAPI
  Server                   Uvicorn
  Frontend                 React.js
  Version control          Git + GitHub

Versions used during development:

``` text
Apache Spark   4.1.3
PySpark        4.1.3
PyArrow        25.0.1
Hadoop image   3.4.3
MongoDB        8.3
PyMongo        4.18.2
```

The host Spark development environment uses Java 17.

------------------------------------------------------------------------

# 8. Repository Structure

``` text
web-server-anomaly-detection/
│
├── README.md
├── .gitignore
├── requirements.txt
├── docker-compose.yml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── bigdata/
│   ├── hadoop/
│   │   ├── mapper/
│   │   ├── reducer/
│   │   └── jobs/
│   │
│   ├── spark/
│   │   ├── jobs/
│   │   ├── transformations/
│   │   └── utils/
│   │
│   ├── preprocessing/
│   │   ├── schema.py
│   │   └── log_parser.py
│   │
│   └── mongodb/
│       ├── Dockerfile
│       └── migrate_hdfs_to_mongodb.py
│
├── anomaly_detection/
│   ├── traffic_spike/
│   ├── error_rate/
│   └── url_access/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
│
├── cluster/
│   ├── hadoop/
│   └── spark/
│
├── scripts/
│   ├── setup/
│   ├── run/
│   └── deployment/
│
├── tests/
│   ├── bigdata/
│   ├── anomaly_detection/
│   ├── backend/
│   └── frontend/
│
└── docs/
    ├── architecture/
    ├── setup/
    └── reports/
```

Generated/raw data is intentionally excluded from Git.

------------------------------------------------------------------------

# 9. Dataset

The project uses the Kaggle **Web Server Access Logs** dataset:

``` text
https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs
```

The raw records follow an Nginx-style format:

``` text
IP - - [timestamp] "METHOD URL PROTOCOL" STATUS RESPONSE_SIZE "REFERER" "USER_AGENT" "-"
```

The parser extracts:

``` text
ip
timestamp
method
url
protocol
status_code
response_size
referer
user_agent
```

------------------------------------------------------------------------

# 10. Phase 1 - Streaming Log Parsing

## Objective

Convert unstructured log lines into typed structured records without
loading the entire dataset into memory.

Conceptual flow:

``` text
access.log
    ↓
read one line
    ↓
parse with regular expression
    ↓
valid?
 ┌──┴──┐
yes    no
 ↓      ↓
record  parser_errors.log
 ↓
batch of 10,000
 ↓
Parquet
```

## Why streaming?

The raw dataset is large. Reading the complete file into RAM would
unnecessarily increase memory usage.

The parser therefore:

-   reads line-by-line
-   parses incrementally
-   creates batches
-   writes batches
-   preserves invalid records

This gives bounded memory usage and makes the parser easier to scale.

------------------------------------------------------------------------

# 11. Parser Schema

The final Parquet schema is:

``` text
ip              string
timestamp       timestamp[us]
method          string
url             string
protocol        string
status_code     int64
response_size   int64
referer         string
user_agent      string
```

------------------------------------------------------------------------

# 12. Parser Results

Full dataset:

``` text
Total lines:       10,365,152
Valid lines:       10,365,075
Invalid lines:            77
Success rate:      ~99.99926%
```

Integrity check:

``` text
valid + invalid = total

10,365,075 + 77
= 10,365,152
```

Malformed lines are preserved in:

``` text
data/processed/parser_errors/parser_errors.log
```

The valid output is:

``` text
data/processed/access_logs/access_logs.parquet
```

------------------------------------------------------------------------

# 13. Phase 2 - Parquet Storage

The structured dataset is stored as Parquet with Snappy compression.

Why Parquet?

-   columnar storage
-   efficient analytical reads
-   typed schema
-   compression
-   column pruning
-   Spark compatibility
-   HDFS compatibility

The resulting structured dataset contains:

``` text
10,365,075 valid records
```

------------------------------------------------------------------------

# 14. Phase 3 - HDFS

The Parquet file is copied to:

``` text
/data/access_logs/access_logs.parquet
```

The Docker Hadoop cluster is:

``` text
node1 → NameNode
node2 → DataNode
node3 → DataNode
```

Architecture:

``` text
                    NameNode
                      node1
                     /     \
                    /       \
                   ▼         ▼
             DataNode      DataNode
               node2         node3
```

HDFS replication factor:

``` text
2
```

The dataset was approximately:

``` text
238 MiB
```

and used two HDFS blocks with replication factor 2.

------------------------------------------------------------------------

# 15. Hadoop Configuration

`core-site.xml`:

``` xml
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://node1:9000</value>
  </property>
</configuration>
```

Relevant `hdfs-site.xml` configuration:

``` xml
<property>
  <name>dfs.replication</name>
  <value>2</value>
</property>
```

Workers:

``` text
node2
node3
```

------------------------------------------------------------------------

# 16. Phase 4 - Spark Cluster

Spark is responsible for distributed analytical computation.

Architecture:

``` text
                 Spark Master
                      |
             +--------+--------+
             |                 |
             ▼                 ▼
        Worker 1          Worker 2
```

Master:

``` text
spark://spark-master:7077
```

Spark UI:

``` text
http://localhost:8080
```

The workers were configured with approximately:

``` text
1536 MB memory each
```

after increasing the initial worker memory configuration.

------------------------------------------------------------------------

# 17. Why Spark?

The project requires operations such as:

-   group by IP
-   five-minute time windows
-   request counting
-   error counting
-   distinct URL counting
-   historical observations
-   median/MAD calculations
-   anomaly classification

These operations are much more representative of distributed data
processing than a simple single-machine script.

------------------------------------------------------------------------

# 18. Phase 5 - Common Analytical Unit

The three detectors use the same basic observation unit:

``` text
IP + 5-minute window
```

For example:

``` text
IP = X

10:00–10:05
10:05–10:10
10:10–10:15
...
```

This converts millions of raw HTTP events into a manageable behavioral
time series for each client.

The final analytical universe contains:

``` text
520,408 IP-window observations
```

for each detector.

------------------------------------------------------------------------

# 19. Traffic Aggregation

Implementation:

``` text
bigdata/spark/transformations/traffic_aggregation.py
```

Output:

``` text
hdfs://node1:9000/data/traffic_aggregation/traffic_5min.parquet
```

Logic:

``` text
Raw requests
      ↓
groupBy(ip, 5-minute window)
      ↓
count(*)
      ↓
request_count
```

Output:

``` text
ip
window_start
window_end
request_count
```

Validation:

``` text
Rows:                 520,408
Invalid request count:      0
Invalid windows:            0
Duplicate IP-window:        0
```

------------------------------------------------------------------------

# 20. Error Rate Aggregation

Implementation:

``` text
bigdata/spark/transformations/error_rate_aggregation.py
```

Output:

``` text
hdfs://node1:9000/data/error_rate_aggregation/error_rate_5min.parquet
```

For every IP/window:

``` text
total_requests
error_requests
error_rate
```

Conceptually:

``` text
error_rate =
    error_requests / total_requests
```

Output:

``` text
ip
window_start
window_end
total_requests
error_requests
error_rate
```

Observed distribution:

``` text
min     = 0
p50     = 0
p75     = 0
p90     = 0
p95     ≈ 0.0667
p99     ≈ 0.8889
p99.9   = 1
max     = 1
```

Validation:

``` text
Rows: 520,408
error_rate ∈ [0, 1]
invalid rows: 0
```

The highly skewed distribution is one reason a robust statistical
approach was chosen.

------------------------------------------------------------------------

# 21. URL Access Aggregation

Implementation:

``` text
bigdata/spark/transformations/url_access_aggregation.py
```

Output:

``` text
hdfs://node1:9000/data/url_access_aggregation/url_access_5min.parquet
```

Logic:

``` text
groupBy(ip, 5-minute window)
        ↓
countDistinct(url)
        ↓
unique_url_count
```

Output:

``` text
ip
window_start
window_end
unique_url_count
```

Distribution:

``` text
min     = 1
p50     = 2
p75     = 19
p90     = 52
p95     = 85
p99     = 186
p99.9   = 348
max     = 918
```

Validation:

``` text
Rows: 520,408
Minimum: 1
Maximum: 918
Invalid count: 0
Duplicate IP-window: 0
```

------------------------------------------------------------------------

# 22. Phase 6 - Statistical Analysis

The system deliberately uses **robust statistics rather than a global
threshold or trained ML model**.

The reason is that web traffic is:

-   highly skewed
-   heavy-tailed
-   heterogeneous across IPs
-   naturally affected by bots/crawlers
-   prone to extreme values

A single global threshold would be poor because:

``` text
IP A:
2, 2, 3, 2, 3

IP B:
100, 120, 110, 130, 125
```

Both are normal relative to their own behavior, even though their
absolute volumes differ greatly.

Therefore the system builds an **IP-specific baseline**.

------------------------------------------------------------------------

# 23. Historical Baseline

For every current observation:

``` text
current IP/window
       ↓
previous five observations of same IP
       ↓
historical baseline
       ↓
compare current value
```

Constants:

``` text
MIN_HISTORY = 5
MAX_HISTORY_AGE_HOURS = 24
ROBUST_Z_THRESHOLD = 3.5
```

The historical baseline requires:

``` text
history_count >= 5
```

and the oldest selected historical observation must be no more than 24
hours old.

------------------------------------------------------------------------

# 24. Median

Given:

``` text
x1, x2, x3, x4, x5
```

the baseline is:

``` text
median(x)
```

Median is used because it is resistant to extreme observations.

Example:

``` text
2, 3, 3, 4, 500
```

Median:

``` text
3
```

The extreme 500 does not significantly distort the baseline.

------------------------------------------------------------------------

# 25. Median Absolute Deviation (MAD)

MAD is:

``` text
MAD = median(|xi - median(x)|)
```

Example:

``` text
values:
2, 3, 3, 4, 5

median = 3

absolute deviations:
1, 0, 0, 1, 2

MAD = 1
```

MAD is useful because the system is itself trying to detect outliers.

------------------------------------------------------------------------

# 26. Robust Z-Score

When:

``` text
MAD > 0
```

the system calculates:

``` text
robust_z_score =
(current_value - baseline_median)
/
(1.4826 × MAD)
```

The anomaly threshold is:

``` text
3.5
```

Therefore:

``` text
robust_z_score >= 3.5
```

means the current value is unusually high relative to the historical
baseline.

------------------------------------------------------------------------

# 27. Zero-MAD Problem

If previous observations are identical:

``` text
10, 10, 10, 10, 10
```

then:

``` text
median = 10
MAD = 0
```

The normal robust Z-score would divide by zero.

Instead of producing infinity or NaN, explicit fallback rules are used.

------------------------------------------------------------------------

# 28. Traffic Spike Detector

Traffic metric:

``` text
request_count
```

When:

``` text
MAD > 0
```

use:

``` text
robust_z_score >= 3.5
```

When:

``` text
MAD = 0
```

use:

``` text
current_request_count >=
max(
    3 × baseline_median,
    baseline_median + 5
)
```

Output fields:

``` text
ip
window_start
window_end
request_count
history_count
baseline_median
mad
history_age_hours
robust_z_score
is_traffic_spike
```

Results:

``` text
Total observations: 520,408
Anomalies:            2,865
Normal:             517,543
Anomaly rate:         ~0.55%
```

------------------------------------------------------------------------

# 29. Error Rate Detector

Metrics:

``` text
error_rate
total_requests
```

Additional minimum volume:

``` text
total_requests >= 5
```

When:

``` text
MAD > 0
```

use:

``` text
robust_z_score >= 3.5
```

When:

``` text
MAD = 0
```

use:

``` text
current_error_rate >=
max(
    3 × baseline_median,
    baseline_median + 0.20
)
```

Output:

``` text
ip
window_start
window_end
total_requests
error_requests
error_rate
history_count
baseline_median
mad
history_age_hours
robust_z_score
is_error_rate_anomaly
```

Results:

``` text
Total observations: 520,408
Anomalies:                680
Normal:               519,728
Anomaly rate:           ~0.13%
```

------------------------------------------------------------------------

# 30. URL Access Detector

Metric:

``` text
unique_url_count
```

When:

``` text
MAD > 0
```

use:

``` text
robust_z_score >= 3.5
```

When:

``` text
MAD = 0
```

use:

``` text
current_unique_url_count >=
max(
    3 × baseline_median,
    baseline_median + 5
)
```

Output:

``` text
ip
window_start
window_end
unique_url_count
history_count
baseline_median
mad
history_age_hours
robust_z_score
is_url_access_anomaly
```

Results:

``` text
Total observations: 520,408
Anomalies:            2,755
Normal:             517,653
```

------------------------------------------------------------------------

# 31. Detector Architecture

All three detectors follow the same conceptual algorithm:

``` text
                 Current IP Window
                         |
                         ▼
              Retrieve previous 5
                 IP observations
                         |
                         ▼
                 history_count >= 5?
                    /          \
                  no            yes
                  |              |
                  ▼              ▼
              Normal       oldest <= 24h?
                                 /    \
                               no      yes
                               |        |
                               ▼        ▼
                            Normal   Calculate
                                     median/MAD
                                        |
                                  +-----+-----+
                                  |           |
                               MAD > 0      MAD = 0
                                  |           |
                                  ▼           ▼
                              Robust Z     Fallback
                                  |           |
                                  +-----+-----+
                                        |
                                        ▼
                              Anomaly / Normal
```

This is the core statistical engine of the project.

------------------------------------------------------------------------

# 32. Detector Results Summary

  Detector            Total Windows   Anomalies          Normal
  ----------------- --------------- ----------- ---------------
  Traffic Spike             520,408       2,865         517,543
  Error Rate                520,408         680         519,728
  URL Access                520,408       2,755         517,653
  **Total flags**     **1,561,224**   **6,300**   **1,554,924**

Overall detector-level anomaly rate:

``` text
6,300 / 1,561,224 × 100
≈ 1.21%
```

> Important: 6,300 is the number of anomaly **flags across three
> detectors**. It does not mean there were 6,300 unique anomalous HTTP
> requests.

------------------------------------------------------------------------

# 33. Phase 7 - MongoDB

Database:

``` text
web_server_anomaly_detection
```

Collections:

``` text
traffic_anomalies
error_rate_anomalies
url_access_anomalies
```

Documents:

``` text
520,408 per collection
1,561,224 total
```

MongoDB is used as the **serving/analytical database** for the backend.
HDFS remains the distributed data-processing storage layer.

------------------------------------------------------------------------

# 34. MongoDB Document Model

Traffic example:

``` json
{
  "ip": "...",
  "window_start": "...",
  "window_end": "...",
  "request_count": 150,
  "history": {
    "count": 5,
    "baseline_median": 10,
    "mad": 2,
    "age_hours": 4.5
  },
  "robust_z_score": 47.23,
  "is_anomaly": true
}
```

Error example:

``` json
{
  "ip": "...",
  "window_start": "...",
  "window_end": "...",
  "total_requests": 100,
  "error_requests": 80,
  "error_rate": 0.8,
  "history": {
    "count": 5,
    "baseline_median": 0.05,
    "mad": 0.02,
    "age_hours": 3.5
  },
  "robust_z_score": 25.3,
  "is_anomaly": true
}
```

URL example:

``` json
{
  "ip": "...",
  "window_start": "...",
  "window_end": "...",
  "unique_url_count": 227,
  "history": {
    "count": 5,
    "baseline_median": 2,
    "mad": 1,
    "age_hours": 4.0
  },
  "robust_z_score": 151.76,
  "is_anomaly": true
}
```

------------------------------------------------------------------------

# 35. MongoDB Indexes

Indexes:

``` text
{ ip: 1, window_start: 1 }
```

and:

``` text
{ is_anomaly: 1, window_start: -1 }
```

Logical observation key:

``` text
IP + window_start
```

These indexes support:

-   IP investigation
-   historical filtering
-   anomaly filtering
-   dashboard queries

------------------------------------------------------------------------

# 36. Spark-to-MongoDB Migration

A custom image was created:

``` text
rishi-spark-mongodb:4.1.3
```

Dockerfile:

``` dockerfile
FROM apache/spark:4.1.3

USER root
RUN pip install --no-cache-dir pymongo==4.18.2
USER spark
```

Migration script:

``` text
bigdata/mongodb/migrate_hdfs_to_mongodb.py
```

The migration:

1.  Reads anomaly Parquet from HDFS.
2.  Processes partitions.
3.  Creates a MongoDB client per Spark partition.
4.  Uses `UpdateOne`.
5.  Uses `upsert=True`.
6.  Writes in batches of approximately 1000.

The full successful migration used:

``` text
Spark local[*]
+
custom PyMongo-enabled Spark image
```

This was done because the normal Spark worker image did not contain
PyMongo.

The distinction is:

``` text
Distributed Spark
      ↓
Feature generation + anomaly detection

Custom Spark local[*]
      ↓
HDFS-to-MongoDB serving-store migration
```

------------------------------------------------------------------------

# 37. MongoDB Backup

A complete database dump was created using MongoDB Database Tools.

Backup:

``` text
E:\mongo-backup\web_server_anomaly_detection.zip
```

Contains:

``` text
traffic_anomalies.bson
error_rate_anomalies.bson
url_access_anomalies.bson
```

Counts:

``` text
traffic_anomalies       520,408
error_rate_anomalies   520,408
url_access_anomalies   520,408
```

Total:

``` text
1,561,224
```

------------------------------------------------------------------------

# 38. Phase 8 - FastAPI Architecture

Backend structure:

``` text
backend/
└── app/
    ├── main.py
    ├── routes/
    │   └── dashboard.py
    ├── services/
    │   ├── database.py
    │   ├── anomaly_service.py
    │   └── investigation_service.py
    ├── models/
    └── utils/
```

Responsibility:

``` text
Route
  ↓
Service
  ↓
MongoDB
```

`anomaly_service.py` contains dashboard summary and trend queries.

`investigation_service.py` contains IP-level investigation queries.

This separation prevents the main anomaly service from becoming a large
monolithic file.

------------------------------------------------------------------------

# 39. Database Connection

The development environment uses:

``` text
Windows MongoDB
        ↑
        │
      WSL
        ↑
        │
FastAPI
```

Connection used:

``` text
mongodb://172.17.176.1:27017/?directConnection=true
```

The `directConnection=true` option is important for this development
topology because the MongoDB replica-set configuration used a
localhost-advertised member while the FastAPI process runs inside WSL.

A production deployment should use proper service hostnames and
replica-set networking rather than relying on this development-specific
arrangement.

------------------------------------------------------------------------

# 40. FastAPI Health Endpoint

``` http
GET /api/health
```

Expected response:

``` json
{
  "status": "ok",
  "database": "connected"
}
```

This provides a simple backend/database health check.

------------------------------------------------------------------------

# 41. API 1 - Dashboard Summary

``` http
GET /api/dashboard/summary
```

Purpose:

> Give the dashboard the overall current state of the analytical system.

Returns:

``` text
total_log_records
total_anomaly_events

traffic_spike
  anomalies
  total_windows
  anomaly_rate

error_rate
  anomalies
  total_windows
  anomaly_rate

url_access
  anomalies
  total_windows
  anomaly_rate

overall_anomaly_rate
```

Current values:

``` text
Raw valid records:       10,365,075
Traffic anomalies:            2,865
Error anomalies:                680
URL anomalies:                2,755
Total anomaly flags:          6,300
Overall detector rate:        ~1.21%
```

------------------------------------------------------------------------

# 42. API 2 - Traffic Trend

``` http
GET /api/dashboard/traffic-trend?range_hours=24
```

Purpose:

> Show how total request traffic changes over a selected historical
> period and where traffic anomaly windows occur.

Supported ranges:

``` text
1h
6h
24h
72h
168h
```

Resolution:

  Range     Resolution
  ------- ------------
  1h             5 min
  6h            15 min
  24h           60 min
  72h          180 min
  168h         360 min

Response:

``` text
data_source
range
interval_minutes
total_requests
anomaly_windows
data[]
```

Each point:

``` text
time
bucket_end
request_count
anomaly_windows
```

Final 24-hour test:

``` text
total_requests:    2,585,739
anomaly_windows:         651
data points:              25
```

Because the dataset is historical, the API anchors the selected range to
the latest timestamp in the dataset.

------------------------------------------------------------------------

# 43. API 3 - Error Rate Trend

``` http
GET /api/dashboard/error-rate-trend?range_hours=24
```

Purpose:

> Show how overall HTTP error behavior changes through time.

Response:

``` text
data_source
range
interval_minutes
total_requests
total_errors
overall_error_rate
anomaly_windows
data[]
```

Each point:

``` text
time
bucket_end
total_requests
error_requests
error_rate
anomaly_windows
```

Final 24-hour test:

``` text
total_requests:       2,585,739
total_errors:            51,865
overall_error_rate:      0.0201
anomaly_windows:             222
data points:                  25
```

------------------------------------------------------------------------

# 44. API 4 - URL Access Trend

``` http
GET /api/dashboard/url-access-trend?range_hours=24
```

Purpose:

> Show how resource-access activity changes through time.

Response:

``` text
data_source
range
interval_minutes
total_unique_url_accesses
anomaly_windows
data[]
```

Each point:

``` text
time
bucket_end
unique_url_accesses
anomaly_windows
```

Important:

``` text
unique_url_accesses
```

is the sum of per-IP unique URL counts over the selected windows.

It is **not** a globally deduplicated count of URLs.

Final 24-hour test:

``` text
total_unique_url_accesses: 2,356,275
anomaly_windows:                 633
data points:                      25
```

------------------------------------------------------------------------

# 45. API 5 - Top Traffic-Anomaly IPs

``` http
GET /api/dashboard/top-traffic-anomaly-ips?range_hours=24&limit=10
```

Purpose:

> Identify the IPs responsible for the largest number of traffic-spike
> anomaly windows.

Supported limits:

``` text
5
10
20
50
```

Each result contains:

``` text
ip
anomaly_count
total_requests
max_request_count
max_robust_z_score
first_anomaly
last_anomaly
```

Sorting:

``` text
anomaly_count DESC
max_robust_z_score DESC
```

Example top result:

``` text
IP: 66.249.66.92
anomaly_count: 17
total_requests: 2777
max_request_count: 379
max_robust_z_score: 83.187...
```

------------------------------------------------------------------------

# 46. API 6 - Top URL-Anomaly IPs

``` http
GET /api/dashboard/top-url-anomaly-ips?range_hours=24&limit=10
```

Purpose:

> Identify IPs responsible for the most unusual URL/resource-access
> activity.

Each result contains:

``` text
ip
anomaly_count
total_unique_url_count
max_unique_url_count
max_robust_z_score
first_anomaly
last_anomaly
```

Sorting:

``` text
anomaly_count DESC
max_robust_z_score DESC
```

Example top result:

``` text
IP: 66.249.66.197
anomaly_count: 16
total_unique_url_count: 324
max_unique_url_count: 58
max_robust_z_score: 17.874
```

------------------------------------------------------------------------

# 47. API-to-Dashboard Mapping

The final dashboard maps exactly to the six APIs:

``` text
API 1
  ↓
Summary Cards

API 2
  ↓
Traffic Trend Chart

API 3
  ↓
Error Rate Trend Chart

API 4
  ↓
URL Access Trend Chart

API 5
  ↓
Top Traffic-Anomaly IP Table

API 6
  ↓
Top URL-Anomaly IP Table
```

This avoids unnecessary API proliferation.

------------------------------------------------------------------------

# 48. Dashboard Architecture

``` text
                    React Dashboard
                           |
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
   Summary              Trends          Investigations
       │                   │                   │
       ▼            ┌──────┼──────┐      ┌────┴────┐
     API 1          API 2  API 3  API 4  API 5   API 6
```

The frontend is intentionally a presentation layer.

Expensive processing stays in:

``` text
Spark
```

and analytical query logic stays in:

``` text
FastAPI services
```

------------------------------------------------------------------------

# 49. Docker Runtime

The distributed environment is simulated on one machine using Docker.

Hadoop:

``` text
apache/hadoop:3.4.3

hadoop-node1 → NameNode
hadoop-node2 → DataNode
hadoop-node3 → DataNode
```

Spark:

``` text
apache/spark:4.1.3

spark-master
spark-worker1
spark-worker2
```

Docker network:

``` text
rishi_bigdata-net
```

This provides:

-   isolated services
-   reproducible node names
-   distributed networking
-   repeatable cluster startup
-   resource configuration
-   realistic master/worker architecture

> This is a simulated distributed cluster on one physical machine. A
> production deployment could place each node on separate hosts or
> Kubernetes workloads.

------------------------------------------------------------------------

# 50. Complete Runtime Diagram

``` text
                    Docker Network
                 rishi_bigdata-net

       Hadoop                           Spark
 ┌───────────────┐               ┌───────────────┐
 │ hadoop-node1  │               │ spark-master  │
 │   NameNode    │               │    :7077      │
 └───────┬───────┘               └───────┬───────┘
         │                               │
   ┌─────┴─────┐                   ┌─────┴─────┐
   ▼           ▼                   ▼           ▼
 node2       node3              worker1     worker2
DataNode    DataNode
```

------------------------------------------------------------------------

# 51. Full Technical Pipeline

``` text
                         RAW DATA
                            │
                            ▼
                 access.log / Nginx
                            │
                            ▼
                  Python streaming parser
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
       Valid records                 Invalid records
             │                             │
             ▼                             ▼
       PyArrow/Parquet              parser_errors.log
             │
             ▼
             HDFS
             │
             ▼
      Spark reads Parquet
             │
     ┌───────┼────────┐
     │       │        │
     ▼       ▼        ▼
 Traffic   Error     URL
 feature   feature   feature
     │       │        │
     └───────┼────────┘
             ▼
    5-minute IP windows
             │
             ▼
   Previous 5 observations
             │
             ▼
        Median + MAD
             │
       ┌─────┴─────┐
       │           │
     MAD > 0     MAD = 0
       │           │
       ▼           ▼
  Robust Z       Fallback
       │           │
       └─────┬─────┘
             ▼
      Anomaly classification
             │
             ▼
          HDFS results
             │
             ▼
      MongoDB migration
             │
             ▼
           MongoDB
             │
             ▼
           FastAPI
             │
             ▼
          React UI
```

------------------------------------------------------------------------

# 52. Validation Strategy

Validation was performed at multiple layers.

## Parser

``` text
total lines
valid lines
invalid lines
success rate
valid + invalid = total
```

## Aggregation

``` text
row count
duplicate IP-window
invalid metrics
invalid windows
```

## Detector

``` text
history_count
history age
robust z-score
anomaly-rule consistency
duplicate IP-window
invalid numerical values
```

## MongoDB

``` text
collection counts
document structure
indexes
migration totals
```

## API

``` text
HTTP status
response schema
range validation
limit validation
database connectivity
```

------------------------------------------------------------------------

# 53. Important Validation Semantics

Some output fields are legitimately null.

For early IP observations:

``` text
history_count < 5
```

there is not enough historical information to calculate:

``` text
baseline_median
mad
robust_z_score
```

Therefore those fields may be null.

This is expected cold-start behavior.

Also:

``` text
history_age_hours > 24
```

can be valid for a normal record.

The 24-hour rule means:

> historical observations older than 24 hours are not eligible as the
> required recent baseline for anomaly classification.

It does not mean every normal record must have a history age less than
24 hours.

------------------------------------------------------------------------

# 54. Performance-Oriented Decisions

## Streaming input

Avoids loading the entire raw dataset into memory.

## Batch Parquet writes

Uses:

``` text
10,000 records per batch
```

during parsing.

## Columnar storage

Parquet reduces unnecessary analytical I/O.

## Distributed processing

Spark distributes aggregation and detection workloads.

## MongoDB indexing

Indexes reduce dashboard query cost.

## Precomputed anomaly results

The frontend does not calculate anomalies.

The expensive work is completed before serving the dashboard.

------------------------------------------------------------------------

# 55. Why Not Use a Global Threshold?

Suppose:

``` text
Global threshold = 100 requests / window
```

Then:

``` text
IP A:
normal = 2–5
current = 110
```

would clearly be suspicious.

But:

``` text
IP B:
normal = 100–150
current = 110
```

would be completely normal.

A global threshold would incorrectly classify IP B.

The project therefore uses:

``` text
IP-specific historical behavior
```

instead.

------------------------------------------------------------------------

# 56. Why Robust Statistics?

Web logs naturally contain:

-   crawlers
-   bots
-   bursts
-   repeated requests
-   large response patterns
-   highly skewed distributions

Mean and standard deviation are easily influenced by these extremes.

Median + MAD provide a more stable baseline.

The detector is therefore:

``` text
explainable
+
robust
+
IP-specific
+
data-driven
```

------------------------------------------------------------------------

# 57. Why 5-Minute Windows?

A window must be:

-   small enough to reveal short bursts
-   large enough to avoid excessive noise

Five minutes is a practical compromise.

It also creates a common time resolution across:

``` text
traffic
error rate
URL access
```

------------------------------------------------------------------------

# 58. Why Previous Five Observations?

The detector needs enough history to estimate normal behavior.

Five observations provide:

``` text
small computational footprint
+
recent behavior
+
robust median/MAD calculation
```

The 24-hour eligibility rule prevents very old observations from
becoming the direct baseline.

------------------------------------------------------------------------

# 59. Security Architecture

During development, MongoDB runs on Windows while FastAPI runs in WSL.

WSL connectivity was enabled through the Windows gateway:

``` text
172.17.176.1
```

A firewall rule was configured for the WSL subnet:

``` text
172.17.176.0/20
```

on MongoDB's port:

``` text
27017
```

Before public deployment, hardening should include:

-   MongoDB authentication
-   TLS
-   restricted bind addresses
-   network segmentation
-   secret management
-   non-root containers
-   API authentication/authorization
-   rate limiting
-   HTTPS
-   secure CORS configuration

The current setup is a controlled development environment, not a public
Internet deployment.

------------------------------------------------------------------------

# 60. Installation Prerequisites

Recommended:

``` text
Linux / WSL
Python 3
Java 17+
Docker
Git
Node.js
MongoDB
```

Host Spark environment:

``` text
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
SPARK_HOME=$HOME/spark
```

Spark:

``` text
4.1.3
```

------------------------------------------------------------------------

# 61. Backend Setup

``` bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install fastapi uvicorn pymongo python-dotenv
```

Run:

``` bash
uvicorn backend.app.main:app --reload
```

Health:

``` http
GET http://127.0.0.1:8000/api/health
```

------------------------------------------------------------------------

# 62. Hadoop Startup

Start the Docker containers.

Then start the daemons where required:

``` bash
docker exec hadoop-node1 bash -c \
  'hdfs --daemon start namenode'

docker exec hadoop-node2 bash -c \
  'hdfs --daemon start datanode'

docker exec hadoop-node3 bash -c \
  'hdfs --daemon start datanode'
```

Verify:

``` bash
jps
```

Expected:

``` text
node1 → NameNode
node2 → DataNode
node3 → DataNode
```

------------------------------------------------------------------------

# 63. Spark Startup

Start:

``` text
spark-master
spark-worker1
spark-worker2
```

Workers should register with:

``` text
spark://spark-master:7077
```

Check the Spark UI:

``` text
http://localhost:8080
```

------------------------------------------------------------------------

# 64. Full Pipeline Execution Order

``` text
1. Put access.log in data/raw/

2. Run parser

3. Validate:
   - valid records
   - invalid records
   - schema

4. Upload Parquet to HDFS

5. Verify HDFS:
   - blocks
   - replication
   - file size

6. Run traffic aggregation

7. Run error-rate aggregation

8. Run URL aggregation

9. Validate all three outputs

10. Run traffic anomaly detection

11. Run error-rate anomaly detection

12. Run URL anomaly detection

13. Validate anomaly outputs

14. Run HDFS → MongoDB migration

15. Validate MongoDB counts and indexes

16. Start FastAPI

17. Test /api/health

18. Test six dashboard APIs

19. Start React frontend

20. Open dashboard
```

------------------------------------------------------------------------

# 65. Git Workflow

Branches:

``` text
main
develop
feature/*
```

Meaning:

``` text
main
  → stable/release

develop
  → integration

feature/*
  → individual implementation
```

Feature development:

``` bash
git checkout -b feature/<feature-name>
```

Commit:

``` bash
git add .
git commit -m "Implement <feature>"
```

Push:

``` bash
git push origin feature/<feature-name>
```

Pull request:

``` text
feature/* → develop
```

Release:

``` text
develop → main
```

This prevents unfinished work from directly entering `main`.

------------------------------------------------------------------------

# 66. Data Exclusion Policy

Large data files should not be committed.

`.gitignore` includes:

``` gitignore
data/raw/*
data/processed/*
data/sample/*
__pycache__/
*.pyc
.venv/
venv/
node_modules/
dist/
build/
.env
.env.*
.vscode/
.idea/
*.log
.DS_Store
Thumbs.db
cluster/hadoop/data/*
```

This keeps the repository source-oriented and avoids committing
multi-gigabyte datasets or generated artifacts.

------------------------------------------------------------------------

# 67. Production-Oriented Improvements

The current implementation is designed to be understandable and
reproducible while following production-oriented separation of concerns.

For an actual production deployment, the next improvements would be:

## Configuration

Move environment-specific settings to environment variables:

``` text
MONGO_URI
MONGO_DATABASE
HDFS_URI
SPARK_MASTER
API_PORT
```

## Secrets

Use:

``` text
Docker secrets
Kubernetes Secrets
Cloud secret manager
```

rather than hard-coded credentials.

## Monitoring

Add:

``` text
Prometheus
Grafana
application logs
Spark metrics
MongoDB monitoring
```

## Deployment

Move from one-machine Docker simulation to:

``` text
Kubernetes
or
real multi-node infrastructure
```

## Streaming

Replace batch ingestion with:

``` text
Nginx
 ↓
Kafka
 ↓
Spark Structured Streaming
 ↓
Anomaly Detection
 ↓
MongoDB
 ↓
FastAPI
 ↓
React
```

------------------------------------------------------------------------

# 68. Current Limitations

## Historical Data

The dataset is historical.

Therefore, a dashboard range such as:

``` text
24 hours
```

means:

``` text
24 hours before the latest timestamp available in the dataset
```

not the current real-world 24-hour period.

------------------------------------------------------------------------

## Single-Machine Cluster Simulation

Hadoop and Spark nodes are separate containers but run on one physical
machine.

This demonstrates distributed architecture, but not physical
server-level fault isolation.

------------------------------------------------------------------------

## Statistical Rather Than ML

The anomaly engine is intentionally statistical.

It does not currently learn:

-   seasonality
-   weekly patterns
-   long-term drift
-   complex multi-feature relationships

------------------------------------------------------------------------

## MongoDB Development Topology

MongoDB currently runs on Windows while the backend runs in WSL.

A production system should use a dedicated internal MongoDB service with
secure networking.

------------------------------------------------------------------------

# 69. Future Extensions

Possible next-generation architecture:

``` text
                 Nginx
                   │
                   ▼
                Kafka
                   │
                   ▼
        Spark Structured Streaming
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Traffic   Errors    URLs
          │        │        │
          └────────┼────────┘
                   ▼
          Online Baselines
                   │
                   ▼
             Anomaly Engine
                   │
          ┌────────┴────────┐
          ▼                 ▼
       MongoDB          Alert System
          │
          ▼
       FastAPI
          │
          ▼
        React
```

Potential detectors:

-   repeated 404 scanning
-   suspicious method usage
-   unusual user-agent behavior
-   response-size anomalies
-   geographic anomalies
-   coordinated IP activity
-   bot detection
-   session-level anomalies
-   clustering-based detection
-   Isolation Forest
-   time-series forecasting
-   online learning

------------------------------------------------------------------------
<!-- 
# 70. Faculty Presentation Explanation

A concise explanation of the complete system:

> We built a Big Data web-server anomaly detection platform. The raw
> Nginx access log contains more than ten million records. We first
> stream-parse the log into typed Parquet records and preserve malformed
> lines separately. The structured data is stored in a three-node Hadoop
> HDFS cluster. Apache Spark then performs distributed five-minute
> IP-level aggregations for request volume, HTTP error rate, and unique
> URL access. For anomaly detection, we do not use a global threshold.
> Instead, each IP is compared against its own previous five
> observations using median and MAD. If MAD is non-zero, we calculate a
> robust Z-score and mark values above 3.5 as anomalies. If MAD is zero,
> explicit fallback thresholds are used. The three detectors generate
> 520,408 observations each. Their results are migrated into MongoDB,
> where indexed analytical documents are served through six FastAPI
> endpoints. React consumes those APIs to visualize summary metrics,
> trends, and top anomalous IPs.

------------------------------------------------------------------------

# 71. Faculty Questions You Should Be Ready For

## Why Hadoop?

Because the project demonstrates distributed storage and replication
through HDFS.

## Why Spark?

Because the computational workload involves large-scale aggregation and
historical analysis.

## Why Parquet?

Because it is a compressed columnar format optimized for analytics.

## Why MongoDB after HDFS?

HDFS is optimized for distributed data storage and batch processing.
MongoDB is used as the application-facing serving store for dashboard
queries.

## Why not query HDFS directly from FastAPI?

That would couple the API to the distributed processing/storage layer
and make interactive dashboard queries less suitable. Precomputed
analytical results in MongoDB provide a cleaner serving layer.

## Why not machine learning?

The project focuses on Big Data engineering and explainable anomaly
detection. Robust statistics provide an auditable baseline without
requiring labeled training data.

## Why median/MAD?

Because web traffic is skewed and contains outliers. Median and MAD are
robust against extreme values.

## Why IP-specific history?

Because different clients have different normal traffic levels.

## Why five observations?

It provides a small recent baseline while keeping the computation
manageable.

## Why five-minute windows?

It balances temporal resolution and noise.

## What happens when MAD is zero?

A fallback rule is used instead of dividing by zero.

## What does 6,300 anomalies mean?

It is the total number of anomaly flags produced by three independent
detectors, not 6,300 unique raw HTTP requests. -->

------------------------------------------------------------------------

# 70. Final Project Metrics

## Raw Dataset

``` text
Raw records:             10,365,152
Valid records:            10,365,075
Invalid records:                 77
Success rate:             ~99.99926%
```

## Feature Windows

``` text
Traffic windows:             520,408
Error-rate windows:          520,408
URL windows:                 520,408
```

## Anomalies

``` text
Traffic spike:                 2,865
HTTP error rate:                 680
URL access:                    2,755
------------------------------------
Total anomaly flags:           6,300
```

## MongoDB

``` text
traffic_anomalies:           520,408
error_rate_anomalies:        520,408
url_access_anomalies:        520,408
--------------------------------------
Total documents:           1,561,224
```

## APIs

``` text
6 dashboard APIs
```

------------------------------------------------------------------------

# 71. Final Architecture in One Diagram

``` text
┌─────────────────────────────────────────────────────────────────┐
│                         WEB SERVER LOGS                          │
│                                                                 │
│                    ~10.3M Nginx records                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMING PARSER                            │
│                                                                 │
│  Regex → typed fields → batch of 10,000 → Parquet              │
│                                                                 │
│  Invalid lines → parser_errors.log                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         HDFS                                    │
│                                                                 │
│   NameNode ───────────── DataNode ───────────── DataNode        │
│                                                                 │
│                  Replication factor = 2                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SPARK                                  │
│                                                                 │
│ Master ───────── Worker 1 ───────── Worker 2                    │
│                                                                 │
│       Distributed aggregation + statistical processing          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       Traffic metric     Error metric      URL metric
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ROBUST ANOMALY ENGINE                          │
│                                                                 │
│ Previous 5 observations                                         │
│          ↓                                                      │
│ IP-specific median + MAD                                        │
│          ↓                                                      │
│ Robust Z-score / zero-MAD fallback                              │
│          ↓                                                      │
│ Anomaly classification                                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MONGODB                                │
│                                                                 │
│ traffic_anomalies | error_rate_anomalies | url_access_anomalies│
│                                                                 │
│                         1.56M documents                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FASTAPI                                 │
│                                                                 │
│ Summary | Traffic | Error | URL | Top Traffic IPs | Top URL IPs│
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         REACT                                  │
│                                                                 │
│ KPI Cards | Trend Charts | Anomaly Tables | Filters             │
└─────────────────────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 72. Conclusion

This project is a complete Big Data application rather than an isolated
anomaly-detection script.

The complete transformation is:

``` text
Raw events
   ↓
Structured events
   ↓
Distributed storage
   ↓
Distributed processing
   ↓
Behavioral windows
   ↓
Historical statistical baselines
   ↓
Anomaly flags
   ↓
Analytical documents
   ↓
REST APIs
   ↓
Dashboard
```

The key engineering idea is the separation of responsibilities:

``` text
Python       → ingestion and parsing
Parquet      → efficient structured storage
HDFS         → distributed storage
Spark        → distributed computation
Statistics   → explainable anomaly detection
MongoDB      → analytical serving layer
FastAPI      → application/API layer
React        → visualization layer
Docker       → reproducible distributed runtime
Git          → controlled collaboration
```

This architecture makes the system easier to explain, test, reproduce,
extend, and eventually migrate from a university-scale implementation
into a real production-style data platform.

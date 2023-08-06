# Aggregated names
AGG_METRICS = "metrics.csv"
CHECK_TYPE_METRICS = "metrics"
CHECK_TYPE_PARAMS = "params"
API_DATA_DIR_NAME = "api_data"

COL_NODE = "node_id"
COL_TIMESTAMP = "agg_timestamp"
COL_NODE_WEIGHT = "node_weight"
COL_ROUND = "round"

# Dataset
ANNOTATION_NAME = "annotation.csv"
COL_DATA_ID = "data_id"
COL_LABEL = "label"
COL_DATA_PATH = "data_path"
COL_ANNOTATION_PATH = "annotation_path"
ANNOTATION_HEADER = [COL_DATA_ID, COL_LABEL, COL_DATA_PATH, COL_ANNOTATION_PATH]
DATASET_TYPE = {
    0: "No annotation file.",
    1: f"Annotation file with headers: {ANNOTATION_HEADER}"
}

# eda result name
EDA_FILENAME = "eda.json"

# Directory to place self-defined classes of aggregation
AGG_CLASSES_DIR = "./aggregate_classes"


# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from foxtail_trainer_api.api.data_set_chunk_api import DataSetChunkApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from foxtail_trainer_api.api.data_set_chunk_api import DataSetChunkApi
from foxtail_trainer_api.api.job_api import JobApi
from foxtail_trainer_api.api.ml_model_api import MLModelApi
from foxtail_trainer_api.api.ml_model_with_training_result_api import MLModelWithTrainingResultApi
from foxtail_trainer_api.api.prediction_task_api import PredictionTaskApi
from foxtail_trainer_api.api.report_api import ReportApi
from foxtail_trainer_api.api.training_config_api import TrainingConfigApi
from foxtail_trainer_api.api.training_result_api import TrainingResultApi
from foxtail_trainer_api.api.worker_api import WorkerApi

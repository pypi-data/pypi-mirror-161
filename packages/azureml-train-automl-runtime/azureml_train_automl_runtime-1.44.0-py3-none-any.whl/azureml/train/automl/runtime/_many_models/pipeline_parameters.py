# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Dict, Union
from abc import ABC
from azureml.automl.core.shared.exceptions import ConfigException
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import DNNNotSupportedForManyModel
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.train.automl.automlconfig import AutoMLConfig


logger = logging.getLogger(__name__)


class TrainPipelineParameters(ABC):

    _MIN_TIMEOUT_DIFF = 300

    def __init__(self, automl_settings: Union[AutoMLConfig, Dict[str, Any]]):
        if isinstance(automl_settings, AutoMLConfig):
            self.automl_settings = automl_settings.as_serializable_dict()
            self.automl_settings["task"] = self.automl_settings.pop("task_type")
        else:
            self.automl_settings = automl_settings
            message = "Please use 'AutoMLConfig' class with 'ForecastingParameters' class to define "\
                      "'automl_settings' instead of directly supplying 'automl_settings' dictionary "\
                      "in '{}' class.".format(type(self).__name__)
            logger.warning(message)

    def validate(self, run_invocation_timeout):
        if self.automl_settings.get("enable_dnn", False):
            raise ConfigException._with_error(
                AzureMLError.create(
                    DNNNotSupportedForManyModel,
                    reference_code=ReferenceCodes._VALIDATE_DNN_ENABLED_MANY_MODELS))
        if "experiment_timeout_hours" not in self.automl_settings:
            self.automl_settings["experiment_timeout_hours"] = round((
                run_invocation_timeout - self._MIN_TIMEOUT_DIFF) / 3600, 2)
            message = "As the experiment_timeout_hours must be smaller than run_invocation_timeout - "\
                      "{}, we have set the value to {} automatically as we didn't find it in the settings.".\
                      format(self._MIN_TIMEOUT_DIFF, self.automl_settings["experiment_timeout_hours"])
            logger.warning(message)


class InferencePipelineParameters(ABC):
    def __init__(self):
        pass

    def validate(self):
        pass

"""
model.py
====================================
Abstract Base Class Model Class used for Risk & Impactability Models
"""
from abc import ABC
from datetime import datetime

from logzero import logger
from pandas import DataFrame
from validation_decorators import ValidateArgType
from validation_decorators.errors import raise_error
import tempfile

from curia.api.swagger_client import Model

type_validator = ValidateArgType(raise_error, logger=logger)


class _Model(ABC):

    def __init__(
            self,
            session,
            name: str,
            description: str = None,
            model_type: str = None,
            model_id: str = None,
            model_dataset_id: str = None,
            project_id: str = None,
            environment_id: str = None,
            last_train_model_dataset_id: str = None,
    ):

        self.session = session

        self.name = name
        self.description = description
        self.feature_store = 'byod'

        self.model_type = model_type
        self.model_id = model_id
        self.model_dataset_id = model_dataset_id
        self.project_id = project_id
        self.environment_id = environment_id
        self.last_train_model_dataset_id = last_train_model_dataset_id

        self._job_type = None

    def set_name(self, name: str):
        """

        Parameters
        ----------
        name: str :
            

        Returns
        -------

        """

        self.session.logger.debug(name)
        self.name = name

    def set_description(self, description: str):
        """

        Parameters
        ----------
        description: str :
            

        Returns
        -------

        """

        self.session.logger.debug(description)
        self.description = description

    def set_model_id(self, model_id: str):
        """

        Parameters
        ----------
        model_id: str :
            

        Returns
        -------

        """

        self.session.logger.debug(model_id)
        self.model_id = model_id

    def set_model_dataset_id(self, model_dataset_id: str):
        """

        Parameters
        ----------
        model_dataset_id: str :
            

        Returns
        -------

        """

        self.session.logger.debug(model_dataset_id)
        self.model_dataset_id = model_dataset_id

    def set_project_id(self, project_id: str):
        """

        Parameters
        ----------
        project_id: str :
            

        Returns
        -------

        """

        self.session.logger.debug(project_id)
        self.project_id = project_id

    def set_environment_id(self, environment_id: str):
        """

        Parameters
        ----------
        environment_id: str :
            

        Returns
        -------

        """

        self.session.logger.debug(environment_id)
        self.environment_id = environment_id

    def set_job_type(self, job_type: str):
        """

        Parameters
        ----------
        job_type: str :
            

        Returns
        -------

        """

        self.session.logger.debug(job_type)
        self._job_type = job_type

    @type_validator(data=DataFrame)
    def model_dataset_upload(self, data: DataFrame):
        """

        Parameters
        ----------
        data: DataFrame :
            

        Returns
        -------

        """

        self.session.logger.info('uploading DataFrame with shape %s', data.shape)
        if self.model_id is None:
            model: Model = self.session.api_instance.create_one_base_model_controller_model(
                self.session.api_client.Model(
                    name=self.name,
                    type=self.model_type,
                    feature_store=self.feature_store,
                    description=self.description,
                    project_id=self.project_id
                )
            )
        else:
            model = self.session.api_instance.get_one_base_model_controller_model(self.model_id)

        self.session.logger.info('created new model: %s', model)
        self.model_id = model.id

        dataset = self.session.api_instance.create_one_base_dataset_controller_dataset(
            self.session.api_client.Dataset(
                name=f'{self.model_id}-{self._job_type}-{datetime.now()}',
                description='BYOD train dataset uploaded via curia-python-sdk',
                type=self._job_type,
                file_size=int(data.memory_usage(index=False).sum()),
                dataset_results={}
            )
        )

        self.session.logger.info('dataset data: %s', dataset)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            data.to_csv(temp, chunksize=1000)
        self.session.api_instance.dataset_controller_upload(
            temp.name,
            dataset.id
        )
        self.session.logger.info('upload successful')

        model_dataset = self.session.api_instance.create_one_base_model_dataset_controller_model_dataset(
            self.session.api_client.ModelDataset(
                dataset_id=dataset.id,
                model_id=self.model_id,
                train_model_dataset_id=self.last_train_model_dataset_id if self._job_type == 'predict' else None
            )
        )
        if self._job_type == 'train':
            self.last_train_model_dataset_id = model_dataset.id
        self.session.logger.info('created model dataset: %s', model_dataset)

        self.model_dataset_id = model_dataset.id

        return model_dataset

    def start(self):
        """Start the model job"""
        self.session.logger.info(
            'starting model job: type=%s modelDatasetId=%s environmentId=%s projectId=%s',
            self._job_type,
            self.model_dataset_id,
            self.environment_id,
            self.project_id
        )
        model_job = self.session.api_instance.create_one_base_model_job_controller_model_job(body={
            'type': self._job_type,
            'modelDatasetId': self.model_dataset_id,
            'environmentId': self.environment_id,
            'projectId': self.project_id
        })
        self.session.logger.info('model job created: %s', model_job)

        self.session.api_instance.model_job_controller_start(model_job.id, type=self._job_type)
        self.session.logger.info('model job started')

    def status(self):
        """Check the model job status"""
        self.session.logger.info(
            'checking model job status: model_id=%s job_type=%s',
            self.model_id,
            self._job_type,
        )
        return self.session.api_instance.get_one_base_model_controller_model(self.model_id, self._job_type)

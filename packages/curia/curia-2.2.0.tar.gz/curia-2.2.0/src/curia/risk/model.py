from logzero import logger
from pandas import DataFrame, Series
from validation_decorators import ValidateArgType
from validation_decorators.errors import raise_error

from curia.model import _Model
from curia.session import Session

type_validator = ValidateArgType(raise_error, logger=logger)


class RiskModel(_Model):
    """Create a Curia risk model"""

    @type_validator(session=Session, name=str)
    def __init__(
            self,
            session,
            name: str,
            description: str = None,
            project_id: str = None,
            environment_id: str = None,
    ):

        self.session = session
        self.model_id = None
        self.model_type = 'risk'

        super().__init__(
            session=self.session,
            name=name,
            description=description,
            project_id=project_id,
            environment_id=environment_id,
            model_type=self.model_type,
        )

    @type_validator(features=DataFrame, label=Series)
    def train(self, features: DataFrame, label: Series):
        """

        Parameters
        ----------
        features: DataFrame :
            
        label: Series :
            

        Returns
        -------

        """

        df = features.copy()
        df['label'] = label

        self.set_job_type('train')

        self.model_dataset_upload(df)

        self.start()

        # TODO - how to handle wait=True param (check status every n seconds)

    @type_validator(features=DataFrame)
    def predict(self, features: DataFrame):
        """

        Parameters
        ----------
        features: DataFrame :
            

        Returns
        -------

        """

        df = features.copy()

        self.set_job_type('predict')

        self.model_dataset_upload(df)

        self.start()

        # TODO - how to handle wait=True param (check status every n seconds)

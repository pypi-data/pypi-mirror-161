from logzero import logger
from pandas import DataFrame, Series
from validation_decorators import ValidateArgType
from validation_decorators.errors import raise_error

from curia.model import _Model
from curia.session import Session

type_validator = ValidateArgType(raise_error, logger=logger)


class ImpactabilityModel(_Model):
    """Create a Curia impactability model"""

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
        self.model_type = 'impactability'

        super().__init__(
            session=self.session,
            name=self.name,
            description=self.description,
            project_id=self.project_id,
            environment_id=self.environment_id,
            model_type=self.model_type,

        )

    @type_validator(features=DataFrame, label=Series, treatment=Series)
    def train(self, features: DataFrame, label: Series, treatment: Series):
        """

        Parameters
        ----------
        features: DataFrame :
            
        label: Series :
            
        treatment: Series :
            

        Returns
        -------

        """

        df = features.copy()
        df['label'] = label
        df['treatment'] = treatment

        self.set_job_type('train')

        self.model_dataset_upload(df)

        self.start()

        # TODO - how to handle wait=True param (check status every n seconds)

    @type_validator(features=DataFrame, treatment=Series)
    def predict(self, features: DataFrame, treatment: Series):
        """

        Parameters
        ----------
        features: DataFrame :
            
        treatment: Series :
            

        Returns
        -------

        """

        df = features.copy()
        df['treatment'] = treatment

        self.set_job_type('predict')

        self.model_dataset_upload(features)

        self.start()

        # TODO - how to handle wait=True param (check status every n seconds)

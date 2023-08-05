import abc
import functools
import time

from curia.session import Session
from curia.utils.string import to_camel_case


class JobInterface(abc.ABC):
    _METHOD_PATTERNS = {
        "get": "get_one_base_{0}_controller_{0}",
        "start": "{0}_controller_start",
        "stop": "{0}_controller_stop"
    }
    SUPPORTED_FUNCTIONS = list(_METHOD_PATTERNS.keys())

    SUPPORTED_AUTOVARIANTS = ['model_job', 'model_batch_job', 'analysis_job', 'process_job', 'dataset_job']

    def __init__(self, session: Session):
        self.session = session

    def run(self, job_id, timeout=3600, interval=5):
        self.start(job_id)
        start_time = time.time()
        while True:
            if time.time() >= timeout + start_time:
                raise TimeoutError(f"Run operation timed out after {timeout} seconds")
            time.sleep(interval)
            job = self.get(job_id)
            status = job.status
            if status != "RUNNING":
                return job

    @abc.abstractmethod
    def get(self, job_id):
        pass

    @abc.abstractmethod
    def start(self, job_id):
        pass

    @abc.abstractmethod
    def stop(self, job_id):
        pass

    @classmethod
    def functionality_builder(cls, job_type_stub, function):
        def handler(self, job_id):
            return getattr(self.session.api_instance, cls._METHOD_PATTERNS[function].format(job_type_stub))(id=job_id)
        return handler

    @classmethod
    @functools.lru_cache(maxsize=None)
    def auto_variant(cls, job_type_stub):
        assert job_type_stub in cls.SUPPORTED_AUTOVARIANTS
        return type(
            f"{to_camel_case(job_type_stub).capitalize()}Interface",
            (cls,),
            {
                function: cls.functionality_builder(job_type_stub, function)
                for function in cls.SUPPORTED_FUNCTIONS
            }
        )


def get_interface(session: Session, job_type_stub: str = None, **kwargs) -> JobInterface:
    """
    :param session: Curia Session object to construct the interface around
    :param job_type_stub: Optional parameter specifying the job type stub to use.
    :param kwargs: Keyword arguments mapping job type stubs to boolean values. The first job_type_stub mapped to a
    truthy value will be used.
    :return: Instantiated JobInterface

    Example (the following are equivalent)::

        job_interface = get_interface(session, job_type_stub="model_job")

        job_interface = get_interface(session, model_job=True)

        job_interface = get_interface(session, model_job="2198302")

        job_interface = get_interface(session, model_job="2198302", process_job=False)

        job_interface = get_interface(session, model_job="2198302", process_job=0)

    The following examples of invalid configuration since they have undefined behavior::

        job_interface = get_interface(session, job_type_stub="model_job", model_job=True)

        job_interface = get_interface(session, job_type_stub="model_job", process_job="2198302")

        job_interface = get_interface(session)

        job_interface = get_interface(session, job_type_stub=None)

        job_interface = get_interface(session, process_job=None)

    """
    truthy_keys = [key for key, value in kwargs.items() if value]
    if job_type_stub is None:
        if len(truthy_keys) == 0:
            raise ValueError("No job_type_stub provided and no non-none job_type_stub kwargs provided!")
        if len(truthy_keys) > 1:
            truthy_keys_to_values = {key: kwargs[key] for key in truthy_keys}
            raise ValueError(f"No job_type_stub provided but multiple truthy job_type_stub kwargs provided! "
                             f"({truthy_keys_to_values})")
        job_type_stub: str = truthy_keys[0]
    else:
        if len(truthy_keys) > 0:
            truthy_keys_to_values = {key: kwargs[key] for key in truthy_keys}
            raise ValueError(f"job_type_stub provided and truthy job_type_stub kwargs also provided!"
                             f"(job_type_stub={job_type_stub}, truthy kwargs={truthy_keys_to_values})")
    variant: type = JobInterface.auto_variant(job_type_stub)
    return variant(session)


ModelJobInterface = JobInterface.auto_variant("model_job")
ModelBatchJobInterface = JobInterface.auto_variant("model_batch_job")
AnalysisJobInterface = JobInterface.auto_variant("analysis_job")
ProcessJobInterface = JobInterface.auto_variant("process_job")
DatasetJobInterface = JobInterface.auto_variant("dataset_job")

from curia.api.swagger_client import Dataset
from curia.session import Session
from curia.utils.s3 import s3_listdir, get_metadata


def create_dataset_from_s3_path(
        session: Session,
        dataset_type: str,
        dataset_name: str,
        file_type: str,
        description: str,
        s3_path: str,
        addtl_dataset_kwargs: dict = None):
    if addtl_dataset_kwargs is None:
        addtl_dataset_kwargs = {}
    object_locations = s3_listdir(s3_path)
    content_length = 0
    metadata = None
    for sub_object in object_locations:
        metadata = get_metadata(sub_object)
        content_length += metadata["ContentLength"]
    dataset = session.api_instance.create_one_base_dataset_controller_dataset(
        Dataset(
            name=dataset_name,
            description=description,
            type=dataset_type,
            file_type=file_type,
            location=s3_path,
            file_content_type=metadata["ContentType"],
            file_size=str(content_length),
            **addtl_dataset_kwargs
        )
    )

    return dataset

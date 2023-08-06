from google.cloud import aiplatform
from typing import Sequence


def get_image_dataset(
    dataset_id: str,
    project: str = "capturpwa",
    location: str = "us-central1"
) -> aiplatform.ImageDataset:
    aiplatform.init(project=project, location=location)
    ds = aiplatform.ImageDataset(dataset_id)
    return ds


def export_data_files(dataset: aiplatform.ImageDataset, output_dir: str) -> Sequence[str]:
    data_files = dataset.export_data(output_dir=output_dir)
    return data_files


class AIPlatformImageDataset():
    def __init__(self, dataset_id: str, project: str = "capturpwa", location: str = "us-central1"):
        self.dataset_id = dataset_id
        self.project = project
        self.location = location

    def get_dataset(self) -> aiplatform.ImageDataset:
        aiplatform.init(project=self.project, location=self.location)
        ds = aiplatform.ImageDataset(self.dataset_id)
        return ds

    def export_data_files(self, output_dir: str) -> Sequence[str]:
        ds = self.get_dataset()
        data_files = ds.export_data(output_dir=output_dir)
        return data_files

from undeepvo.utils import DatasetManager
from undeepvo.data.supervised import GroundTruthDataset, MonoDepthDataset, DataTransformManager
from torch.utils.data import DataLoader, random_split


class SupervisedDatasetManager(DatasetManager):
    def __init__(self, dataset: GroundTruthDataset, num_workers=4, lenghts=(80, 10, 10), final_img_size=(128, 384),
                 transform_params={"filters": True, "normalize": False}):
        dataset = MonoDepthDataset(dataset=dataset)
        train, val, test = random_split(dataset, lenghts)
        self._num_workers = num_workers
        super().__init__(train, val, test)
        self._transform = DataTransformManager(self._train_dataset.dataset.get_image_size(), final_img_size,
                                               transform_params)

    def get_train_batches(self, batch_size):
        self._train_dataset.dataset.set_transform(self._transform.get_train_transform())
        return DataLoader(self._train_dataset, batch_size=batch_size, shuffle=True, num_workers=self._num_workers)

    def get_validation_batches(self, batch_size, with_normalize=False):
        self._validation_dataset.dataset.set_transform(
            self._transform.get_validation_transform(with_normalize=with_normalize))
        return DataLoader(self._validation_dataset, batch_size=batch_size, shuffle=False, num_workers=self._num_workers)

    def get_test_batches(self, batch_size, with_normalize=False):
        self._test_dataset.dataset.set_transform(self._transform.get_test_transform(with_normalize=with_normalize))
        return DataLoader(self._test_dataset, batch_size=batch_size, shuffle=False, num_workers=self._num_workers)

    def get_validation_dataset(self, with_normalize=False):
        self._validation_dataset.dataset.set_transform(
            self._transform.get_validation_transform(with_normalize=with_normalize))
        return self._validation_dataset

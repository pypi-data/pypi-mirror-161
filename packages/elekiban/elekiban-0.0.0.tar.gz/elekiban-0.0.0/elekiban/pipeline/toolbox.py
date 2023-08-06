from abc import ABCMeta, abstractmethod
import random
from xml.dom import ValidationErr


class AbstractFaucet(metaclass=ABCMeta):
    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _turn_on(self, indices):
        pass

    @abstractmethod
    def turn_on(self, indices):
        pass

    @abstractmethod
    def get_output_names(self, indices):
        pass


class SimpleFaucet:
    def __init__(self, input_pipelines: list, output_pipelines: list, batch_size: int) -> None:
        self._pipelines = {"x": input_pipelines, "y": output_pipelines}
        self.batch_size = batch_size
        self._setup()

    def _setup(self):
        data_nums = {}
        for i_pipeline in self._pipelines["x"] + self._pipelines["y"]:
            data_nums[i_pipeline.pipeline_name] = i_pipeline.data_num

        if len(set(data_nums.values())) != 1:
            raise ValidationErr(f"dataset nums should be equal for all dataset. {data_nums}")
        else:
            print(f"dataset num are same for all dataset.{data_nums}")
            data_num = list(set(data_nums.values()))[0]
            self.iteration = int(data_num / self.batch_size)
            self._indices = list(range(data_num))
            pass

    def _turn_on(self, key, remained_indices):
        return {p.pipeline_name: p.generate(remained_indices[:self.batch_size]) for p in self._pipelines[key]}

    def turn_on(self) -> dict:
        while True:
            random.shuffle(self._indices)
            remained_indices = self._indices
            for _ in range(self.iteration):
                yield [self._turn_on("x", remained_indices), self._turn_on("y", remained_indices)]
                remained_indices = remained_indices[:self.batch_size]

    def get_output_names(self):
        return [i_pipeline.pipeline_name for i_pipeline in self._pipelines["y"]]

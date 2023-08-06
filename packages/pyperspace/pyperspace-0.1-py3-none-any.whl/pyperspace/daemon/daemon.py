from .dataset import HybridDataSet
from pyperspace.workers import DataSetWorkerPool, StorageManagerWorker, TCP_MODE, TCP_FAST_MODE, PIPE_MODE
from pyperspace.storage import LSMDataSet, StorageManagerClient
from typing import List

class DataSetConfig:
    def __init__(self, **kwargs):
        self.mode = TCP_MODE
        self.num_nodes = 3
        self.insert_buffer_size = 100
        self.select_buffer_size = 100000
        self.freeze_limit = 5000
        self.acknowledge = False
        self.flush = True

        for key, value in kwargs.items():
            setattr(self, key, value)

class StorageConfig:
    def __init__(self, **kwargs):
        self.cycle_time = 5

        for key, value in kwargs.items():
            setattr(self, key, value)

class Daemon(DataSetWorkerPool):
    def __init__(self, path: str, ds_cfg: DataSetConfig, sm_cfg: StorageConfig):
        # Start StorageManagerWorker to get the port for DataSetWorkerPool
        self._sm = StorageManagerWorker(path, sm_cfg.cycle_time)
        self._sm.start()
        super().__init__(self._sm.listener_port, \
                         ds_cfg.mode, \
                         path, \
                         ds_cfg.num_nodes, \
                         ds_cfg.insert_buffer_size, \
                         ds_cfg.select_buffer_size, \
                         ds_cfg.freeze_limit, \
                         ds_cfg.acknowledge, \
                         ds_cfg.flush)
        self._sm_client = StorageManagerClient(self._sm.listener_port)

    @property
    def storage(self) -> StorageManagerClient:
        return self._sm_client

    def get_dataset_names(self) -> List[str]:
        res = self._sm_client.list_datasets()
        return list(res.DataSets.names)

    def open_lsm_dataset(self, name: str) -> HybridDataSet:
        return HybridDataSet(self, name, self._sm.listener_port)

    def stop(self) -> None:
        super().stop()
        super().join()
        self._sm_client.close()
        self._sm.stop()
        self._sm.join()

    def close(self) -> None:
        super().close()
        self._sm.close()

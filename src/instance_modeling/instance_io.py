from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class WorkflowInstance:
    num_tasks: int
    num_configs: int
    num_data: int
    num_vms: int
    num_buckets: int
    num_bucket_ranges: int
    max_running_time: float
    max_financial_cost: float


@dataclass
class TaskRow:
    task_id: str
    activity_id: int
    task_type: int
    vm_cpu_time: float
    n_input: int
    input_ids: List[str]
    n_output: int
    output_ids: List[str]


@dataclass
class DataRow:
    data_id: str
    data_size_bytes: int
    read_time_avg: Optional[float]
    write_time_avg: Optional[float]
    is_static: int
    n_source_devices: int
    device_ids: List[str]


@dataclass
class VmRow:
    vm_id: str
    cpu_slowdown: float
    cost_per_second: float
    storage_bytes: int
    bandwidth_mbps: float


@dataclass
class ConfigRow:
    task_id: str
    activity_id: int
    conf_id: int
    task_cost: float
    task_time_duration: float
    task_time_init: float
    task_time_cpu: float
    task_time_read: float
    task_time_write: float
    task_count: int


@dataclass
class BucketRangeRow:
    bucket_range_id: str
    size1_bytes: int
    size2_bytes: int
    cost_per_byte: float


@dataclass
class ParsedInstance:
    file_path: Path
    header: WorkflowInstance
    tasks: List[TaskRow]
    data: List[DataRow]
    vms: List[VmRow]
    configs: List[ConfigRow]
    bucket_ranges: List[BucketRangeRow]


class InstanceParser:
    SECTION_TASK = "#<task_id> <activity_id> <task_type__0-VM__1-VM_FX>"
    SECTION_DATA = "#<data_id>"
    SECTION_VM = "#<vm_id>"
    SECTION_CONFIG = "#<task_id> <activity_id> <conf_id>"
    SECTION_BUCKET = "#<bucket_range_id>"

    @staticmethod
    def parse_file(path: Path) -> ParsedInstance:
        with path.open("r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        header_values = lines[1].split("\t")
        header = WorkflowInstance(
            num_tasks=int(header_values[0]),
            num_configs=int(header_values[1]),
            num_data=int(header_values[2]),
            num_vms=int(header_values[3]),
            num_buckets=int(header_values[4]),
            num_bucket_ranges=int(header_values[5]),
            max_running_time=float(header_values[6]),
            max_financial_cost=float(header_values[7]),
        )

        idx_task = InstanceParser._find_idx(lines, InstanceParser.SECTION_TASK)
        idx_data = InstanceParser._find_idx(lines, InstanceParser.SECTION_DATA)
        idx_vm = InstanceParser._find_idx(lines, InstanceParser.SECTION_VM)
        idx_config = InstanceParser._find_idx(lines, InstanceParser.SECTION_CONFIG)
        idx_bucket = InstanceParser._find_idx(lines, InstanceParser.SECTION_BUCKET)

        task_lines = lines[idx_task + 1 : idx_data]
        data_lines = lines[idx_data + 1 : idx_vm]
        vm_lines = lines[idx_vm + 1 : idx_config]
        config_lines = lines[idx_config + 1 : idx_bucket]
        bucket_lines = lines[idx_bucket + 1 :]

        return ParsedInstance(
            file_path=path,
            header=header,
            tasks=[InstanceParser._parse_task(x) for x in task_lines],
            data=[InstanceParser._parse_data(x) for x in data_lines],
            vms=[InstanceParser._parse_vm(x) for x in vm_lines],
            configs=[InstanceParser._parse_config(x) for x in config_lines],
            bucket_ranges=[InstanceParser._parse_bucket(x) for x in bucket_lines],
        )

    @staticmethod
    def _find_idx(lines: List[str], marker: str) -> int:
        for i, line in enumerate(lines):
            if line.startswith(marker):
                return i
        raise ValueError(f"Section not found: {marker}")

    @staticmethod
    def _parse_list(raw: str) -> List[str]:
        raw = raw.strip()
        if not (raw.startswith("[") and raw.endswith("]")):
            return []
        return [x.strip() for x in raw[1:-1].split(",") if x.strip()]

    @staticmethod
    def _parse_optional_float(raw: str) -> Optional[float]:
        if raw.lower() == "none":
            return None
        return float(raw)

    @staticmethod
    def _parse_task(line: str) -> TaskRow:
        cols = line.split("\t")
        return TaskRow(
            task_id=cols[0],
            activity_id=int(cols[1]),
            task_type=int(cols[2]),
            vm_cpu_time=float(cols[3]),
            n_input=int(cols[4]),
            input_ids=InstanceParser._parse_list(cols[5]),
            n_output=int(cols[6]),
            output_ids=InstanceParser._parse_list(cols[7]),
        )

    @staticmethod
    def _parse_data(line: str) -> DataRow:
        cols = line.split("\t")
        return DataRow(
            data_id=cols[0],
            data_size_bytes=int(float(cols[1])),
            read_time_avg=InstanceParser._parse_optional_float(cols[2]),
            write_time_avg=InstanceParser._parse_optional_float(cols[3]),
            is_static=int(cols[4]),
            n_source_devices=int(cols[5]),
            device_ids=InstanceParser._parse_list(cols[6]),
        )

    @staticmethod
    def _parse_vm(line: str) -> VmRow:
        cols = line.split("\t")
        return VmRow(
            vm_id=cols[0],
            cpu_slowdown=float(cols[1]),
            cost_per_second=float(cols[2]),
            storage_bytes=int(float(cols[3])),
            bandwidth_mbps=float(cols[4]),
        )

    @staticmethod
    def _parse_config(line: str) -> ConfigRow:
        cols = line.split("\t")
        return ConfigRow(
            task_id=cols[0],
            activity_id=int(cols[1]),
            conf_id=int(cols[2]),
            task_cost=float(cols[3]),
            task_time_duration=float(cols[4]),
            task_time_init=float(cols[5]),
            task_time_cpu=float(cols[6]),
            task_time_read=float(cols[7]),
            task_time_write=float(cols[8]),
            task_count=int(cols[9]),
        )

    @staticmethod
    def _parse_bucket(line: str) -> BucketRangeRow:
        cols = line.split("\t")
        return BucketRangeRow(
            bucket_range_id=cols[0],
            size1_bytes=int(float(cols[1])),
            size2_bytes=int(float(cols[2])),
            cost_per_byte=float(cols[3]),
        )


def load_workflow_instance(path: str) -> Tuple[WorkflowInstance, List[TaskRow], List[DataRow], List[VmRow], List[ConfigRow], List[BucketRangeRow]]:
    parsed = InstanceParser.parse_file(Path(path))
    return parsed.header, parsed.tasks, parsed.data, parsed.vms, parsed.configs, parsed.bucket_ranges


def get_data_by_id(datas: List[DataRow], data_id: str) -> Optional[DataRow]:
    for data_row in datas:
        if data_row.data_id == data_id:
            return data_row
    return None


def get_read_time(datas: List[DataRow], data_id: str) -> float:
    data_row = get_data_by_id(datas, data_id)
    if data_row is None or data_row.read_time_avg is None:
        return 0.0
    return float(data_row.read_time_avg)


def get_write_time(datas: List[DataRow], data_id: str) -> float:
    data_row = get_data_by_id(datas, data_id)
    if data_row is None or data_row.write_time_avg is None:
        return 0.0
    return float(data_row.write_time_avg)

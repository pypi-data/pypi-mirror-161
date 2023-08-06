"""metrics_manager.py
============
Functionality related to managing metrics
"""

import requests
from collections.abc import Iterable
from .util import raise_resp_exception_error, ElementType
from typing import (
    Any,
    Optional,
    Union,
    List,
    Dict,
    TYPE_CHECKING,
    Tuple,
    TypeVar,
)
from typing_extensions import TypedDict
from termcolor import colored
from base64 import b64encode
import json

if TYPE_CHECKING:
    from .client import Client

# TODO: Better typing
QueryEntry = List[Tuple[str, str]]
QueryEntries = List[QueryEntry]
QueryOrdering = str


class ConfusionsOptsRequired(TypedDict, total=True):
    confidence_threshold: Union[float, int]
    iou_threshold: Union[float, int]
    queries: QueryEntries
    ordering: QueryOrdering


class ConfusionsOpts(ConfusionsOptsRequired, total=False):
    cur_offset: int
    max_results: int
    include_background: bool


class ConfusionsResultDict(TypedDict):
    cur_offset: int
    num_rows: int
    rows: List[Dict[str, Any]]


class MetricValueDict(TypedDict):
    score: float
    threshold: Optional[float]
    succeeds: Optional[bool]


class MetricCountDict(TypedDict):
    score: int


class ScenarioMetricResultDict(TypedDict):
    segment_name: str
    frame_count: int
    segment_type: str
    uuid: str
    precision: MetricValueDict
    recall: MetricValueDict
    f1_score: MetricValueDict
    false_positives: MetricCountDict
    false_negatives: MetricCountDict
    total_confusions: MetricCountDict


class ScenarioInfo(TypedDict):
    name: str
    issue_id: str
    uuid: str
    updated_at: str
    template_type: str
    thresholds: Dict[str, float]


T_ = TypeVar("T_")


def flatten(nested: List[List[T_]]) -> List[T_]:
    return [item for sublist in nested for item in sublist]


class MetricsManager:
    """A manager for interacting with metrics within a given project.

    Contains the following constants:

    .. code-block:: text

        MetricsManager.ORDER_CONF_DESC
        MetricsManager.ORDER_CONF_ASC
        MetricsManager.ORDER_IOU_DESC
        MetricsManager.ORDER_IOU_ASC
        MetricsManager.ORDER_BOX_SIZE_DESC
        MetricsManager.ORDER_BOX_SIZE_ASC

    Args:
        client (Client): An Aquarium Learning Python Client object.
        project_id (str): The project id associated with this manager.
    """

    ORDER_CONF_DESC = "inference_data.confidence__by__desc"
    ORDER_CONF_ASC = "inference_data.confidence__by__asc"
    ORDER_IOU_DESC = "iou__by__desc"
    ORDER_IOU_ASC = "iou__by__asc"
    ORDER_BOX_SIZE_DESC = "box_size__by__desc"
    ORDER_BOX_SIZE_ASC = "box_size__by__asc"

    TEMPLATE_TO_TYPE_MAPPING = {
        "testScenarioSplit": "Split",
        "testScenarioRegression": "Regression Test",
        "testScenarioGeneric": "Scenario",
    }

    def __init__(self, client: "Client", project_id: str) -> None:
        print(
            colored(
                "\nThe metrics manager is in an alpha state, and may experience breaking changes in future updates\n",
                "yellow",
            )
        )

        self.client = client
        self.project_id = project_id
        self.project_info = self.client.get_project(project_id)

        # Matches logic in /all_detection_metrics
        inference_class_map = [
            x
            for x in self.project_info["label_class_map"]
            if "train_name" not in x or x["train_name"] != ""
        ]
        inference_class_names = [
            x.get("train_name") or x.get("name") for x in inference_class_map
        ]

        # Pre-computed metrics are normalized to always be lowercased to be case insensitive
        inference_class_names = [x.lower() for x in inference_class_names]
        inference_class_set = set(inference_class_names)

        # Make sure it has background
        self.inference_classes_nobg = sorted(list(inference_class_set))
        self.inference_classes = self.inference_classes_nobg + ["background"]
        self.inference_classes_set = set(self.inference_classes)

    def list_scenarios(self, dataset_id: str) -> List[ScenarioInfo]:
        """List all scenarios for a dataset.

        Args:
            dataset_id (str): The dataset id.

        Returns:
            List[ScenarioInfo]: All scenarios for the dataset.
        """
        url = f"/projects/{self.project_id}/datasets/{dataset_id}/list_scenarios"
        r = requests.get(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
        )
        raise_resp_exception_error(r)

        result = r.json()
        return result

    def get_metrics(
        self,
        dataset_id: str,
        inferences_id: str,
        confidence_pct: float,
        iou_pct: float,
        scenario_ids: List[str] = [],
        metrics_class: Optional[str] = None,
    ) -> List[ScenarioMetricResultDict]:
        """Get metrics for an inference set, optionally across scenarios.

        Args:
            dataset_id (str): The dataset id.
            inferences_id (str): The inference set id.
            confidence_pct (float or int): The confidence threshold provided as a percent (ie 10 instead of 0.10).
            iou_pct (float or int): The IOU threshold provided as a percent (ie 10 instead of 0.10).
            scenario_ids (None or List[str]): Scenario names to fetch metrics for.
                If None, returns metrics for all scenarios for the dataset.
                Defaults to [], which only returns metrics for the complete inference set.
            metrics_class (None or str): Class name to fetch metrics for. Defaults to None which returns weighted avg.

        Returns:
            List[ScenarioMetricResultDict]: Result metrics.
        """
        datasets = self.client.get_datasets(self.project_id, include_archived=False)
        existing_dataset_ids = [dataset.get("id") for dataset in datasets]

        inferences_dataset_id = self._get_inference_name(dataset_id, inferences_id)

        if dataset_id not in existing_dataset_ids:
            raise Exception(f"Invalid dataset id provided: {dataset_id}.")

        if inferences_dataset_id not in existing_dataset_ids:
            raise Exception(f"Invalid inference id provided: {inferences_dataset_id}.")

        if (
            metrics_class is not None
            and metrics_class not in self.inference_classes_set
        ):
            raise Exception("Invalid class.")

        base_dataset_info = next(x for x in datasets if x.get("id") == dataset_id)
        inferences_info = next(
            x for x in datasets if x.get("id") == inferences_dataset_id
        )

        labels_table_filtered = self._load_data_table(
            dataset_id, inferences_dataset_id, base_dataset_info, inferences_info
        )
        bbox_metrics_metadata = inferences_info.get("bbox_metrics_metadata", {})
        if bbox_metrics_metadata.get("metrics_type") != "precomputed_v4":
            if iou_pct % 10 != 0:
                raise Exception("IOU percent must be multiple of 10")
            if confidence_pct % 10 != 0:
                raise Exception("Confidence percent must be multiple of 10")

        url = f"/projects/{self.project_id}/datasets/get_scenario_metrics"

        if scenario_ids is not None and len(scenario_ids) > 0:
            scenarios = []
            all_scenarios = self.list_scenarios(dataset_id)
            for scenario_id in scenario_ids:
                matched = [x for x in all_scenarios if x["name"] == scenario_id]
                if len(matched) != 1:
                    raise Exception(f"Scenario not found: {scenario_id}")
                scenarios += matched
        elif scenario_ids is not None:
            scenarios = []
        else:
            scenarios = None

        payload: Dict[str, Any] = {
            "filtered_labels": False,
            "labels_table_filtered": labels_table_filtered,
            "inferences": [
                {
                    "name": inferences_dataset_id,
                    "iou": iou_pct,
                    "confidence": confidence_pct,
                    "is_other_inf": False,
                }
            ],
            "scenarios": scenarios,
            "metrics_class": metrics_class,
        }
        r = requests.post(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )
        metrics = r.json()

        iou_str = str(float(iou_pct))
        conf_str = str(float(confidence_pct))

        results: List[ScenarioMetricResultDict] = []
        for scenario_result in metrics[inferences_dataset_id]:
            precision_threshold = scenario_result.get("issue_thresholds", {}).get(
                "precision_threshold"
            )
            recall_threshold = scenario_result.get("issue_thresholds", {}).get(
                "recall_threshold"
            )
            f1_threshold = scenario_result.get("issue_thresholds", {}).get(
                "f1_threshold"
            )
            scenario_metrics = scenario_result["metrics"][iou_str][conf_str]
            results.append(
                {
                    "segment_name": scenario_result["name"],
                    "frame_count": scenario_result["count"],
                    "precision": {
                        "score": scenario_metrics[0],
                        "threshold": precision_threshold,
                        "succeeds": scenario_metrics[0] >= precision_threshold
                        if precision_threshold
                        else None,
                    },
                    "recall": {
                        "score": scenario_metrics[1],
                        "threshold": recall_threshold,
                        "succeeds": scenario_metrics[0] >= recall_threshold
                        if recall_threshold
                        else None,
                    },
                    "f1_score": {
                        "score": scenario_metrics[2],
                        "threshold": f1_threshold,
                        "succeeds": scenario_metrics[2] >= f1_threshold
                        if f1_threshold
                        else None,
                    },
                    "false_positives": {"score": scenario_metrics[3]},
                    "false_negatives": {"score": scenario_metrics[4]},
                    "total_confusions": {"score": scenario_metrics[5]},
                    "segment_type": self.TEMPLATE_TO_TYPE_MAPPING[
                        scenario_result["issue_template_type"]
                    ],
                    "uuid": scenario_result["uuid"],
                }
            )
        return results

    def make_cell_query(self, gt: str, inf: str) -> QueryEntry:
        """Make a query entry for a specific confusion of gt as as inf.

        Args:
            gt (str): The classname of the ground truth class.
            inf (str): The classname of the inference class.

        Returns:
            QueryEntry: Result query entry.
        """
        if (
            gt not in self.inference_classes_set
            or inf not in self.inference_classes_set
        ):
            raise Exception("Invalid classname provided.")

        return [(gt, inf)]

    def make_correct_query(self) -> QueryEntry:
        """Make a query entry for all correct detections/classifications (gt == inf)

        Returns:
            QueryEntry: Result query entry.
        """

        return [(name, name) for name in self.inference_classes_nobg]

    def make_confusions_query(self) -> QueryEntry:
        """Make a query entry for all confusions (gt != inf)

        This will only include cases where two matched detections exist, not
        for false positive or false negative detections.

        Returns:
            QueryEntry: Result query entry.
        """

        acc = []
        for gt_name in self.inference_classes_nobg:
            for inf_name in self.inference_classes_nobg:
                if gt_name == inf_name:
                    continue

                acc.append((gt_name, inf_name))

        return acc

    def make_false_positives_query(self) -> QueryEntry:
        """Make a query entry for all false positive detections.

        These are cases without corresponding ground truth detections
        for an inference detection.

        Returns:
            QueryEntry: Result query entry.
        """

        return [("background", name) for name in self.inference_classes_nobg]

    def make_false_negatives_query(self) -> QueryEntry:
        """Make a query entry for all false negative detections.

        These are cases without corresponding inference detections
        for a ground truth detection.

        Returns:
            QueryEntry: Result query entry.
        """

        return [(name, "background") for name in self.inference_classes_nobg]

    def make_confused_as_query(self, name: str) -> QueryEntry:
        """Make a query entry for all confusions as name. (inf == name, gt != inf)

        This will only include cases where two matched detections exist, not
        for false positive or false negative detections.

        Returns:
            QueryEntry: Result query entry.
        """

        if name not in self.inference_classes_set:
            raise Exception("Invalid classname provided.")

        acc = []
        for other_name in self.inference_classes_nobg:
            if other_name == name:
                continue
            acc.append((other_name, name))

        return acc

    def make_confused_from_query(self, name: str) -> QueryEntry:
        """Make a query entry for all confusions from name. (gt == name, gt != inf)

        This will only include cases where two matched detections exist, not
        for false positive or false negative detections.

        Returns:
            QueryEntry: Result query entry.
        """

        if name not in self.inference_classes_set:
            raise Exception("Invalid classname provided.")

        acc = []
        for other_name in self.inference_classes_nobg:
            if other_name == name:
                continue
            acc.append((name, other_name))

        return acc

    def _encode_query(self, query: QueryEntry) -> str:
        """This function takes in a full-form Query Entry (list of pairs), and returns a short string representation.

        To do so, it replaces explicit lists of inclusions with lists of exclusions.
        For example, assume you have 100 classes and want every time class X is confused as something else.
        This is equivalent to a row of the confusion matrix, minus the cell on the diagonal.

        If we list all included cells, that's 99 unique pairs. Instead, we can represent membership
        as "this row, except where cell[0] == X and cell[1] == X".

        This function takes the input and replaces cells with more efficient row/column-except representations.

        Then, it takes that shorter list and jsonifies -> b64 encodes so it can be easily transmitted and stored.

        Args:
            query (QueryEntry): Full-form query to be compressed / encoded

        Returns:
            str: base64 encoded form of the json string describing the query.
        """
        REQ_RATIO = 3

        def pairKey(a: str, b: str) -> str:
            return f"{a}__aq__{b}"

        def splitKey(s: str) -> List[str]:
            return s.split("__aq__")

        unassigned = set([pairKey(x[0], x[1]) for x in query])
        result = []

        for inf_name in self.inference_classes:
            yes = []
            no = []
            for gt_name in self.inference_classes:
                key = pairKey(gt_name, inf_name)
                if key in unassigned:
                    yes.append(gt_name)
                else:
                    no.append(gt_name)

            if len(yes) > (len(no) * REQ_RATIO):
                res = ["inf_except_gt", inf_name]
                res.extend(no)
                for gt_name in self.inference_classes:
                    to_remove_key = pairKey(gt_name, inf_name)
                    if to_remove_key in unassigned:
                        unassigned.remove(to_remove_key)
                result.append(res)

        for gt_name in self.inference_classes:
            yes = []
            no = []
            for inf_name in self.inference_classes:
                key = pairKey(gt_name, inf_name)
                if key in unassigned:
                    yes.append(gt_name)
                else:
                    no.append(gt_name)

            if len(yes) > (len(no) * REQ_RATIO):
                res = ["gt_except_inf", gt_name]
                res.extend(no)
                for inf_name in self.inference_classes:
                    to_remove_key = pairKey(gt_name, inf_name)
                    if to_remove_key in unassigned:
                        unassigned.remove(to_remove_key)
                result.append(res)

        for remaining in unassigned:
            gt_name, inf_name = splitKey(remaining)
            result.append(["pair", gt_name, inf_name])

        stringified = json.dumps(result)
        encoded = b64encode(stringified.encode("utf-8")).decode("utf-8")
        return encoded

    def fetch_confusions(
        self, dataset_id: str, inferences_id: str, opts: ConfusionsOpts
    ) -> ConfusionsResultDict:
        """Fetch confusions for a given dataset + inference set pair.

        The options define the parameters of the query. The options are a dictionary of the form:

        .. code-block:: text

            {
                'confidence_threshold': Union[float, int],
                'iou_threshold': Union[float, int],
                'queries': List[QueryEntry],
                'ordering': QueryOrdering,
                'max_results': int (optional, defaults to 10,000),
                'cur_offset': int (optional, defaults to 0),
            }


        Confidence and iou thresholds can be any multiple of 0.1 between 0.0 and 1.0.
        Queries are a list of queries produced from helper methods such as

            metrics_manager.make_confusions_query()

        Ordering is defined by constants on the class object, such as:

            metrics_manager.ORDER_CONF_DESC

        Args:
            dataset_id (str): The dataset id.
            inferences_id (str): The inference set id.
            opts (ConfusionsOpts): Options for the query.

        Returns:
            ConfusionsResultDict: All of your query results, up to max_results (default = 10k)
        """

        datasets = self.client.get_datasets(self.project_id, include_archived=False)
        existing_dataset_ids = [dataset.get("id") for dataset in datasets]

        inferences_dataset_id = self._get_inference_name(dataset_id, inferences_id)

        if (
            inferences_dataset_id not in existing_dataset_ids
            or dataset_id not in existing_dataset_ids
        ):
            raise Exception("Invalid IDs provided.")

        base_dataset_info = next(x for x in datasets if x.get("id") == dataset_id)
        inferences_info = next(
            x for x in datasets if x.get("id") == inferences_dataset_id
        )

        is_streaming = base_dataset_info.get("is_streaming", False)
        latest_window = str((inferences_info.get("ingest_agg_windows") or [0])[-1])
        bbox_metrics_metadata = inferences_info.get("bbox_metrics_metadata")
        if bbox_metrics_metadata is None:
            raise Exception("No valid metrics computed.")

        ######################################################################
        # Load (potentially windowed / versioned) data table
        ######################################################################
        dataset_table = ".".join([self.project_id, dataset_id])
        inference_set_table = ".".join([self.project_id, inferences_dataset_id])

        labels_table_filtered = self._load_data_table(
            dataset_id, inferences_dataset_id, base_dataset_info, inferences_info
        )

        ######################################################################
        # Load confusion matrix
        ######################################################################

        for field in ["confidence_threshold", "iou_threshold", "queries", "ordering"]:
            if field not in opts:
                raise Exception(f"Required field {field} not in opts.")

        flattened_query_cells = flatten(opts["queries"])
        encoded_query = self._encode_query(flattened_query_cells)

        # TODO: Make labels_table_filtered the results of calling `/api/v1/query`

        default_payload_args = {
            "active_metric_type": "default",
            "associations_table": bbox_metrics_metadata["metrics_table"],
            "cur_offset": 0,
            "include_background": False,
            "inferences_table": inference_set_table,
            "labels_table": dataset_table,
            "labels_table_filtered": labels_table_filtered,
            "max_results": 10000,
            "other_associations_table": None,
        }

        payload = {**default_payload_args, "encoded_filter_classes": encoded_query}
        for k, v in opts.items():
            if k == "queries":
                continue

            payload[k] = v  # type: ignore

        if int(payload["iou_threshold"] * 100) % 10 != 0:
            raise Exception("iou_threshold must be a multiple of 0.1")
        if int(payload["confidence_threshold"] * 100) % 10 != 0:
            raise Exception("confidence_threshold must be a multiple of 0.1")

        url = "/confusion_matrix_query"
        r = requests.post(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)

        result = r.json()
        if "dest_table" in result:
            del result["dest_table"]

        return result

    def _load_data_table(
        self,
        dataset_id: str,
        inferences_dataset_id: str,
        base_dataset_info: Dict[str, Any],
        inferences_info: Dict[str, Any],
    ) -> str:
        ######################################################################
        # Load (potentially windowed / versioned) data table
        ######################################################################

        is_streaming = base_dataset_info.get("is_streaming", False)
        latest_window = str((inferences_info.get("ingest_agg_windows") or [0])[-1])
        bbox_metrics_metadata = inferences_info.get("bbox_metrics_metadata")
        if bbox_metrics_metadata is None:
            raise Exception("No valid metrics computed.")

        dataset_table = ".".join([self.project_id, dataset_id])
        inference_set_table = ".".join([self.project_id, inferences_dataset_id])

        # TODO: Support streaming datasets
        table_query_params: Dict[str, Union[bool, str]] = {
            "dataset": dataset_table,
            "inference_set": inference_set_table,
            "metrics_table": bbox_metrics_metadata.get("metrics_table"),
            "is_streaming": is_streaming,
            "project": self.project_id,
            "window": latest_window,
            "query": "{}",
        }

        url = "/joined_filtered_table"
        r = requests.get(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            params=table_query_params,
        )

        raise_resp_exception_error(r)
        result = r.json()

        labels_table_filtered = result["dest_table"]
        return labels_table_filtered

    def _get_inference_name(self, dataset_id: str, inferences_id: str) -> str:
        inferences_dataset_id = inferences_id
        if not inferences_dataset_id.startswith("inferences_"):
            inferences_dataset_id = "_".join(["inferences", dataset_id, inferences_id])
        return inferences_dataset_id

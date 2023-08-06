"""work_queues.py
============
Functionality related to work queue management
"""

import requests
from collections.abc import Iterable
from .util import all_issue_states, raise_resp_exception_error, ElementType, IssueState
from typing import Any, Union, List, Dict, Optional, TYPE_CHECKING
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from .client import Client


class WorkQueueElement:
    """Definition for work queue element.

    Args:
        element_id (str): The element id.
        frame_id (str): The frame id of the element.
        element_type (str): The element type of the issue element ("frame" or "crop").
        dataset (str): The base dataset an element is from. (Can be formatted as either "project_name.dataset_name" or just "dataset_name")
        batch_name (str): The batch within the queue that the element belongs to
        status (str): The work status of the element. Can be queued, assigned, or done
        assignee: (Optional[str]): The email of the person who is assigned to work on the element
        inference_set (Optional[str]): The inference set an element is from (if any). (Can be formatted as either "project_name.inference_set_name" or just "inference_set_name")
        label_metadata (Optional[Dict[str, Any]]): (*For read purposes, not element modification*). JSON object with confidence and IOU info if the element was created from a ground truth/inference comparison.
    """

    def __init__(
        self,
        element_id: str,
        frame_id: str,
        element_type: str,
        dataset: str,
        batch_name: str,
        status: str,
        assignee: Optional[str] = None,
        inference_set: Optional[str] = None,
        label_metadata: Optional[Dict[str, Any]] = None,
    ):
        if element_type != "crop" and element_type != "frame":
            raise Exception('element_type must be either "crop" or "frame"')

        self.element_id = element_id
        self.frame_id = frame_id
        self.element_type = element_type
        self.status = status
        self.assignee = assignee
        self.batch_name = batch_name
        self.dataset = dataset
        self.inference_set = inference_set
        self.label_metadata = label_metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "frame_id": self.frame_id,
            "element_type": self.element_type,
            "status": self.status,
            "assignee": self.assignee,
            "batch_name": self.batch_name,
            "dataset": self.dataset,
            "inference_set": self.inference_set,
            "label_metadata": self.label_metadata,
        }


class WorkQueueApiResp(TypedDict):
    id: str
    compare_dataset: Optional[str]
    dataset: Optional[str]
    name: str
    element_type: ElementType
    created_at: Optional[str]
    updated_at: Optional[str]
    state: Optional[IssueState]
    issue_id: Optional[str]
    element_count: int
    batch_statuses: Dict[str, str]
    batch_assignees: Dict[str, str]
    elements: Optional[List[Dict[str, Any]]]


class WorkQueue:
    """Definition for work queue.

    Args:
        name (str): The work queue name.
        dataset (Optional[str]): The dataset for this work queue.
        elements (List[WorkQueueElement]): The elements of the work queue.
        element_type (str): The element type of the work queue ("frame", "crop").
        element_count (int): The number of elements in the work queue.
        created_at (str): The time of work queue creation.
        updated_at (str): The time of last work queue update.
        work_queue_id (str): The work queue id.
        batch_statuses (Dict[str, str]): The statuses of all batches in this queue.
        batch_assignees (Dict[str, str]): The emails of users assigned to batches if they have been assigned
        inference_set (Optional[str], optional): The inference set for this work queue. Defaults to None.
    """

    def __init__(
        self,
        name: str,
        dataset: Optional[str],
        element_count: Optional[int],
        element_type: ElementType,
        work_queue_id: str,
        batch_statuses: Dict[str, str],
        batch_assignees: Dict[str, str],
        elements: Optional[List[WorkQueueElement]] = None,
        # TODO: This used to say datetime, but it looks like it should be a str?
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        inference_set: Optional[str] = None,
    ):

        self.name = name
        self.dataset = dataset
        self.elements = elements
        self.element_count = element_count or (len(elements) if elements else 0)
        self.element_type = element_type
        self.batch_statuses = batch_statuses
        self.batch_assignees = batch_assignees
        self.created_at = created_at
        self.updated_at = updated_at
        self.work_queue_id = work_queue_id
        self.inference_set = inference_set

    def __repr__(self) -> str:
        return "Work Queue {} ({})".format(self.work_queue_id, self.name)

    def __str__(self) -> str:
        return "Work Queue {} ({})".format(self.work_queue_id, self.name)

    def to_dict(self) -> Dict[str, Any]:
        wq_dict: Dict[str, Any] = {
            "name": self.name,
            "dataset": self.dataset,
            "element_count": self.element_count,
            "element_type": self.element_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "work_queue_id": self.work_queue_id,
            "inference_set": self.inference_set,
            "batch_statuses": self.batch_statuses,
            "batch_assignees": self.batch_assignees,
        }
        if self.elements:
            wq_dict["elements"] = [x.to_dict() for x in self.elements]

        return wq_dict


class WorkQueueManager:
    """A work queue manager for interacting with work queues within a given project.

    Args:
        client (Client): An Aquarium Learning Python Client object.
        project_id (str): The project id associated with this manager.
    """

    def __init__(self, client: "Client", project_id: str) -> None:
        self.client = client
        self.project_id = project_id

    @staticmethod
    def _work_queue_from_api_resp(api_resp: WorkQueueApiResp) -> WorkQueue:
        # TODO: Hack because internal data model for work queues is still dataset/compare dataset,
        # not dataset + inference set + other inference set.

        compare_dataset = api_resp.get("compare_dataset")
        raw_dataset = api_resp.get("dataset")
        dataset: Optional[str] = None
        inference_set: Optional[str] = None

        batch_statuses = api_resp.get("batch_statuses", {})
        batch_assignees = api_resp.get("batch_assignees", {})

        for batch_name in batch_statuses:
            if batch_statuses[batch_name] != "done" and batch_name in batch_assignees:
                batch_statuses[batch_name] = "assigned"

        if compare_dataset and raw_dataset:
            dataset = compare_dataset.split(".")[1]
            inference_set = raw_dataset.split(".")[1]
        elif raw_dataset:
            dataset = raw_dataset.split(".")[1]
            inference_set = None
        else:  # in the case of an issue with no elements
            dataset = None
            inference_set = None

        elements = []
        raw_els = api_resp.get("elements", []) or []
        for raw_el in raw_els:
            # TODO: Is the change to explicit accesses vs nullable gets correct?
            elements.append(
                WorkQueueElement(
                    element_id=raw_el["element_id"],
                    element_type=api_resp["element_type"],
                    frame_id=raw_el["frame_id"],
                    status=raw_el["status"],
                    batch_name=raw_el["batch_name"],
                    assignee=raw_el["assignee"],
                    dataset=raw_el["dataset"],
                    inference_set=raw_el.get("inference_set"),
                    label_metadata=raw_el.get("label_metadata"),
                )
            )

        # TODO: Is the change to explicit accesses vs nullable gets correct?
        return WorkQueue(
            name=api_resp["name"],
            element_type=api_resp["element_type"],
            created_at=api_resp.get("created_at"),
            updated_at=api_resp.get("updated_at"),
            work_queue_id=api_resp["id"],
            dataset=dataset,
            inference_set=inference_set,
            element_count=api_resp.get("element_count"),
            elements=elements or None,
            batch_statuses=batch_statuses,
            batch_assignees=batch_assignees,
        )

    def list_work_queues(self) -> List[WorkQueue]:
        """List work queues in the associated project.

        NOTE: this does NOT include any element data, just the element counts.
        (Use `get_work_queue` instead to see that info).

        Returns:
            List[WorkQueue]: List of all work queues data.
        """
        url = "/projects/{}/issues/work_queues/summaries".format(self.project_id)
        r = requests.get(
            self.client.api_endpoint + url, headers=self.client._get_creds_headers()
        )

        raise_resp_exception_error(r)
        return [self._work_queue_from_api_resp(x) for x in r.json()]

    def get_work_queue(
        self,
        work_queue_id: str,
    ) -> WorkQueue:
        """Get a specific work queue in the associated project.

        Args:
            work_queue_id (str): The work queue id.

        Returns:
            WorkQueue: The work queue data (including elements).
        """
        url = "/projects/{}/issues/work_queues/{}/download_elements".format(
            self.project_id, work_queue_id
        )

        r = requests.get(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            params={
                "get_as_gcs_file": True,
            },
        )

        raise_resp_exception_error(r)
        signed_url = r.json()["signed_url"]
        r = requests.get(signed_url)
        return self._work_queue_from_api_resp(r.json())

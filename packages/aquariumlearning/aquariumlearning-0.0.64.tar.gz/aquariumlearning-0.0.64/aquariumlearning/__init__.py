# Only expose public API

from .util import check_if_update_needed

from .client import (
    Client as Client,
    LabeledDataset as LabeledDataset,
    UnlabeledDataset as UnlabeledDataset,
    LabeledFrame as LabeledFrame,
    UnlabeledFrame as UnlabeledFrame,
    Inferences as Inferences,
    InferencesFrame as InferencesFrame,
    LabelClassMap as LabelClassMap,
    ClassMapEntry as ClassMapEntry,
    ClassMapUpdateEntry as ClassMapUpdateEntry,
    UpdateGTLabelSet as UpdateGTLabelSet,
    CustomMetricsDefinition as CustomMetricsDefinition,
    StratifiedMetricsDefinition as StratifiedMetricsDefinition,
    orig_label_color_list as orig_label_color_list,
    tableau_colors as tableau_colors,
    turbo_rgb as turbo_rgb,
    viridis_rgb as viridis_rgb,
)
from .collection_client import CollectionClient as CollectionClient

from .issues import (
    IssueManager as IssueManager,
    Issue as Issue,
    IssueElement as IssueElement,
)
from .metrics_manager import MetricsManager as MetricsManager
from .work_queues import (
    WorkQueueManager as WorkQueueManager,
    WorkQueue as WorkQueue,
    WorkQueueElement as WorkQueueElement,
)

# TODO: Avoid duplicating here while still getting nice autodoc?
__all__ = [
    "Client",
    "CollectionClient",
    "LabeledDataset",
    "UnlabeledDataset",
    "LabeledFrame",
    "UnlabeledFrame",
    "Inferences",
    "InferencesFrame",
    "LabelClassMap",
    "ClassMapEntry",
    "ClassMapUpdateEntry",
    "UpdateGTLabelSet",
    "CustomMetricsDefinition",
    "StratifiedMetricsDefinition",
    "orig_label_color_list",
    "tableau_colors",
    "turbo_rgb",
    "viridis_rgb",
    "IssueManager",
    "Issue",
    "IssueElement",
    "MetricsManager",
    "WorkQueueManager",
    "WorkQueue",
    "WorkQueueElement",
]

check_if_update_needed()

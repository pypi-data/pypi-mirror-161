"""
Workflow which exercises the common tasks in an end to end scenario
"""
from dkist_processing_common.tasks import AddDatasetReceiptAccount
from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitQuality
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_core import Workflow

from dkist_processing_test.tasks.fake_science import GenerateCalibratedData
from dkist_processing_test.tasks.movie import AssembleTestMovie
from dkist_processing_test.tasks.movie import MakeTestMovieFrames
from dkist_processing_test.tasks.parse import ParseL0TestInputData
from dkist_processing_test.tasks.quality import TestQualityL0Metrics
from dkist_processing_test.tasks.write_l1 import WriteL1Data

end_to_end = Workflow(
    process_category="test",
    process_name="management_processes_end_to_end",
    workflow_package=__package__,
    tags=["test"],
)
end_to_end.add_node(task=TransferL0Data, upstreams=None)
end_to_end.add_node(task=ParseL0TestInputData, upstreams=TransferL0Data)
end_to_end.add_node(task=TestQualityL0Metrics, upstreams=ParseL0TestInputData)
end_to_end.add_node(task=GenerateCalibratedData, upstreams=TestQualityL0Metrics)
end_to_end.add_node(task=WriteL1Data, upstreams=GenerateCalibratedData)
end_to_end.add_node(task=QualityL1Metrics, upstreams=WriteL1Data)
end_to_end.add_node(task=SubmitQuality, upstreams=QualityL1Metrics)
end_to_end.add_node(task=MakeTestMovieFrames, upstreams=WriteL1Data)
end_to_end.add_node(task=AssembleTestMovie, upstreams=MakeTestMovieFrames)
end_to_end.add_node(task=AddDatasetReceiptAccount, upstreams=[AssembleTestMovie, SubmitQuality])
end_to_end.add_node(task=TransferL1Data, upstreams=AddDatasetReceiptAccount)
end_to_end.add_node(task=PublishCatalogAndQualityMessages, upstreams=TransferL1Data)
end_to_end.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)

import logging
from typing import List

from bigeye_sdk.model.metric_facade import SimpleUpsertMetricRequest

from bigeye_sdk.client.datawatch_client import DatawatchClient

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator


class CreateMetricOperator(ClientExtensibleOperator):
    """
    The CreateMetricOperator takes a list of SimpleUpsertMetricRequest objects and instantiates them according to the
    business logic of Bigeye's API.
    """

    def __init__(self,
                 connection_id: str,
                 warehouse_id: int,
                 configuration: List[dict],
                 run_after_upsert: bool = False,
                 *args,
                 **kwargs):
        """
        param connection_id: string referencing a defined connection in the Airflow deployment.
        param warehouse_id: int id of the warehouse where the operator will upsert the metrics.
        param configuration: list of metric configurations to upsert.  The dicts passed as a list must conform to the
        dataclass SimplePredefinedMetricTemplate.
        param args: not currently supported
        param kwargs: not currently supported
        """

        super(CreateMetricOperator, self).__init__(*args, **kwargs)
        self.connection_id = connection_id

        self.configuration: List[SimpleUpsertMetricRequest] = []

        for c in configuration:
            c['warehouse_id'] = warehouse_id
            self.configuration.append( SimpleUpsertMetricRequest.from_dict(c))

        self.connection_id = connection_id
        self.client = None

        self.run_after_upsert = run_after_upsert

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(self.connection_id)
        return self.client

    def execute(self, context):

        num_failing_metric_runs = 0
        created_metrics_ids: List[int] = []

        # Iterate each configuration
        for c in self.configuration:

            metric_id = self.get_client().upsert_metric_from_simple_template(sumr=c)
            created_metrics_ids.append(metric_id)

            if self.run_after_upsert and metric_id is not None:
                hook = self.get_hook('GET')
                logging.info(f"Running metric ID: {metric_id}")
                metric_result = hook.run(
                    f"statistics/runOne/{metric_id}",
                    headers={"Content-Type": "application/json", "Accept": "application/json"}).json()

                for mr in metric_result:
                    if not mr['statusOk']:
                        logging.error("Metric is not OK: %s", metric_id)
                        logging.error("Metric result: %s", mr)
                        num_failing_metric_runs += 1

        return created_metrics_ids


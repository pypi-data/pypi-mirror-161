from gantry.query.core.dataframe import GantrySeries
from gantry.query.core.utils import check_response, same_size


class GantryDistance(object):
    """
    Gantry distribution distance accessor.
    """

    def __init__(self, api_client) -> None:
        self._api_client = api_client

    @same_size("feat1", "feat2")
    def d1(self, feat1: GantrySeries, feat2: GantrySeries) -> float:
        """
        Computes the D1 distance between the input feature's distributions.

        Args:
            feat1: feature as a GantrySeries
            feat2: feature to compute dist with as a GantrySeries
        Returns: float d1 distance
        """
        return self._diff_query(feat1, feat2, "d1")

    @same_size("feat1", "feat2")
    def dinf(self, feat1: GantrySeries, feat2: GantrySeries) -> float:
        """
        Computes the maximum distance between the input features's distributions.

        Args:
            feat1: feature as a GantrySeries
            feat2: feature to compute dist with as a GantrySeries
        Returns: float d_inf distance
        """
        return self._diff_query(feat1, feat2, "dinf")

    def ks(self, feat1: GantrySeries, feat2: GantrySeries) -> float:
        """
        Performs the one-sample Kolmogorov-Smirnov test for goodness of fit between the
        input features's distributions.

        Args:
            feat1: feature as a GantrySeries
            feat2: feature to compute dist with as a GantrySeries
        Returns: Tuple[float ks distance measure]
        """
        return self._diff_query(feat1, feat2, "ks")

    @same_size("feat1", "feat2")
    def kl(self, feat1: GantrySeries, feat2: GantrySeries) -> float:
        """
        Gets the Kullback-Leibler divergence between the input features's distributions.

        Args:
            feat1: feature as a GantrySeries
            feat2: feature to compute dist with as a GantrySeries
        Returns: Tuple[float kl divergence]
        """
        return self._diff_query(feat1, feat2, "kl")

    def _diff_query(self, feat1: GantrySeries, feat2: GantrySeries, stat: str) -> float:
        data = feat1.query_info.get_base_query_params()
        data["queries"] = {
            "query": {
                "query_type": "diff",
                "stat": stat,
                "base": {
                    "query_type": "feature",
                    "feature": feat1.name,
                    "model_node_id": feat1.query_info.application_node_id,
                    "start_time": feat1.query_info.start_time,
                    "end_time": feat1.query_info.end_time,
                },
                "other": {
                    "query_type": "feature",
                    "feature": feat2.name,
                    "model_node_id": feat2.query_info.application_node_id,
                    "start_time": feat2.query_info.start_time,
                    "end_time": feat2.query_info.end_time,
                },
            }
        }
        response = self._api_client.request("POST", "/api/v1/aggregate/query", json=data)
        check_response(response)

        try:
            return response["data"]["query"][stat]
        except KeyError:
            raise RuntimeError("Invalid response from API server")

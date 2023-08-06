from typing import Dict
from typing import List

from tecton._internals.fco import Fco
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id


class FeatureDefinition(Fco):
    """
    Represents the base class for Declarative FeatureViews and FeatureTables
    """

    _args: FeatureViewArgs
    _source_info: SourceInfo

    @property
    def _id(self) -> Id:
        return self._args.feature_view_id

    @property
    def name(self) -> str:
        """
        Name of this Tecton Object.
        """
        return self._args.info.name

    def __getitem__(self, features: List[str]):
        from tecton.feature_services.feature_service_args import FeaturesConfig

        assert isinstance(features, list), "The `features` field must be a list"
        return FeaturesConfig(feature_view=self, namespace=self.name, features=features)

    def with_name(self, namespace: str):
        """
        Used to rename a Feature View used in a Feature Service.

        .. code-block:: python

            from tecton import FeatureService

            # The feature view in this feature service will be named "new_named_feature_view" in training data dataframe
            # columns and other metadata.
            feature_service = FeatureService(
                name="feature_service",
                features=[
                    my_feature_view.with_name("new_named_feature_view")
                ],
            )

            # Here is a more sophisticated example. The join keys for this feature service will be "transaction_id",
            # "sender_id", and "recipient_id" and will contain three feature views named "transaction_features",
            # "sender_features", and "recipient_features".
            transaction_fraud_service = FeatureService(
                name="transaction_fraud_service",
                features=[
                    # Select a subset of features from a feature view.
                    transaction_features[["amount"]],

                    # Rename a feature view and/or rebind its join keys. In this example, we want user features for both the
                    # transaction sender and recipient, so include the feature view twice and bind it to two different feature
                    # service join keys.
                    user_features.with_name("sender_features").with_join_key_map({"user_id" : "sender_id"}),
                    user_features.with_name("recipient_features").with_join_key_map({"user_id" : "recipient_id"}),
                ],
            )
        """
        from tecton.feature_services.feature_service_args import FeaturesConfig

        return FeaturesConfig(feature_view=self).with_name(namespace)

    def with_join_key_map(self, join_key_map: Dict[str, str]):
        """
        Used to rebind join keys for a Feature View used in a Feature Service. The keys in `join_key_map` should be the feature view join keys, and the values should be the feature service overrides.

        .. code-block:: python

            from tecton import FeatureService

            # The join key for this feature service will be "feature_service_user_id".
            feature_service = FeatureService(
                name="feature_service",
                features=[
                    my_feature_view.with_join_key_map({"user_id" : "feature_service_user_id"}),
                ],
            )

            # Here is a more sophisticated example. The join keys for this feature service will be "transaction_id",
            # "sender_id", and "recipient_id" and will contain three feature views named "transaction_features",
            # "sender_features", and "recipient_features".
            transaction_fraud_service = FeatureService(
                name="transaction_fraud_service",
                features=[
                    # Select a subset of features from a feature view.
                    transaction_features[["amount"]],

                    # Rename a feature view and/or rebind its join keys. In this example, we want user features for both the
                    # transaction sender and recipient, so include the feature view twice and bind it to two different feature
                    # service join keys.
                    user_features.with_name("sender_features").with_join_key_map({"user_id" : "sender_id"}),
                    user_features.with_name("recipient_features").with_join_key_map({"user_id" : "recipient_id"}),
                ],
            )
        """
        from tecton.feature_services.feature_service_args import FeaturesConfig

        return FeaturesConfig(feature_view=self).with_join_key_map(join_key_map)

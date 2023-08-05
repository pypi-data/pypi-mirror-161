from typing import List

import numpy as np
from pandas import DataFrame

from arthurai import ArthurAttribute
from arthurai.common.constants import Stage
from arthurai.common.exceptions import UserValueError


def validate_predicted_attribute_order_matches_remote(model) -> None:
    """
    Checks that the position field of each predicted attribute matches the value when the model is fetched by ID from
    the API

    :param model: model to validate
    :return: None
    :raises UserValueError: if the positions don't match
    """
    local_pred_attr_to_position = {attr.name: attr.position
                                   for attr in model.get_attributes(stage=Stage.PredictedValue)}
    remote_attributes_dict = model._client.get(f"/models/{model.id}", params={"expand": "attributes"})['attributes']
    remote_attrs = [ArthurAttribute.from_dict(attr_dict) for attr_dict in remote_attributes_dict]
    remote_pred_attr_to_position = {attr.name: attr.position
                                    for attr in remote_attrs if attr.stage == Stage.PredictedValue}

    if local_pred_attr_to_position != remote_pred_attr_to_position:
        raise UserValueError(f"Local predicted attribute order does not match remote. Please call ArthurModel"
                             f".update() to register your local changes with the API.")


def validate_predicted_attribute_order_matches_dataframe(actual_preds: np.ndarray, sample_data: DataFrame,
                                                         predicted_attributes: List[ArthurAttribute]):
    """
    Helper function to check that the order of the predicted attributes matches the output from the user predict()
    function.

    A common failure case is a user registering a binary classifier with a single positive predicted
    attribute, but returning the value of predict_proba() from their classifier. The result is that the implicit
    negative column is registered as the second column (<pos_proba>, <neg_proba>) but SkLearn and most other libraries
    output with the negative prediction in the first column (<neg_proba>, <pos_proba>).

    :param actual_preds: predictions pulled from the user's predict() function
    :param sample_data: a DataFrame containing user-provided predictions
    :param predicted_attributes: the model's predicted attributes
    :return: None
    :raises UserValueError: if the prediction order doesn't match or it cannot be determined
    """
    # special case: if binary classifier and negative predicted attribute not provided, add it to the DataFrame
    if len(predicted_attributes) == 2:
        pos_pred_attr = None
        neg_pred_attr = None
        for attr in predicted_attributes:
            if attr.is_positive_predicted_attribute:
                pos_pred_attr = attr.name
            else:
                neg_pred_attr = attr.name
        if pos_pred_attr is None or neg_pred_attr is None:
            raise UserValueError(f"Binary classifier does not have exactly one positive predicted attribute")

        if neg_pred_attr not in sample_data.columns:
            if pos_pred_attr not in sample_data.columns:
                raise UserValueError(f"Predictions not found in provided sample data. Please ensure columns for your "
                                     f"predicted attributes are present in the sample DataFrame when "
                                     f"enabling explainability")
            sample_data = sample_data.copy()  # don't mutate input
            sample_data[neg_pred_attr] = 1 - sample_data[pos_pred_attr]

    # get a NumPy array of the predictions in the DataFrame, with column order matching registered attribute positions
    ordered_pred_attrs = [attr.name for attr in sorted(predicted_attributes, key=lambda a: a.position)]
    try:
        provided_preds = sample_data[ordered_pred_attrs].to_numpy()
    except KeyError as e:
        raise UserValueError(f"Predictions not found in provided sample data. Please ensure columns for your "
                             f"predicted attributes are present in the sample DataFrame when "
                             f"enabling explainability") from e

    # assert that the provided predictions array matches the ordered one using DataFrame values
    provided_preds = provided_preds.reshape(actual_preds.shape)
    epsilon = 0.01
    if (np.abs(provided_preds - actual_preds) > epsilon).any():
        raise UserValueError(f"The outputs of your provided predict() function don't seem to match the prediction "
                             f"outputs in your DataFrame. This may be because the output column order doesn't match "
                             f"the positions of the registered model attributes. View your registered prediction "
                             f"attribute order with:\n"
                             f"    sorted([attr.name for attr in arthur_model.get_attributes("
                             f"stage=Stage.PredictedValue)\n"
                             f"This should match the order of the columns output by your predict() function. For a "
                             f"binary classifier, your predict() function may return the probability for only the "
                             f"positive class or both classes. If you'd like to simply swap the registered positions "
                             f"of your attributes, use ArthurModel.swap_predicted_attribute_positions().\n"
                             f"For other models (e.g. those with several classes), update the 'position' property for "
                             f"each of your predicted attributes, and then call ArthurModel.update() to persist the "
                             f"changes.")

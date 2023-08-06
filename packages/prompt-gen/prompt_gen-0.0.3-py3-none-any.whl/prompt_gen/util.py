from typing import List


def _validate_all_inputs_are_strings_in_a_list_and_not_empty(
    input_list: List[str]
) -> bool | ValueError:
    """
    Validates that all inputs are strings and not empty.
    """
    result = all(
        [
            isinstance(input_item, str) and input_item != ""
            for input_item in input_list
        ])
    if result is False:
        raise ValueError("All inputs must be strings and not empty.")
    else:
        return input_list

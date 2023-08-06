import typing as tp


def validate_type(line_input: tp.Any, line_id: int = 0) -> None:
    """ Verifies if ´line_input´ is of string or list type.
    
    :param line_input: Line to have its type checked.
    :type line_input: `any`
    :param line_id: Optional line identification.
    :type line_id: `int`
    
    :raise Exception: if the input line is not of a valid listed type.
    """
    valid_types = (str, list)
    input_type = type(line_input)
    
    if input_type not in valid_types:
        raise TypeError(f'Expected input of type string or list, but received a type {input_type} on line {line_id}')

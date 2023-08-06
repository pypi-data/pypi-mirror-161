import string
import re


def set_valid_characters(processing_parameter: list) -> set:
    """Set valid characters to keep

    :param processing_parameter: Processing types to be applied.
    :type processing_parameter: `list`
    :return: set with characters to keep
    :rtype: `set`
    """
    accented_letters = {"á", "é", "í", "ó", "ú", "à", "â", "ê", "ô", "ã", "õ",
                        "ç"}
    if "SYMBOL" in processing_parameter:
        valid_characters = set(string.ascii_letters)
        punctuation_to_keep = {"!", ",", ".", ";", "?", ":", "_", "-", "’"}
        valid_characters = valid_characters.union(punctuation_to_keep)
        valid_characters.add(" ")
    else:
        valid_characters = set(string.printable)
    valid_characters = valid_characters.union(accented_letters)
    return valid_characters


def remove_non_ascii_symbol_characters(text_input: str,
                                       processing_parameter: list = []) -> str:
    """ Remove non-ascii characters and symbols from input text.

    To remove symbols value "SYMBOL" has to be set on processing_parameter.

    :param text_input: Input text to be processed.
    :type text_input: `str`
    :param processing_parameter: Processing types to be applied.
    :type processing_parameter: `list`

    :return: Processed text
    :rtype: `str`
    """
    valid_characters = set_valid_characters(processing_parameter)

    return re.sub(" +", " ",
                  "".join(filter(lambda x: x in valid_characters, text_input)))

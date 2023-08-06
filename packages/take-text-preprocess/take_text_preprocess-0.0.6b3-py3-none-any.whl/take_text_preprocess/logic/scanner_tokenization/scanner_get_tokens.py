import typing as tp

from .scanner import Scanner

SCAN = Scanner()


def get_tokens(text_input: str) -> tp.Tuple[tp.List[str]]:
    """ Take Scanner call to tokenize the input text.

    :param text_input: Text to be tokenized.
    :type text_input: `str`
    :return: A tuple containing a list of the tokens and a list of the token types.
    :rtype: `tp.Tuple[tp.List[str]]`
    """
    return SCAN.get_tokens(input_text=text_input)

import typing as tp

from .replace_regex import replace_url, replace_email


def regex_preprocessing(text_input: str, processing_parameters: tp.List[str]) -> str:
    """Apply regex preprocessing methods on text.

    :param text_input: Input to be processed.
    :type text_input: `str`
    :param processing_parameters: Processing types to be applied. Current types supported are 'url' and 'email'.
    :type processing_parameters: `tp.List[str]`
    :return: Processed text
    :rtype: `str`
    """
    sentence = text_input
    if 'URL' in processing_parameters:
        sentence = replace_url(sentence)
    if 'EMAIL' in processing_parameters:
        sentence = replace_email(sentence)
    return sentence

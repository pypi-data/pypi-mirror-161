import typing as tp

from take_text_preprocess.data.validate_inputs import validate_type
from take_text_preprocess.logic.decision_pipeline.pipeline import decision_pipeline


def pre_process(text_input: str, optional_tokenization: tp.List[str] = []):
    """ Apply appropriate pre processing methods to input text.
    
    Optional tokenization includes: `DOC`, `CEP`, `PHONE`, `NUMBER`, `CODE`, `URL`, `CEP`.

    :param text_input: Input text to be processed.
    :type text_input: `str`
    :param optional_tokenization: Optional pre processing options to be applied. Defaults to basic pre processing.
    :type optional_tokenization: tp.List[`str`]
    :return: Pre processed text.
    :rtype: `str`
    """
    validate_type(text_input)
    return decision_pipeline(text_input, optional_tokenization)

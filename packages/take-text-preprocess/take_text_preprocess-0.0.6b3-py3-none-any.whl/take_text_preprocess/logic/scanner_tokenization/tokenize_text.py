import typing as tp

from .scanner_get_tokens import get_tokens


def tokenize_text(text_input: str, processing_parameters: tp.List[str] = []) -> str:
    """ Replace Numbers and Codes with tokens.
    
    :param text_input: Input to be tokenized.
    :type text_input: `str`
    :param processing_parameters: Processing types to be applied. Current types supported are 'NUMBER' or 'CODE'.
    :type processing_parameters: `tp.List[str]`
    :return: Tokenized text.
    :rtype: `str`
    """
    tokens, tokens_type = get_tokens(text_input)
    tokenized_sentence = []
    
    for token, token_type in zip(tokens, tokens_type):
        if token_type in processing_parameters:
            tokenized_sentence.append(token_type)
        else:
            tokenized_sentence.append(token)
        
    return ' '.join(tokenized_sentence)[:-1]

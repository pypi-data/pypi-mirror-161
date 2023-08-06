import re


def add_space_to_punctuation(text_input: str) -> str:
    """ Adds a blank space around punctuation and hyphens on input text.
    
    :param text_input: Text to be processed.
    :type text_input: `str`
    
    :return: Processed text with added black spaces before punctuation.
    :rtype: `str`
    """
    processed_punct = add_space_around_punctuation(text_input)
    processed_hyphen = add_space_to_hyphens(processed_punct)
    
    return processed_hyphen.strip()


def add_space_to_hyphens(text_input: str) -> str:
    """ Adds a blank space around hyphens when the character before it is a number.

    :param text_input: Text to be processed.
    :type text_input: `str`

    :return: Processed text with added black spaces around hyphens.
    :rtype: `str`
    """
    hyphen_pattern = re.compile('(\d)(-)(\w)?')
    return re.sub(hyphen_pattern, r'\1 \2 \3', text_input)


def add_space_around_punctuation(text_input: str) -> str:
    """ Adds a blank space around punctuation.
    
    The characters we consider punctuation are (,.!?/\{}[]()*#@%)

    :param text_input: Text to be processed.
    :type text_input: `str`

    :return: Processed text with added black spaces around hyphens.
    :rtype: `str`
    """
    punctuation_pattern = re.compile('(?<=[^ ])(?=[:,.\\\\!?/\{}\\[\\]()*#@%])|(?<=[:,.\\\\!?/\{}\\[\\]()*#@%])(?=[^ ])')
    
    return re.sub(punctuation_pattern, r' ', text_input)

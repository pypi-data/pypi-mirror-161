import typing as tp


def replace_abbreviations(sentence: str,
                          abbreviations: tp.Dict[str, str]) -> str:
    """
    Checks if there is abbreviated words on the sentence and replaces it with
    the full word.

    :param sentence: Sentence to be processed.
    :type sentence: `str`
    :param abbreviations: Dictionary containing word abbreviations and their full form.
    :type abbreviations: `tp.Dict[str, str]`
    :return: Sentence with all words in their full form.
    :rtype: `str`
    """
    sentence_split = sentence.split()
    modified_sentence = []
    for word in sentence_split:
        if word in abbreviations:
            modified_sentence += abbreviations[word].split()
        else:
            modified_sentence += [word]
    return ' '.join(modified_sentence)

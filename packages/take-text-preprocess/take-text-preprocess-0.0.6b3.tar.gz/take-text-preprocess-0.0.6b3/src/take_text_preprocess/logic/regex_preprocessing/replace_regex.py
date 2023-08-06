import re


def replace_url(text_input: str) -> str:
    """Replace URL with <URL> token on input text.
    :param text_input: Input text to be processed.
    :type text_input: `str`
    :return: Text with URL replaced by <URL>.
    :rtype: `str`
    """
    url_regex = re.compile(r'((https?:\/\/)|(www\.))\w+\.\w+(\.\w+)*(\/.+)*')
    processed_sentence, _ = url_regex.subn('URL', text_input)
    return processed_sentence


def replace_email(text_input: str) -> str:
    """Replace e-mails with <EMAIL> token on input text
    :param text_input: Input text to be processed.
    :type text_input: `str`
    :return: Text with Email replaced by <EMAIL>.
    :rtype: `str`
    """
    if text_input.find('@'):
        email_regex = re.compile(r'([a-z.0-9\_]+)@\w+\.\w+(\.br)?')
        processed_sentence, _ = email_regex.subn('EMAIL', text_input)
        return processed_sentence
    else:
        return text_input

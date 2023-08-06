# Take Text Pre-Process #

This package is a tool for pre-processing a sentence.

The basic functionality available in this packages are:
* Converting to lower case
* Remove non ascii characters
* Add space between punctuation and word

The customize functionality available are:
* Replace URL by a token
* Replace Email by a token
* Replace Numbers by a token
* Replace Code (Number and letters) by a token
* Remove symbols
* Replace abbreviations
* Keep emojis

## Installation
The TakeTextPreProcess can be installed from PyPi:

```bash
pip install take-text-preprocess
```

## Usage

### Basic pre-process
To use the basic pre-process:
```python
from take_text_preprocess.presentation import pre_process
sentence = 'Bom dia, meu ẞ caro'
pre_process(sentence)
```

### Customize pre-process
To use the customize pre-process is needed a input with a list of all pre-process you wanted to use.

The following examples show all the customized pre-processes available.
* URL
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['URL']
sentence = 'Bom dia, meu https://www.take.net  caro'
pre_process(sentence, optional_tokenization)
```

* EMAIL
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['EMAIL']
sentence = 'Bom dia, meu teste@gmail.com  caro'
pre_process(sentence, optional_tokenization)
```

* NUMBER
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['NUMBER']
sentence = 'Este é um número 99999-9999'
pre_process(sentence, optional_tokenization)
```

* CODE
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['CODE']
sentence = 'Este é um código 91234abc'
pre_process(sentence, optional_tokenization)
```

* SYMBOLS
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['SYMBOL']
sentence = 'Este é um símbolo %'
pre_process(sentence, optional_tokenization)
```

* ABBREVIATIONS
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['ABBR']
sentence = 'Este é uma abreviação vc'
pre_process(sentence, optional_tokenization)
```
* EMOJI
```python
from take_text_preprocess.presentation import pre_process
optional_tokenization = ['EMOJI']
sentence = 'Este é um emoji 😀'
pre_process(sentence, optional_tokenization)
```

## Contribute
If this is the first time you are contributing to this project, first create the virtual environment using the following command:
    
    conda env create -f env/environment.yml
   
Then activate the environment:

    conda activate taketextpreprocess
    
To test your modifications build the package:

    pip install dist\take-text-preprocess-VERSION-py3-none-any.whl --force-reinstall
    
Then run the tests:

    pytest

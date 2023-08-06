

<!-- ![Tests](https://gitlab.com/tiro-is/h10/h10/numi/actions/workflows/tests.yml/badge.svg) -->

## Númi
Númi er pakki sem stafar út tölustafi. Þegar notandinn gefur Núma tölu ásamt streng sem inniheldur upplýsingar um beygingar skilar hann öllum mögulegum leiðum sem þessi tala getur verið stöfðu út.

This package expands Icelandic numbers to their corresponding written form. Given a digit and a string containing the case, gender and inflection the funciton will output a list of strings for all written variants.



## Usage

To get started run 
```
pip install numi
```

The main function in Númi is `spell_out`. It takes in two parameters, a number and a string specifying the desired morphology.

In the following example, we want to get the number `124` in plural, masculine and nominative form.  
```
> from numi import spell_out
> print(spell_out(124, "ft_kk_nf")

> ["eitt hundrað tuttugu og fjórir", "hundrað tuttugu og fjórir"]
```

The spell_out function parses the input string so that the order of the values is not irrelevant. If one or all of the three values (number, gender, case) Numi will fill in all possible forms for that number. Note that the output will contain the string for the form values. 

In the following example, the value for the case is omitted and Numi will fill in all possible declensions
```

> print(spell_out((92, "ft_kvk"))
>  [[92, 'ft_kvk_nf', ['níutíu og tvær']], 
    [92, 'ft_kvk_þf', ['níutíu og tvær']],
    [92, 'ft_kvk_þgf', ['níutíu og tveimur', 'níutíu og tveim']],
    [92, 'ft_kvk_ef', ['níutíu og tveggja']]]
```

All the abbreviations for the input string are as follows:

| Abbr. | English    | Icelandic  |
| ----- | ---------- | ---------- |
| et    | singular   | eintala    |
| ft    | plural     | fleirtala  |
|       |            |            |
| kk    | masculine  | karlkyns   |
| kvk   | feminine   | kvenkyns   |
| hk    | neuter     | hvorugkyns |
|       |            |            |
| nf    | nominative | nefnifall  |
| þf    | accusative | þolfall    |
| þgf   | dative     | þágufall   |
| ef    | genitive   | eignafall  |

The Icelandic number system isn't the simplest (to state it lightly). The numbers one to four are declined for the respective cases and genders, of them the number `1` has both a singular and plural form. Other numbers are not declined, except for those that are actually nouns.

Numbers other than 1-4 that are also not nouns have the shorthand: 
```
at_af (án tölu og án fallbeygingar) 
``` 
(This is probably not a linguistically correct term and will be changed once the author is scolded by a linguist)


## Contributing
This package is a work in progress. Rough ideas of development are listed in the project status. 

There are probably some error that can be found and comments and corrects are highly welcomed. 

To contribute please install the requiements file and use the `tests/test_numi.py` file with `pytest` for development testing.

Setting up:
```
python venv .venv
python -m pip install -r requirements_dev.txt
pip install -e .
pytest
```



## Project status
* 0.0.6 
    - Support for numbers between 1-999
    - Add test script for development
    - Document the abbreviations
* 0.0.7 - Parse user input in a robust way/  
* 0.0.8 - Add numbers support for numbers 1,000-999,999
  
Future work
* Adding the first decimal place for all numbers
* Add CLI support 

## License
MIT
# py2srbcyr

Python module that transliterates text from Latin to [Cyrillic alphabet](https://en.wikipedia.org/wiki/Serbian_Cyrillic_alphabet).

The module is Python implementation of great Javascript [Ћирилизатор - Cyrillizer](https://github.com/turanjanin/cirilizator).

Модул за пресловљавање латиничног текста на српску ћирилицу.

## Употреба

    from py2srbcyr import SerbCyr
    ...
    cir = SerbCyr()
    print(cir.text_to_cyrillic('Zdravo svete!'))

## Тестирање

Да бисте програм тестирали неопходно је да имате инсталиран модуо `pytest`. Пошто сте га инсталирали, на командној линији из коренског директоријума задајте:

    python -m pytest

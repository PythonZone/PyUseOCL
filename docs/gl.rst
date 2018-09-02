.. .. coding=utf-8

gl - Glossary Models
====================

Examples
--------

::

    glossary model Medium
        | ceci `est` la description de `un` élément
        | dans `un` contexte `uno` et `deux`
        | `un` `test`

    Trois
        | a
        package: technical
        synonyms: Uno One
        inflections: unite uns
        label: "un"
        translations
            en: ""
            es: ""


    Reference
        |
        | `une` `référence` est un peu plus que
        | `deux` mot. Attention à l'`indentation`
        | qui doit être toujours de `huit` espaces.
        synonyms : a b c
        package : a


    Deux
        | ceci est la description de `un` élément
        | dans `un` contexte `uno` et `deux`
        | `un` `test`
        | trois
        package: a

    ZIO
        | packaef
        package: b

    ODK
        | Order Designed Kant
        package: a


Entries
-------

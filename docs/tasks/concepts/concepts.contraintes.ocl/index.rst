..  _`tâche concepts.contraintes.ocl`:

tâche concepts.contraintes.ocl
==============================

:résumé: L'objectif de cette tâche est de traduire les contraintes
    exprimées en langage naturel en contraintes OCL.

:langage:  :ref:`ClassScript1`
:artefacts:
    * ``classes/classes.cl1``


(A) Contraintes
---------------

L'expression des contraintes en langage naturel est indispensable pour
garantir l'alignement avec les contraintes métier (business rules).
Sans cela le logiciel ne correspondera pas au besoin du client. Dans
cette tâche il s'agit d'aller plus loin en formalisant ces contraintes
en langage OCL, le langage standardisé d'UML pour les contraintes.
Voir la `feuille de résumé OCL`_  pour des précisions sur le langage OCL.
Vérifier que la traduction en OCL est fidèle à la contrainte en
langage naturel.

..  note::

    Pour rappel, par abus de langage nous utilisons les termes
    "contraintes" et "invariants" de manière interchangeable.
    Les autres types de contraintes (pré et post conditions) ne sont
    pas considérée dans la mesure où les opérations ne sont pas
    prises en compte.

(B) Tests positifs
------------------

Vérifier que l'ensemble des modèles d'objets (positifs) ne
génèrent aucune erreur. Utiliser la commande ``use -qv`` pour cela.
Si des erreurs sont produites cela veut dire que les contraintes
sont trop restrictives.

(C) Tests négatifs
------------------

Vérifier que les tests négatifs concernant telle ou telle contrainte
produisent bien les violations escomptées. Si toutes les violations
attendues ne sont pas produites alors c'est que les contraintes écrites
ne sont pas assez restrictives. Revoir les contraintes dans ce cas là.

(Z) Suivi et status
-------------------

**Suivi**: Des questions ou des hypothèses ? Voir la
:ref:`tâche projet.suivis`.

**Status**: Avant de terminer cette tâche écrire le status. Voir la
:ref:`tâche projet.status`.


..  _`feuille de résumé OCL`:
    https://scribestools.readthedocs.io/en/latest/_downloads/UMLOCL-CheatSheet-18.pdf

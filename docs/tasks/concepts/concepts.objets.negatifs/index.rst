.. _`tâche concepts.objets.negatifs`:

tâche concepts.objets.negatifs
==============================

:résumé: L'objectif de cette tâche est (1) de créer des modèles négatifs
    d'objets et (2) que ces modèles génèrent les erreurs escomptées.

:langage:  :ref:`ObjectScript1`
:artéfacts:
    * ``objets/no<N>/no<N>.ob1``
    * ``objets/status.md``


(A) Création
------------

Les modèles négatifs d'objets donnent lieu soit à des violations de
cardinalités, soit à des violations de contraintes. Il s'agit dans
cette tâches d'écrire un ou plusieurs modèles d'objets négatifs.
Chaque violation attendue doit être déclarée dans le modèle.
Se référer à la documentation concernant les :ref:`violations` pour plus
de détails.

(B) Vérification
----------------

Une fois les violations déclarées dans les modèles d'objets négatifs
il s'agit de vérifier, pour chaque modèle, que les violations ont
bien lieu. Utiliser pour cela l'outil USE. Les violations de cardinalités
sont indiquées dans la section ``Cheching structure...``. Les
violations de contraintes sont indiquées dans la section
``Checking invariants...``. Si une violation n'est pas détectée, soit la
contrainte (ou la cardinalité) est erronée (ou non implémentée),
soit le modèle d'objets est incorrect.

(Z) Suivi et status
-------------------

**Suivi**: Des questions ou des hypothèses ? Voir la
:ref:`tâche projet.suivis`.

**Status**: Avant de terminer cette tâche écrire le status. Voir la
:ref:`tâche projet.status`.
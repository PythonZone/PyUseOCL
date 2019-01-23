tache:objets
============

:résumé: L'objectif de cette tâche est (1) de traduire les modèles d'objets
    textuels en  modèle d'objets annotés en :ref:`ObjectScript1`,
    (2) de compiler ces modèles d'objets et (3) de créer des diagrammes
    d'objets.

:langage:  :ref:`ObjectScript1`
:résultat:
    * ``objects/o<N>/o<N>.ob1``
    * ``objects/o<N>/diagrams/o<N>.obd.olt``
    * ``objects/o<N>/diagrams/o<N>.obd.png``
    * ``objects/status.md``


(A) Objectif
------------

Cette tâche consiste à traduire les modèles d'objets (états) décrits sous
forme textuelle en un modèle d'objets annoté. Chaque modèle d'objets se
concrétise en un fichier ``.ob1`` exécutable. Ces fichiers vont être 
utilisés pour valider le modèle de classes (fichier ``.cl1``).
Il s'agit de répéter les étapes ci-dessous pour chaque modèle d'objets
dans le répertoire ``objects/``.

(B) Traduire des états en langage ObjectScript
----------------------------------------------

Le fichier ``objects/o<N>/o<N>.ob1`` (où N est un entier)
contient un  modèle d'objets décrit en langue naturelle.
Il s'agit de plus de traduire chaque ligne en utilisant le langage 
:ref:`ObjectScript1` lorsque nécessaire.

Lorsqu'une valeur n'est pas définie utiliser une instruction
``... := Undefined``. Dans certains cas il peut être pertinent "d'inventer"
une valeur ou des valeurs. Dans ce cas mettre une note dans le modèle de suivi.
Certaines valeurs ne sont pas fondamentales (par exemple la valeur de
certains attributs) alors que d'autres sont plus importantes car le
scénario en dépend de manière plus ou moins directe.

Faire au mieux sachant que l'objectif est de traduire un texte fourni
par (ou écrit en collaboration avec) le client. Il sera est peut être
nécessaire de voir avec lui comment compléter/valider la description
d'un modèle d'objets sachant qu'un tel modèle pourra par la suite être
utilisés pour établir des tests et en particulier des tests de recette.

(C) Vérifier l'alignement avec le modèle de classes
---------------------------------------------------

Vérifier que l'état est aligné avec le modèle de classes.
Pour cela utiliser la commande suivante à partir du répertoire principal ::

    use -qv classes/classes.cl1 objects/o<N>/o<N>.ob1

L'interpreteur affichera les éventuelles erreurs de syntaxe
ainsi que les erreurs de types ou de cardinalités. Si rien ne s'affiche
cela signifie qu'aucune erreur n'a été trouvée.

(D) Créér un diagramme d'objets
-------------------------------

Produire un diagramme d'objets représentant le modèle d'objets ``objects/o<N>``.
Pour cela utiliser la même technique que pour les diagrammes de classes.
La disposition des objets doit autant que possible refléter
la disposition du diagramme de classes. 

Observer la présence ou non d'objets isolés. Vérifier s'il s'agit d'un
problème dans le scénario lui même ou un problème dans la traduction qui en
a été faite.

(Z) Suivi et status
-------------------

**Suivi**: Si des questions ou des hypothèses surgissent lors de ce travail
appliquer les :ref:`règles relatives au suivi <Tracks_Rules>`.

**Status**: Avant de terminer cette tâche écrire le status en appliquant
les :ref:`règles relatives au status <Status>`.
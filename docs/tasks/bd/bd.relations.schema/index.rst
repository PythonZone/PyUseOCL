..  _`tâche bd.relations.schema`:


tâche bd.relations.schema
=========================

:résumé: Cette tâche a pour objectif de créer le schéma relationnel,
    à partir du modèle de classes si celui-ci existe.

:langage: :ref:`RelationScript`
:artéfacts:
    * ``relations/relations.res``


Introduction
------------

Le modèle de relations doit être créé à partir du modèle de classes,
s'il existe. Il s'agit plus précisemment de créer le "schéma" relationnel,
c'est à dire l'ensemble des relations et des contraintes que l'on peut
déduire à partir du modèle de classes-relations. Dans un second temps
seulement, d'éventuels jeux de données (datasets) seront ajoutés. Dans
ce travail on se limite à la création du schéma. Aucun contenu n'est
créé.

(A) Transformations
-------------------

Si le modèle de relations est créé à partir de zero (sans modèle
de classe alors cette partie peut être ignorée ainsi que toute
référence à la notion de transformation de modèle.

Lorsque des règles de transformation "standards" existent alors celles-ci
doivent être respectées à chaque fois que faire ce peut. Plus précisemment
si une liste précise de transformations nommées a été fournie, il s'agit
alors d'indiquer voir de justifier l'application de ces transformations
(mot-clé ``transformation`` et ``rule``). Ajouter un commentaire
lorsque les  règles standards ne peuvent pas être appliquées directement.

(B) Contraintes
---------------

Définir les contraintes intégrité suivantes:

* les contraintes sur les colonnes (p.e. contraintes de domaine, mot
  clé ``dom``),

* les contraintes de clés (mot clé ``key``). Rappel: la notation
  "souligné" indique simplement que la colonne soulignée fait partie
  d'au moins une clé. Il peut y avoir plusieurs clés et une clé
  peut être composite. Ces informations ne peuvent pas être déduites
  de la notation "soulignée". Les contraintes de clés doivent donc
  être exprimées explicitement.

* les contraintes d'intégrité référentielle (par exemple
  ``R[x] C= S[y]``),

* les autre contraintes. Si une contrainte ne peut pas être exprimées
  avec le modèle relationnel, celle-ci doit être spécifiée. Si cette
  contrainte provient du modèle de classes conceptuel, alors répéter
  uniquement le nom de la contrainte (par exemple
  ``constraint AtLeastForItemPerDay``).

(Z) Suivi et status
-------------------

**Suivi**: Des questions ou des hypothèses ? Voir la
:ref:`tâche projet.suivis`.

**Status**: Avant de terminer cette tâche écrire le status. Voir la
:ref:`tâche projet.status`.
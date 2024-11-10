# Application-pour-la-gestion-des-couches-ArcGIS
Interface de gestion des couches :

Afficher la liste des couches : La fonction Afficher_liste charge et affiche les couches disponibles dans une géodatabase spécifiée.
Ajouter une couche : La fonction ajouter_couche permet de créer une nouvelle couche avec un nom et un type choisis par l'utilisateur. Les types de couches disponibles incluent POINT, MULTIPOINT, POLYGON, POLYLINE, et MULTIPATCH.
Modifier une couche : La fonction modifier_couche permet de renommer une couche et de changer son type.
Gestion des attributs de couches :

Ajouter un champ : Ajouter_champ ajoute un nouveau champ à une couche existante, avec un nom et un type spécifiés (e.g., TEXT, FLOAT, DATE).
Supprimer un champ : Supprimer_champ supprime un champ existant d’une couche sélectionnée.
Modifier un champ : Modifier_champ change le nom et le type d’un champ existant.
Gestion des enregistrements de couches :

Ajouter un enregistrement : ajouter_enregistrement_couche_arcgis ajoute une nouvelle entrée dans une couche sélectionnée. Elle permet de saisir des valeurs pour chaque champ requis.
Supprimer un enregistrement : supprimer_enregistrement permet de supprimer un enregistrement d’une couche en fonction de son OBJECTID.
Gestion des fichiers et erreurs :

Importer une géodatabase : importer_gdb permet de sélectionner un dossier de géodatabase (GDB) et de le définir comme chemin de travail pour les opérations suivantes.
Gestion des erreurs : Plusieurs fonctions, telles que Erreur et messagebox.showerror, affichent des messages d'erreur pour aider l'utilisateur à éviter des erreurs fréquentes, telles que la sélection d'une couche inexistante.


# Aperçu

*GenerateMNT* est un plugin QGIS 3.

*GenerateMNT*  permet de générer un MNT Raster à partir des données RGE ALTI de l'IGN qui peuvent être téléchargées via le lien suivant pour chaque département :
https://geoservices.ign.fr/rgealti

*GenerateMNT* a été développé par Antoine Sensier ([*UMR TETIS*](https://www.umr-tetis.fr) / [*INRAE*](http://www.inrae.fr)).

# Paramètres

Le plugin prend trois données en entrées :
 - *Zone d'étude* : Polygone représentant la zone d'étude, qui permet de selectionner les dalles qui intersectent cette zone.
 -  *Dalles des MNT* : Shapefile qui représente la zone d'étude sous forme de maille de 1000 mètres de côté. Pour chaque dalle, un champ indique le nom du Raster ASC correspondant. La couche se trouve généralement dans le répertoire 3_SUPPLEMENTS_LIVRAISON_...
 - *Dossier de fichiers MNT ASC*: Ce dossier à selectionner comprend l'ensemble des dalles sous forme de fichiers ASC. Il se trouve généralement dans le dossier 1_DONNEES_LIVRAISON_.../RGEALTI_MNT_1M_ASC_...

Le fichier de sortie est un raster MNT au format tif, qui correspond au mozaïquage des dalles selectionnées via la zone d'études, construit grace à un raster virtuel.

# Contact

*Développement* : Antoine Sensier (antoine.sensier@inrae.fr)

*Coordination* : Jennifer Amsallem (jennifer.amsallem@inrae.fr)


# Installation

Pour installer *AntoineSensier* dans *QGIS*, aller dans le menu *Extensions->Installer/Gérer les extensions->Installer depuis un zip* et sélectionner l'archive *GenerateMNT.zip*.

Les algorithmes apparaissent alors dans la boîte à outils de traitement.


# Développeurs


Pour installer le git :  
> git clone https://github.com/AntoineSensier/GenerateMNT.git
>
> cd GenerateMNT

Sous Windows, le répertoire des plugins *QGIS* est *C:/Users/user/AppData/Romaing/QGIS/QGIS3/profiles/default/python/plugins*.

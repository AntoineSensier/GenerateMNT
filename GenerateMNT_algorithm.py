# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GenerateMNT
                                 A QGIS plugin
 generate MNT raster from RGE ALTI files
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-31
        copyright            : (C) 2023 by Antoine Sensier, INRAE
        email                : antoine.sensier@inrae.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Antoine Sensier, INRAE'
__date__ = '2023-03-31'
__copyright__ = '(C) 2023 by Antoine Sensier, INRAE'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingUtils
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsVectorLayer
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsFeatureRequest
from .qgis_lib_mc import utils, qgsUtils
from qgis import processing
import os


class GenerateMNTAlgorithm(QgsProcessingAlgorithm):
    
    EXTENT_ZONE = 'ExtentZone'
    GRID_INPUT = 'GridInput'
    FOLDER_MNT_FILES = 'FolderMntFiles'
    OUTPUT_RASTER_MNT = 'OutputRasterMNT'
    FIELD_DALLE = 'NOM_DALLE'
    
    results = {}
    
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.EXTENT_ZONE, self.tr("Zone d'étude"), [QgsProcessing.TypeVectorPolygon]))
        
        self.addParameter(QgsProcessingParameterVectorLayer(self.GRID_INPUT, self.tr('dalles'), defaultValue=None))
        
        self.addParameter(QgsProcessingParameterFile(self.FOLDER_MNT_FILES, self.tr('Dossier de fichiers MNT ASC'), behavior=QgsProcessingParameterFile.Folder, fileFilter='Tous les fichiers (*.*)', defaultValue=None))
        
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_RASTER_MNT, 'Fichier de sortie Raster MNT', createByDefault=True, defaultValue=None))

    def parseParams(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters,self.EXTENT_ZONE,context)
        self.inputExtent = source.materialize(QgsFeatureRequest(),feedback=feedback)
        
        self.inputGrid = self.parameterAsVectorLayer(parameters, self.GRID_INPUT, context)
        self.outputRasterMNT = self.parameterAsOutputLayer(parameters,self.OUTPUT_RASTER_MNT,context)
        
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        step = 0
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        outputs = {}

        self.parseParams(parameters,context,feedback)
         
        # Extraire par localisation
        temp_file_extract = QgsProcessingUtils.generateTempFilename('temp_file_extract.gpkg')
        alg_params = {
        'INPUT': self.inputGrid,
        'INTERSECT': self.inputExtent,
        'PREDICATE': [0],
        'OUTPUT': temp_file_extract }
        res = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        bn = os.path.basename(temp_file_extract)
        layer_name_of_path = os.path.splitext(bn)[0]
        layer = QgsVectorLayer(temp_file_extract, layer_name_of_path, "ogr")

        step+=1
        feedback.setCurrentStep(step)
        if feedback.isCanceled():
            return {}
        
        # Remplacement des "\\" par des "/" dans le chemin du dossier
        temp_path_folder = parameters[self.FOLDER_MNT_FILES].split("\\")
        temp_path_folder = '/'.join(temp_path_folder)
        
        # Récupération des indices des dalles selectionnées
        # Ajoute les noms des fichiers asc en fonction de la sélection
        list_grids_raster = []
        fields = layer.fields()
        selected_grids_index = []
        if fields.indexOf(self.FIELD_DALLE) > -1:
            features = layer.getFeatures()
            i=0
            for feature in features:
                field_value = feature[self.FIELD_DALLE]
                split_value = ""
                if i==0:
                    if "EXT" in field_value:
                        split_value="EXT"
                    elif "FXX" in field_value:
                        split_value="FXX"
                    else:
                        break
                selected_grids_index.append(field_value.split(split_value)[1][0:10])
            list_grids_raster = []
            for grid_index in selected_grids_index:
                for file in os.listdir(temp_path_folder):
                    if grid_index in file and file.endswith('.asc'):
                        list_grids_raster.append(temp_path_folder+'/'+file)
                        break
            
        if len(list_grids_raster) == 0:
            utils.internal_error("The extent zone intesect no grid")
            
        # Construire un vecteur virtuel
        alg_params = {
            'INPUT': list_grids_raster,
            'RESOLUTION':0,
            'SEPARATE':False,
            'PROJ_DIFFERENCE':False,
            'ADD_ALPHA':False,
            'ASSIGN_CRS':layer.crs(),
            'RESAMPLING':0,
            'SRC_NODATA':'',
            'EXTRA':'',
            'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConstruireUnVecteurVirtuel'] = processing.run('gdal:buildvirtualraster', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        step+=1
        feedback.setCurrentStep(step)
        if feedback.isCanceled():
            return {}

        # Convertir le raster virtuel en raster
        alg_params = {
            'COPY_SUBDATASETS': False,
            'DATA_TYPE': 0,  # Utiliser le type de donnée de la couche en entrée
            'EXTRA': '',
            'INPUT': outputs['ConstruireUnVecteurVirtuel']['OUTPUT'],
            'NODATA': None,
            'OPTIONS': 'COMPRESS=DEFLATE',
            'TARGET_CRS': layer.crs(),
            'OUTPUT': self.outputRasterMNT
        }
        self.results['RasterMNT'] = processing.run('gdal:translate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
        
        step+=1
        feedback.setCurrentStep(step)
        if feedback.isCanceled():
            return {}
            
        return self.results

    def name(self):
        return 'GenerateMNTfromRGEALTI'

    def displayName(self):
        return self.tr('Create MNT from RGEALTI')

    # def group(self):
        # return self.tr('Misc')

    # def groupId(self):
        # return 'Misc'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
        
    def createInstance(self):
        return GenerateMNTAlgorithm()

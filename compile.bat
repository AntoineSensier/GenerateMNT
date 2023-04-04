@echo off
call "C:\Program Files\QGIS 3.22.15\bin\o4w_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc

if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
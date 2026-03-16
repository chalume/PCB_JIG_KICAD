# PCB_JIG_KICAD
Tool for automated creation of PCB jigs for solder mask and manual componements placement for Rhino

1-export_openings.py : tool for delimiting jig opening for each package, based on kicad file and kicad STEP export. This program will preview openings and step delimitation of each package and export it to .svg. You can adjust opening sizes with optionnal X or Y shift, and control inter opening distance for 3D printing of the masks. The toll will export a .dxf file with openings and PCB cutout. The BOTTOM LAYER parameter will mirror the component when expored. The EXPORT_PACKAGES list allows to export only the designated packages. All PCB components are exported if the list is empty, you can use this lits to export top lay first then mirrored components for bottom layer.

2-rhino_import_openings.py : Python script to be mauched from Rhino7. Import the previously created .dxf File and creates componment placement jig and solder mask alignment. Various parameters of the jigs can be adjusted.


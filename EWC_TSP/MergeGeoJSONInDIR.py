import os
import glob
import processing

# Set the directory containing the geojson files
dir_path = r"C:\Users\jdeur\OneDrive\Documents\TSP_Projs\EWC_TSP\MST_Cut"

# Get a list of all geojson files in the directory
geojson_files = glob.glob(os.path.join(dir_path, "*to*"))

# Initialize a QgsVectorLayer object to hold the merged data
merged_layer = QgsVectorLayer("Line", "merged", "memory")

# Loop through the geojson files and add their features to the merged layer
for geojson_file in geojson_files:
    layer_name = os.path.splitext(os.path.basename(geojson_file))[0]
    layer = QgsVectorLayer(geojson_file, layer_name, "ogr")
    if not layer.isValid():
        print(f"Layer {layer_name} is invalid")
        continue
    merged_layer.dataProvider().addFeatures(layer.getFeatures())

# Save the merged layer to a geojson file
merged_file = os.path.join(dir_path, "merged.geojson")
#QgsVectorFileWriter.writeAsVectorFormat(merged_layer, merged_file, "UTF-8", merged_layer.crs(), "GeoJSON")
#QgsVectorFileWriter.writeAsVectorFormatV3(merged_layer, merged_file,QgsCoordinateTransformContext(),QgsVectorFileWriter.SaveVectorOptions())
processing.run("native:mergevectorlayers", {"LAYERS":geojson_files,"OUTPUT":merged_file})
print("Done, file is at "+str(merged_file))
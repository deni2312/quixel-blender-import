import bpy
import os

def import_fbx_files_in_grid_with_textures(folder_path):

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".fbx"):

                file_path = os.path.join(root, file)
                

                bpy.ops.import_scene.fbx(filepath=file_path)
                

                imported_object = bpy.context.selected_objects[0]
                
                clear_materials(imported_object)

                apply_textures_from_folder(imported_object, root)


def clear_materials(obj):
    if obj.data.materials:
        obj.data.materials.clear()

def apply_textures_from_folder(obj, folder_path):

    texture_files = {
        "BaseColor": None,
        "Metalness": None,
        "Roughness": None,
        "Normal": None,
    }

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        file_lower = file.lower()
        
        if "basecolor" in file_lower and file_lower.endswith(".jpg"):
            texture_files["BaseColor"] = file_path
        elif "metalness" in file_lower and file_lower.endswith(".jpg"):
            texture_files["Metalness"] = file_path
        elif "roughness" in file_lower and file_lower.endswith(".jpg"):
            texture_files["Roughness"] = file_path
        elif "normal" in file_lower and file_lower.endswith(".jpg"):
            texture_files["Normal"] = file_path


    material = bpy.data.materials.new(name=f"{obj.name}_Material")
    material.use_nodes = True
    obj.data.materials.append(material)
    

    nodes = material.node_tree.nodes
    links = material.node_tree.links


    for node in nodes:
        nodes.remove(node)

    def create_and_link_texture(tex_type, tex_path, bsdf_input):
        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(tex_path)
        tex_node.label = tex_type

        links.new(tex_node.outputs["Color"], bsdf_input)

    principled_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    links.new(principled_bsdf.outputs["BSDF"], output_node.inputs["Surface"])


    if texture_files["BaseColor"]:
        create_and_link_texture("BaseColor", texture_files["BaseColor"], principled_bsdf.inputs["Base Color"])
    if texture_files["Metalness"]:
        create_and_link_texture("Metalness", texture_files["Metalness"], principled_bsdf.inputs["Metallic"])
    if texture_files["Roughness"]:
        create_and_link_texture("Roughness", texture_files["Roughness"], principled_bsdf.inputs["Roughness"])
    if texture_files["Normal"]:
        normal_map_node = nodes.new(type="ShaderNodeNormalMap")
        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(texture_files["Normal"])
        tex_node.label = "Normal"
        links.new(tex_node.outputs["Color"], normal_map_node.inputs["Color"])
        links.new(normal_map_node.outputs["Normal"], principled_bsdf.inputs["Normal"])


folder_path = "/location/quixel/"

import_fbx_files_in_grid_with_textures(folder_path)

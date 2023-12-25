#Optimises blockbench structure models by connecting planes with the same texture
#Also adds the display data and changes texture to pixel

import json
import sys
import numpy
import subprocess
import os

def modify_binary_arr(texture_id,face,layer,x,y):
    if layer not in binary_array_dict[texture_id][face]:
        binary_array_dict[texture_id][face][layer] = numpy.zeros((32, 32), dtype=int)
    binary_array_dict[texture_id][face][layer][x,y] = 1

def get_planes(bin_arr):
    input_str = ' '.join(map(str, bin_arr.flatten()))  
    p=subprocess.Popen(rectangle_dissector_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    p.stdin.writelines(input_str+"\n") 
    p.stdin.flush()
    return p.stdout.read().split("\n")[:-1]

file_name = input("Enter file name: ")

rectangle_dissector_path = os.path.abspath('./dissector')
model_path = os.path.abspath(os.path.join(os.getcwd(), file_name))

if not os.path.exists(model_path):
    print(f"Error: File at '{model_path}' not found.")
    sys.exit(1)

with open(model_path, 'r') as file:
    data = json.load(file)

print("Loaded {}".format(file_name))

if 'credit' in data:
    del data['credit']

if 'display' not in data:
    data['display'] = {"head":{"translation":[0,12.4,0],"scale":[1.54,1.54,1.54]}}

print("Splitting into texture layers")

#Put Voxel into binary layers
binary_array_dict = dict()
for texture_id, texture in data["textures"].items():

    data["textures"][texture_id] = texture.replace("block/","pixel/pixel_").replace("_concrete","").replace("_planks","")

    binary_array_dict[texture_id] = dict()
    for face in ["north", "south", "west", "east", "down", "up"]:
        binary_array_dict[texture_id][face] = dict()

for cube in data['elements']:
    texture_id = next(iter(cube["faces"].values()))["texture"][1:]
    a = int(cube["from"][0]*2)
    b = int(cube["from"][1]*2)
    c = int(cube["from"][2]*2)
    for face, value in cube["faces"].items():
        match face:
            case "west":
                modify_binary_arr(texture_id,"west",a,b,c)
            case "east":
                modify_binary_arr(texture_id,"east",a,b,c)
            case "down":
                modify_binary_arr(texture_id,"down",b,a,c)
            case "up":
                modify_binary_arr(texture_id,"up",b,a,c)
            case "north":
                modify_binary_arr(texture_id,"north",c,a,b)
            case "south":
                modify_binary_arr(texture_id,"south",c,a,b)

new_elements = list()

for texture, faces in binary_array_dict.items():
    print("Converting texture layer {}".format(data["textures"][texture]))
    for face, arr_dict in faces.items():
        for layer, arr in arr_dict.items():
            plane_list = get_planes(arr)
            for plane in plane_list:
                new_cube = dict()
                level = int(layer)*0.5
                plane = plane.split(" ")
                from1 = int(plane[0])*0.5
                from2 = int(plane[1])*0.5
                to1 = round(int(plane[2])*0.5+0.501,3)
                to2 = round(int(plane[3])*0.5+0.501,3)

                match face:
                    case "west":
                        new_cube["from"] = [level,from1,from2]
                        new_cube["to"] = [level,to1,to2]
                    case "east":
                        new_cube["from"] = [level+0.5,from1,from2]
                        new_cube["to"] = [level+0.5,to1,to2]
                    case "down":
                        new_cube["from"] = [from1,level,from2]
                        new_cube["to"] = [to1,level,to2]
                    case "up":
                        new_cube["from"] = [from1,level+0.5,from2]
                        new_cube["to"] = [to1,level+0.5,to2]
                    case "north":
                        new_cube["from"] = [from1,from2,level]
                        new_cube["to"] = [to1,to2,level]
                    case "south":
                        new_cube["from"] = [from1,from2,level+0.5]
                        new_cube["to"] = [to1,to2,level+0.5]
                
                new_cube["faces"] = {face: {"uv": [0, 0, 16, 16],"texture": "#"+texture}}
                new_elements.append(new_cube)

data['elements'] = new_elements

#Write the modified data back to the file
json_string = json.dumps(data, separators=(',', ':'))

with open(model_path, 'w') as file:
    file.write(json_string)

print("Done") 
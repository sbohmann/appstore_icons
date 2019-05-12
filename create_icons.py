import json
import os
import re
import sys

from wand.image import Image

if len(sys.argv) != 3:
    raise ValueError('Excpecting two arguments: <path to icon set> <path to original image>')

icon_set_directory = sys.argv[1]
original_image = Image(filename=sys.argv[2])

size_description = re.compile(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)')
scale_description = re.compile(r'(\d+(?:\.\d+)?)')

definition_path = os.path.join(icon_set_directory, 'Contents.json')


def run():
    with open(definition_path, 'r', encoding='utf-8') as file:
        text = file.read()
        decoder = json.JSONDecoder()
        content = decoder.decode(text)
    
    print(content)

    for image in content['images']:
        definition_output_path = image['idiom'] + '-' + image['size'] + '@' + image['scale'] + '.png'
        width, height = parse_size(image['size'], image['scale'])
        image['filename'] = definition_output_path
        create_scaled_image(definition_output_path, width, height)
        print(image)

    definition_output_path = definition_path + '.out'
    with open(os.path.join(icon_set_directory, definition_output_path), 'w', encoding='utf-8') as file:
        encoder = json.JSONEncoder(indent=2, separators=(', ', ' : '))
        text = encoder.encode(content)
        file.write(text)
        os.remove(definition_path)
        os.rename(definition_output_path, definition_path)


def parse_size(size, scale):
    size_match = size_description.match(size)
    if not size_match:
        raise ValueError('Illegal size description [' + size + ']')
    scale_match = scale_description.match(scale)
    if not scale_match:
        raise ValueError('Illegal scale description [' + scale + ']')
    factor = float(scale_match[1])
    return scaled_int(size_match[1], factor), scaled_int(size_match[2], factor)


def scaled_int(text, factor):
    result = float(text) * factor
    return rounded_int(result)


def rounded_int(value):
    return int(round(value))


def create_scaled_image(output_filename, width, height):
    if width != height:
        raise ValueError('width: ' + str(width) + ', height: ' + str(height))
    image = Image(original_image)
    image.resize(width, height)
    output_path = os.path.join(icon_set_directory, output_filename)
    image.save(filename=output_path)
    

run()

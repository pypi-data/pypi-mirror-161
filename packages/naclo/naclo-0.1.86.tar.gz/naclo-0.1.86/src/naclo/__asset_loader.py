from importlib import resources
import json


with resources.open_text('naclo.assets', 'bleach_default_params.json') as f:
    bleach_default_params = json.load(f)

with resources.open_text('naclo.assets', 'bleach_default_options.json') as f:
    bleach_default_options = json.load(f)
    
with resources.open_text('naclo.assets', 'binarize_default_params.json') as f:
    binarize_default_params = json.load(f)

with resources.open_text('naclo.assets', 'binarize_default_options.json') as f:
    binarize_default_options = json.load(f)

with resources.open_text('naclo.assets', 'recognized_bleach_options.json') as f:
    recognized_bleach_options = json.load(f)
    
with resources.open_text('naclo.assets', 'recognized_binarize_options.json') as f:
    recognized_binarize_options = json.load(f)

with resources.open_text('naclo.assets', 'recognized_units.json') as f:
    recognized_units = json.load(f)

with resources.open_text('naclo.assets', 'recognized_salts.json') as f:
    recognized_salts = json.load(f)

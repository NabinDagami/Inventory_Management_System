with open('robust_importer.py', 'r') as f:
    lines = f.readlines()

# Build replacement (line 64 to 114, 0-indexed 63 to 113)
new_section = [
    "        self.column_patterns = {\n",
    "            'name': [\n",
    "                r'^.*name.*$', r'^.*bike.*$', r'^.*company.*$', \n",
    "                r'^.*item.*$', r'^.*product.*$', r'^.*model.*$'\n",
    "            ],\n",
    "            'sku': [\n",
    "                r'^sku$', r'^code$', r'product.*code',\n",
    "            ],\n",
    "            'category': [\n",
    "                r'^category$', r'^type$',\n",
    "            ],\n",
    "            'brand': [\n",
    "                r'^brand$', r'^company$', r'^manufacturer$',\n",
    "            ],\n",
    "            'stock': [\n",
    "                r'^qty.*hand$', r'^stock$', r'^quantity$', r'^available.*stock$',\n",
    "            ],\n",
    "            'qty_sold': [\n",
    "                r'^qty.*sold$', r'^sold$',\n",
    "            ],\n",
    "            'price_normal': [\n",
    "                r'^retail.*', r'^price.*', r'^normal.*',\n",
    "            ],\n",
    "            'price_workshop': [\n",
    "                r'^wholesale.*', r'^workshop.*', r'^w/s.*', r'^ws.*',\n",
    "            ],\n",
    "            'cost_price': [\n",
    "                r'^cost.*price$', r'^purchase.*price$',\n",
    "            ],\n",
    "            'reorder_level': [\n",
    "                r'^reorder.*level$', r'^min.*stock$',\n",
    "            ],\n",
    "            'description': [\n",
    "                r'^description$',\n",
    "            ],\n",
    "            'status': [\n",
    "                r'^status$',\n",
    "            ]\n",
    "        }\n"
]

# Keep header line (63) but replace 64-114
new_lines = lines[:63] + new_section + lines[114:]

with open('robust_importer.py', 'w') as f:
    f.writelines(new_lines)

print('Updated patterns')

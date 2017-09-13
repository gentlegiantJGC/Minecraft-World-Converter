In this folder are all the json files that define how blocks, tile entities, entities... should be converted

All the different versions get converted to an intermediate system where every block type, tile entity, entity... are supported. They are then converted out to the desired version where unsupported things will be removed.

#blockMapping
using <inputVersion>_intermediate.json the blocks can be converted to the intermediate system.
using intermediate_<outputVersion>.json the blocks can be converted to the output version.
Every block that exists in the inputVersion should exist in the <inputVersion>_intermediate.json file and every id that exists in the intermediate system should exist in the intermediate_<outputVersion>.json file. In the latter blocks, that don't exist in the output version should map to air thus essentially deleting them.
There are certain cases where nbt will have to be looked up to find the new block id/ data value and vice versa. The code to do this has already been written however no examples have been added to the json files and the code has not really been tested. An example that would use this are shulker boxes. In java, shulker boxes store their colour in different block ids and their rotation in different data values. In bedrock, shulker boxes all have the same block id with colour being stored under the data value and rotation being stored in nbt. Just one example where things can get complicated quickly.
It is worth noting that this isn't where the general tile entity conversion code will go. This is only for conversions revolving around converting block id/data value. General tile entity conversion goes in the tileEntityMapping section.

#tileEntityMapping and entityMapping
tile entity and entity mappings differ slightly from the block mappings in that instead of having multiple files to convert to the intermediate system there is only one (_intermediate.json). This is because there isn't the issue of one input mapping to multiple outputs like there are with block ids.
at the time of writing all the main conversion code that isn't id mappings is done within the main script however ideally this would be converted to json files to reduce the amount of duplicated code and simplify the main script.

#itemMapping
Item mappings are similar to block mappings however (at the time of writing) they don't need nbt lookup and they extend further than just blocks. In the java version items are stored by their string id whereas in bedrock they are stored by their numerical id.
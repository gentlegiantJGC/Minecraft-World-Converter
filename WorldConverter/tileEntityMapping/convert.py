import json
import directories
from WorldConverter.itemMapping.convert import convertItem
blockEntityToIntermediate = json.load(open(directories.getFiltersDir()+'/WorldConverter/tileEntityMapping/_intermediate.json'))

blockEntityFromIntermediate = {}
blockEntityFromIntermediate['PC'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/tileEntityMapping/intermediate_java.json'))
blockEntityFromIntermediate['PE'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/tileEntityMapping/intermediate_bedrock.json'))

from pymclevel import TAG_List, TAG_Byte, TAG_Int, TAG_Compound, TAG_Short, TAG_Double, TAG_String, TAG_Float

def convertBlockEntity(convertFrom, convertTo, te):
	if convertFrom == convertTo:
		return
	if 'id' not in te:
		del te
	if te['id'].value not in blockEntityToIntermediate:
		raise Exception('{} is not a known block entity name'.format(te['id'].value))
	intermediateID = blockEntityToIntermediate[te['id'].value]
	
	# conversion code here
	# something recursive would probably be required in the long term
	
	if intermediateID == 'minecraft:flower_pot':
		if convertFrom == 'PC':
			if 'Item' in te:
				itemID = te['Item'].value
				del te['Item']
			else:
				itemID = 'minecraft:air'
				# raise Exception('Item definition not in te:{}'.format(te))
			if 'Data' in te:
				itemData = te['Data'].value
				del te['Data']
			else:
				itemData = 0
		elif convertFrom == 'PE':
			if 'item' in te:
				itemID = te['item'].value
				del te['item']
			else:
				itemID = 0
				# raise Exception('Item definition not in te:{}'.format(te))
			if 'mData' in te:
				itemData = te['mData'].value
				del te['mData']
			else:
				itemData = 0
				
		itemIDNew, itemDataNew = convertItem(convertFrom, convertTo, itemID, itemData)
		
		if convertTo == 'PC':
			te['Item'] = TAG_String(itemIDNew)
			te['Item'] = TAG_Int(itemDataNew)
		elif convertTo == 'PE':
			te['item'] = TAG_Short(itemIDNew)
			te['mData'] = TAG_Int(itemDataNew)
			
	elif intermediateID == 'minecraft:bed':
		if convertFrom in ['PC', 'PE']:
			if 'color' in te:
				colour = te['color'].value
				del te['color']
			else:
				colour = 14
		
		if convertTo == 'PC':
			te['color'] = TAG_Int(colour)
		elif convertTo == 'PE':
			te['color'] = TAG_Byte(colour)
		
	
	# elif intermediateID == 'minecraft:chest':
		# if PC
			# change things unique to a chest
			# change inventory
			# convertInventory(convertFrom, convertTo, te)
	
	if intermediateID not in blockEntityFromIntermediate[convertTo]:
		raise Exception('{} is not a known block entity name'.format(te['id'].value))
	if blockEntityFromIntermediate[convertTo][intermediateID] is None:
		del te
	else:
		te['id'] = TAG_String(blockEntityFromIntermediate[convertTo][intermediateID])
		
		
		
# def convertInventory(convertFrom, convertTo, te):
	# if PC
		# copy tag to the correct location and convert item using the item mappings
		# convertItem(...)
	# if PE
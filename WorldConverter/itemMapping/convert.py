import json
import directories
itemToIntermediate = {}
itemToIntermediate['PC'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/itemMapping/java_intermediate.json'))
itemToIntermediate['PE'] = {}
							 
itemFromIntermediate = {}
itemFromIntermediate['PC'] = {}
itemFromIntermediate['PE'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/itemMapping/intermediate_bedrock.json'))

def convertItem(convertFrom, convertTo, itemID, itemData):#, nbtIn=None, fallBack = False):
	if convertFrom == convertTo:
		return itemID, itemData
	try:
		intermediateID = itemToIntermediate[convertFrom][str(itemID)][str(itemData)]['intermediateID']
		itemIDNew = itemFromIntermediate[convertTo][intermediateID]['id']
		itemDataNew = itemFromIntermediate[convertTo][intermediateID]['data']	
		return itemIDNew, itemDataNew
	except:
		pass
		#put except code here
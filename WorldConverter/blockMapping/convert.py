# import json
import directories
blockToIntermediate = {}
blockToIntermediate['PC'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/blockMapping/java_intermediate.json'))
blockToIntermediate['PE'] = {}							  
# add json mappings here for the other versions
blockFromIntermediate = {}
blockFromIntermediate['PC'] = {}
blockFromIntermediate['PE'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/blockMapping/intermediate_bedrock.json'))
# add json mappings here for the other versions

def convertBlock(convertFrom, convertTo, blockID, blockData, nbtIn=None, fallBack = False):
	# check the conversion options are valid
	if convertFrom not in ['PC','PE'] or convertTo not in ['PC','PE']:
		raise Exception('{} to {} is not a valid conversion method'.format(convertFrom, convertTo))
	
	try:
		nbtOut = None
		# if the block mapping requires nbt
		if 'nbt' in blockToIntermediate[convertFrom][str(blockID)][str(blockData)] and not fallBack:
			# if fallBack is false and the tile entity has not been defined return -1
			# this happens when doing the whole chunk
			if nbtIn is None:
				return -1,-1, nbtOut
			else:
				# if nbt has been defined then use it to find the intermediate id
				intermediateID = blockToIntermediate[convertFrom][str(blockID)][str(blockData)]
				# multiple keys can be checked. They are stored recursively
				while 'nbt' in intermediateID:
					intermediateID = intermediateID['value'][nbtIn[intermediateID['key']].value]
				intermediateID = intermediateID['intermediateID']
		# otherwise use the normal intermediate id
		else:
			intermediateID = blockToIntermediate[convertFrom][str(blockID)][str(blockData)]['intermediateID']
		
		if 'nbt' in blockFromIntermediate[convertTo][intermediateID]:
			nbtOut = blockFromIntermediate[convertTo][intermediateID]['nbt']
		
		return blockFromIntermediate[convertTo][intermediateID]['id'], blockFromIntermediate[convertTo][intermediateID]['data'], nbtOut

	except BaseException as e:
		# if there is an error with the block mapping then leave everything as it was and let the user know
		# print traceback.print_exc()
		# print e
		# print 'convertFrom:{},convertTo:{},blockID:{},blockData:{},nbtIn:,fallBack:{}'.format(convertFrom,convertTo,blockID,blockData,nbtIn,fallBack)
		return -2, -2, None
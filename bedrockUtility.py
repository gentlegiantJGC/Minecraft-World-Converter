displayName = "World Converter"

inputs = (
	("Convert From",("PC","PE")),
	("Convert To",("PE","PC")),
)

import json
import directories
import numpy as np
import copy
from pymclevel import TAG_List, TAG_Byte, TAG_Int, TAG_Compound, TAG_Short, TAG_Double, TAG_String, TAG_Float
strToNBT = {'byte': TAG_Byte, 'int': TAG_Int, 'short': TAG_Short, 'double': TAG_Double, 'string': TAG_String, 'float': TAG_Float}
from pymclevel import leveldbpocket
from pymclevel import mclevel
from pymclevel.leveldbpocket import PocketLeveldbWorld
import mcplatform
import traceback
blockToIntermediate = {}
blockToIntermediate['PC'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/blockMapping/java_intermediate.json'))
blockToIntermediate['PC'] = {}							  
# add json mappings here for the other versions
blockFromIntermediate = {}
blockFromIntermediate['PE'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/blockMapping/intermediate_bedrock.json'))
blockFromIntermediate['PC'] = {}
# add json mappings here for the other versions

blockEntityToIntermediate = json.load(open(directories.getFiltersDir()+'/WorldConverter/tileEntityMapping/_intermediate.json'))
blockEntityFromIntermediate = {}
blockEntityFromIntermediate['PE'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/tileEntityMapping/intermediate_bedrock.json'))
blockEntityFromIntermediate['PC'] = {}
itemToIntermediate = {}
itemToIntermediate['PC'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/itemMapping/java_intermediate.json'))
itemToIntermediate['PC'] = {}							 
itemFromIntermediate = {}
itemFromIntermediate['PE'] = json.load(open(directories.getFiltersDir()+'/WorldConverter/itemMapping/intermediate_bedrock.json'))
itemFromIntermediate['PC'] = {}

requiresBlockEntity = {}
requiresBlockEntity['PE'] = [26,29,33,54,146]
requiresBlockEntity['PC'] = []



def perform(level, box, options):
	skippedBlocks = []
	# if level.gameVersion == 'PE':
		# convertFrom = 'PE'
	# elif level.gameVersion in ['javalevel','1.12']:
		# convertFrom = 'PC'
	# else:
		# raise Exception('world type {} i	# if level.gameVersion == 'PE':
		# convertFrom = 'PE'
	# elif level.gameVersion in ['javalevel','1.12']:
		# convertFrom = 'PC'
	# else:
		# raise Exception('world type {} is not currently supported'.format(level.gameVersion))
		
		
	convertFrom = options['Convert From']	
	convertTo = options['Convert To']
		
	# # load PE world
	# if convertTo == 'PE':
		# filePath = None
		# filePath = mcplatform.askOpenFile(title="Select a Pocket world to write to", schematics=False)
		# if filePath is not None:
			# if PocketLeveldbWorld._isLevel(filePath):
				# if leveldbpocket.leveldb_available:
					# levelNew = PocketLeveldbWorld(filePath)
				# else:
					# raise Exception("Pocket support has failed")
			# else:
				# raise Exception("Not a Pocket world")
	
	# for (chunk, _, _) in level.getChunkSlices(box):
		# cx, cz = chunk.chunkPosition
		# generateChunk(levelNew, True, cx, cz, 15)
		# chunkNew = levelNew.getChunk(cx, cz)
		# chunkNew.Blocks[:] = copy.deepcopy(chunk.Blocks)
		# chunkNew.Data[:] = copy.deepcopy(chunk.Data)
		# chunkNew.TileEntities = copy.deepcopy(chunk.TileEntities)
		# chunkNew.Entities = copy.deepcopy(chunk.Entities)
		# chunkNew.dirty = True
	# levelNew.saveInPlaceGen()
	# levelNew.close()
	
	
 
	# needs cleaning up (ideally idenfifying map by actual map type rather than user input?)
	# or just merge these into one since it is a bit redunent at this point
	if convertFrom == 'PC':
		filePath = None
		filePath = mcplatform.askOpenFile(title="Select a PC world to read from", schematics=False)
		if filePath is not None:
			levelOld = mclevel.fromFile(filePath)
		else:
			raise Exception('no file given')
	elif convertFrom == 'PE':
		filePath = None
		filePath = mcplatform.askOpenFile(title="Select a PC world to read from", schematics=False)
		if filePath is not None:
			levelOld = mclevel.fromFile(filePath)
		else:
			raise Exception('no file given')
	
	chunksDone = 0
	for chunkOldCoords in levelOld.allChunks:
		cx, cz = chunkOldCoords
		chunkOld = levelOld.getChunk(cx, cz)
		generateChunk(level, True, cx, cz, 15)
		chunk = level.getChunk(cx, cz)
		chunk.Blocks[:] = copy.deepcopy(chunkOld.Blocks)
		chunk.Data[:] = copy.deepcopy(chunkOld.Data)
		chunk.TileEntities = copy.deepcopy(chunkOld.TileEntities)
		chunk.Entities = copy.deepcopy(chunkOld.Entities)
		
		# get a list of all the unique blocks
		chunkBlockList = np.unique(np.add(chunkOld.Blocks*16,chunkOld.Data))
		# go through every block in that list and find the converted id, data and tile entity
		for block in chunkBlockList:
			blockID = block >> 4
			blockData = block % 16
			blockIDNew, blockDataNew, nbtNew = convertBlock(convertFrom, convertTo, blockID, blockData)
			# if  blockIDNew is equal to -1 then there is a tile enitity requirement
			if blockIDNew == -1:
				# for every location with that block id+data combo
				for coord in np.argwhere(np.logical_and(chunkOld.Blocks == blockID, chunkOld.Data == blockData)):
					x,z,y = coord
					x += cx * 16
					z += cz * 16
					# get the tile entity
					te = level.tileEntityAt(x,y,z)
					if te is None:
						# if the tile entity does not exist, use fallback id
						blockIDNew, blockDataNew, nbtNew = convertBlock(convertFrom, convertTo, blockID, blockData, fallBack = True)
						if nbtNew is not None:
							te = createBlockEntity(chunk, convertTo, blockIDNew, x, y, z)
					else:
						# if it does exist 
						blockIDNew, blockDataNew, nbtNew = convertBlock(convertFrom, convertTo, blockID, blockData, te)
					level.setBlockAt(x,y,z,blockIDNew)
					level.setBlockDataAt(x,y,z,blockDataNew)
					if te is not None and nbtNew is not None:
						# merge nbtNew with tile entity
						for nbtToSet in nbtNew:
							te[nbtToSet['key']] = strToNBT['nbtType'](nbtToSet['value'])
						
			# if -2 then there was an exception
			elif blockIDNew == -2:
				# print chunkOldCoords
				# print block
				# raise Exception
				skippedBlocks.append((blockID,blockData))
			elif blockIDNew != blockID or blockDataNew != blockData:
				convertTheseBlocks = np.logical_and(chunkOld.Blocks == blockID, chunkOld.Data == blockData)
				if blockIDNew != blockID:
					chunk.Blocks[convertTheseBlocks] = blockIDNew
				if blockDataNew != blockData:
					chunk.Data[convertTheseBlocks] = blockDataNew
			if nbtNew is not None and blockIDNew not in [-1,-2]:
				# for all blocks where there was not a tile entity requirement
				for coord in np.argwhere(np.logical_and(chunkOld.Blocks == blockID, chunkOld.Data == blockData)):
					x,z,y = coord
					x += cx * 16
					z += cz * 16
					# get the tile entity
					te = level.tileEntityAt(x,y,z)
					if te is None:
						te = createBlockEntity(chunk, convertTo, blockIDNew, x, y, z)
					# merge nbtNew with tile entity
					for nbtToSet in nbtNew:
						te[nbtToSet['key']] = strToNBT['nbtType'](nbtToSet['value'])
			if blockIDNew in requiresBlockEntity[convertTo]:
				for coord in np.argwhere(np.logical_and(chunkOld.Blocks == blockID, chunkOld.Data == blockData)):
					x,z,y = coord
					x += cx * 16
					z += cz * 16
					if level.tileEntityAt(x,y,z) is None:
						createBlockEntity(chunk, convertTo, blockIDNew, x, y, z)
		for te in chunk.TileEntities[:]:
			convertBlockEntity(convertFrom, convertTo, te)
			
		for e in chunk.Entities[:]:
			convertEntity(convertFrom, convertTo, e)
			
		# biomes
		# if convertFrom == 'PC':
			# if chunkOld.root_tag and 'Level' in chunkOld.root_tag.keys() and 'Biomes' in chunkOld.root_tag["Level"].keys():
				# array = chunkOld.root_tag["Level"]["Biomes"].value
			# else:
				# array = np.ones(256)
		# elif convertFrom == 'PE':
			# array = fromstring(chunkOld.Biomes.tostring(), 'uint8')
			
		# if convertTo == 'PC':
			# if chunk.root_tag and 'Level' in chunk.root_tag.keys() and 'Biomes' in chunk.root_tag["Level"].keys():
				# chunk.root_tag["Level"]["Biomes"].value = array
		# elif convertTo == 'PE':
			# array.shape = (16,16)
			# chunk.Biomes = array
		
		
		
		
		
		
		
		chunk.dirty = True
		chunksDone += 1
		print '{}/{}'.format(chunksDone,len(list(levelOld.allChunks)))
	if skippedBlocks != []:
		print skippedBlocks
	levelOld.close()
		


def generateChunk(level, generateBase, cx, cz, y, flatworldIDs=[]):
	try:
		# get the chunk object
		chunk = level.getChunk(cx, cz)
	except:		
		if generateBase:
			level.createChunk(cx,cz)
			chunk = level.getChunk(cx, cz)
		
		else:
			raise Exception()
	# terrain tag in the format (version x1, blocks (air) x4096, block data x4096*0.5, sky light x4096*0.5, block light x4096*0.5)

	if level.gameVersion == 'PE':
		# for every chunk up to the top of the selection box
		for i in range(y+1):
			# if the sub-chunk does not already exist
			if i not in chunk.subchunks:
				if type(flatworldIDs) is not list:
					raise Exception('flatworldIDs must be a list of block ids')
				if len(flatworldIDs) < i*16+1:
					blockIDsChunk = [0]*16
				elif len(flatworldIDs) > (i+1)*16:
					blockIDsChunk = flatworldIDs[i*16:(i+1)*16]
				else:
					blockIDsChunk = flatworldIDs[i*16:] + [0] * (16 - (len(flatworldIDs) - i*16))
					
				if len(blockIDsChunk) != 16:
					raise Exception('blockIDsChunk not the right size')
				blocks = ''.join([chr(block) for block in blockIDsChunk])
				terrain = chunk.version
				for _ in range(256):
					terrain += blocks
				terrain += '\x00'*2048+'\x00'*2048+'\x00'*2048
				# create it with the terrain value created earlier
				chunk.add_data(terrain=terrain, subchunk=i)
	# tell MCedit the chunk has changed
	chunk.dirty = True
	
	
	
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
		
def convertBlockEntity(convertFrom, convertTo, te):
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
				raise Exception('Item definition not in te:{}'.format(te))
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
				raise Exception('Item definition not in te:{}'.format(te))
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
		
	
	if intermediateID not in blockEntityFromIntermediate[convertTo]:
		raise Exception('{} is not a known block entity name'.format(te['id'].value))
	if blockEntityFromIntermediate[convertTo][intermediateID] is None:
		del te
	else:
		te['id'] = TAG_String(blockEntityFromIntermediate[convertTo][intermediateID])
		
def createBlockEntity(chunk, convertTo, block, x, y, z):
	if convertTo == 'PE':
		# bed block
		if block == 26:
			te = TAG_Compound()
			te["color"] = TAG_Byte(14)
			te["id"] = TAG_String(u'Bed')
			te["x"] = TAG_Int(x)
			te["y"] = TAG_Int(y)
			te["z"] = TAG_Int(z)
			chunk.addTileEntity(te)
		# sticky piston
		elif block == 29:		
			te = TAG_Compound()		
			te["AttachedBlocks"] = TAG_List()		
			te["BreakBlocks"] = TAG_List()		
			te["id"] = TAG_String(u'PistonArm')		
			te["isMovable"] = TAG_Byte(1)		
			te["LastProgress"] = TAG_Float()		
			te["NewState"] = TAG_Byte()		
			te["Progress"] = TAG_Float()		
			te["State"] = TAG_Byte()		
			te["Sticky"] = TAG_Byte(1)		
			te["x"] = TAG_Int(x)		
			te["y"] = TAG_Int(y)		
			te["z"] = TAG_Int(z)		
			chunk.addTileEntity(te)
		# normal piston
		elif block == 33:		
			te = TAG_Compound()		
			te["AttachedBlocks"] = TAG_List()		
			te["BreakBlocks"] = TAG_List()		
			te["id"] = TAG_String(u'PistonArm')		
			te["isMovable"] = TAG_Byte(1)		
			te["LastProgress"] = TAG_Float()		
			te["NewState"] = TAG_Byte()		
			te["Progress"] = TAG_Float()		
			te["State"] = TAG_Byte()		
			te["Sticky"] = TAG_Byte(0)		
			te["x"] = TAG_Int(x)
			te["y"] = TAG_Int(y)
			te["z"] = TAG_Int(z)
			chunk.addTileEntity(te)
		# chests
		elif block in [54,146]:
			te = TAG_Compound()
			te["Items"] = TAG_List()
			te["id"] = TAG_String(u'Chest')
			te["x"] = TAG_Int(x)
			te["y"] = TAG_Int(y)
			te["z"] = TAG_Int(z)
			chunk.addTileEntity(te)
		else:
			raise Exception('block {} is not currently supported for making tile entities'.format(block))
	# elif convertTo == 'PC':
	
	else:
		raise Exception('{} is an unsupported conversion type'.format(convertTo))
		
	return te
	
def convertEntity(convertFrom, convertTo, e):
	print 'convert entity'
	
def convertItem(convertFrom, convertTo, itemID, itemData):#, nbtIn=None, fallBack = False):

	# itemToIntermediate
	# itemFromIntermediate

	if convertFrom == 'PC':
		intermediateID = itemToIntermediate['PC'][str(itemID)][str(itemData)]['intermediateID']
		# look up the string id and data to find the intermediate id
	# elif convertFrom == 'PE':
		# look up the numerical id and data to find the intermediate id
	else:
		raise Exception('{} is an unsupported conversion type'.format(convertFrom))
		
	# if convertTo == 'PC':
		# look up the intermediate id to find the string id and data
	if convertTo == 'PE':
		itemIDNew = itemFromIntermediate['PE'][intermediateID]['id']
		itemDataNew = itemFromIntermediate['PE'][intermediateID]['data']
		# look up the intermediate id to find the numerical id and data
	else:
		raise Exception('{} is an unsupported conversion type'.format(convertTo))
		
	return itemIDNew, itemDataNew

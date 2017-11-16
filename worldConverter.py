displayName = "World Converter"
filter_version = "1.0.0"

inputs = (
	("Convert From",("PC","PE")),
	("Convert To",("PE","PC")),
	("NBT", ("Delete", "Keep")),
	("Biomes", (True)),
	("Break Every", (10000)),
)

import json
import directories
import numpy as np
import copy
from pymclevel import TAG_List, TAG_Byte, TAG_Int, TAG_Compound, TAG_Short, TAG_Double, TAG_String, TAG_Float
strToNBT = {'byte': TAG_Byte, 'int': TAG_Int, 'short': TAG_Short, 'double': TAG_Double, 'string': TAG_String, 'float': TAG_Float}
from pymclevel import mclevel
import mcplatform


requiresBlockEntity = {}
requiresBlockEntity['PE'] = [26,29,33,54,146]
requiresBlockEntity['PC'] = []

def perform(level, box, options):
	import WorldConverter
	reload(WorldConverter)

	answer = None
	try:
		update_data = urllib2.urlopen('https://raw.githubusercontent.com/gentlegiantJGC/Minecraft-World-Converter/master/version.txt').read().split(';')
		if filter_version != update_data[0]:
			#this part I found in the MCedit source code so credit to the MCedit team
			answer = albow.ask(
				('Version {} is available').format(update_data[0]),
				[
					'Download',
					'Ignore'
				],
				default=0,
				cancel=1
			)
	except:
		print 'Tried checking if there was an update however there was an issue'
		
	if answer == "Download":
		from mcplatform import platform_open
		platform_open(update_data[1])
		raise Exception(update_data[2].replace('\\n', '\n\n'))

	skippedBlocks = []
	convertFrom = options['Convert From']	
	convertTo = options['Convert To']
	if convertFrom == convertTo:
		raise Exception("due to some bug that I can't work out this doesn't currently work")
		
 
	# needs cleaning up (ideally idenfifying map by actual map type rather than user input?)
	filePath = None
	filePath = mcplatform.askOpenFile(title="Select a PC world to read from", schematics=False)
	if filePath is not None:
		levelOld = mclevel.fromFile(filePath)
	else:
		raise Exception('no file given')
	
	if len(list(levelOld.allChunks)) > options["Break Every"]:
		chunksDonePath = None
		chunksDonePath = mcplatform.askOpenFile(title="Select somewhere to save chunk list", schematics=False)
		if chunksDonePath is not None:
			chunksDoneFO = open(chunksDonePath).read()
			if chunksDoneFO == '':
				chunksDoneList = []
			else:
				chunksDoneList = json.loads(chunksDoneFO)
		else:
			raise Exception('no file given')
	else:
		chunksDoneList = []
		chunksDonePath = None
	
	# level.showProgress("Processed 0 chunks of {}".format(len(list(levelOld.allChunks))),)
	
	# def convertWorld
	chunksDone = 0
	import time
	t = time.time()
	for chunkOldCoords in levelOld.allChunks:
		cx, cz = chunkOldCoords
		if [cx,cz] in chunksDoneList:
			chunksDone += 1
			continue
		else:
			chunksDoneList.append(chunkOldCoords)
		chunkOld = levelOld.getChunk(cx, cz)
		generateChunk(level, True, cx, cz, 15)
		chunk = level.getChunk(cx, cz)
		chunk.Blocks[:] = copy.deepcopy(chunkOld.Blocks)
		chunk.Data[:] = copy.deepcopy(chunkOld.Data)
		if options["NBT"] == "Delete":
			for e in chunk.TileEntities[:]:
				del e
			for e in chunk.Entities[:]:
				del e
		
		for e in chunkOld.TileEntities:
			# try:
				
			# except:
				# pass
			chunk.TileEntities.append(copy.deepcopy(e))
		'''
		copying entities to bedrock seems to cause issues so removed this code until a fix is found
		for e in chunkOld.Entities:
			chunk.Entities.append(copy.deepcopy(e))
		'''
			# chunk.TileEntities = copy.deepcopy(chunkOld.TileEntities)
			# chunk.Entities = copy.deepcopy(chunkOld.Entities)
		#else:
			#need to work out how to copy entities across to the PC version. The above code errors
		
		# get a list of all the unique blocks
		chunkBlockList = np.unique(np.add(chunkOld.Blocks*16,chunkOld.Data))
		# go through every block in that list and find the converted id, data and tile entity
		for block in chunkBlockList:
			blockID = block >> 4
			blockData = block % 16
			blockIDNew, blockDataNew, nbtNew = WorldConverter.convertBlock(convertFrom, convertTo, blockID, blockData)
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
						blockIDNew, blockDataNew, nbtNew = WorldConverter.convertBlock(convertFrom, convertTo, blockID, blockData, fallBack = True)
						if nbtNew is not None:
							te = WorldConverter.createBlockEntity(chunk, convertTo, blockIDNew, x, y, z)
					else:
						# if it does exist 
						blockIDNew, blockDataNew, nbtNew = WorldConverter.convertBlock(convertFrom, convertTo, blockID, blockData, te)
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
						te = WorldConverter.createBlockEntity(chunk, convertTo, blockIDNew, x, y, z)
					# merge nbtNew with tile entity
					for nbtToSet in nbtNew:
						te[nbtToSet['key']] = strToNBT['nbtType'](nbtToSet['value'])
			if blockIDNew in requiresBlockEntity[convertTo]:
				for coord in np.argwhere(np.logical_and(chunkOld.Blocks == blockID, chunkOld.Data == blockData)):
					x,z,y = coord
					x += cx * 16
					z += cz * 16
					if level.tileEntityAt(x,y,z) is None:
						WorldConverter.createBlockEntity(chunk, convertTo, blockIDNew, x, y, z)
		for te in chunk.TileEntities[:]:
			WorldConverter.convertBlockEntity(convertFrom, convertTo, te)
			
		for e in chunk.Entities[:]:
			WorldConverter.convertEntity(convertFrom, convertTo, e)
			
		# biomes
		if options['Biomes']:
			if convertFrom == 'PC':
				if chunkOld.root_tag and 'Level' in chunkOld.root_tag.keys() and 'Biomes' in chunkOld.root_tag["Level"].keys():
					array = copy.deepcopy(chunkOld.root_tag["Level"]["Biomes"].value)
				else:
					array = np.ones(256)
			elif convertFrom == 'PE':
				array = np.fromstring(chunkOld.Biomes.tostring(), 'uint8')
			if convertTo == 'PC':
				if chunk.root_tag and 'Level' in chunk.root_tag.keys() and 'Biomes' in chunk.root_tag["Level"].keys():
					chunk.root_tag["Level"]["Biomes"].value = array
			elif convertTo == 'PE':
				array.shape = (16,16)
				for biomeID in np.unique(array):
					chunk.Biomes[array == biomeID] = biomeID
				# chunk.Biomes[:] = array
		
		
		
		
		
		
		
		chunk.chunkChanged()
		chunksDone += 1
		print '{}/{}'.format(chunksDone,len(list(levelOld.allChunks)))
		if chunksDone % options["Break Every"] == options["Break Every"] - 1:
			break
	if skippedBlocks != []:
		WorldConverter.bugReport(submitThis='skippedBlocks:{}'.format(skippedBlocks))
		# print skippedBlocks
		
		
	# for _ in levelNew.saveInPlaceGen():
		# pass
		
		
		
	levelOld.close()
	print time.time() - t
	if chunksDonePath is not None:
		chunksDoneFO = open(chunksDonePath,'w')
		json.dump(chunksDoneList, chunksDoneFO)
		chunksDoneFO.close()


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
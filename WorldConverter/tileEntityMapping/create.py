from pymclevel import TAG_List, TAG_Byte, TAG_Int, TAG_Compound, TAG_Short, TAG_Double, TAG_String, TAG_Float

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
import wcs



def doCommand(userid):
	userid = int(userid)
	wcs.wcs.wcsplayers[userid].save()

	wcs.wcs.tell(int(userid), '\x04[WCS] \x05You have saved your \x04levels.')

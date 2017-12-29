import wcs



def doCommand(userid):
	userid = str(userid)
	if userid in wcs.wcs.tmp:
		tmp[userid].save()
	if userid in wcs.wcs.tmp1:
		tmp1[userid].save()
	if userid in wcs.wcs.tmp2:
		for x in tmp2[userid]:
			tmp2[userid].save()

	wcs.wcs.tell(int(userid), '\x04[WCS] \x05You have saved your \x04levels.')

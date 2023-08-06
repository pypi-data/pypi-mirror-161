#!/usr/bin/env python3

# XML
#import dicttoxml
import xmltodict

#{{{ xml tools
# XML -> dict
def fromxml(xmldata):
	# TODO: funciona?
	#return dicttoxml.parse("<xml>"+xmldata+"</xml>", disable_entities=True)["xml"]
	return xmltodict.parse(xmldata)
def readxml(xmlfile):
	f=open(xmlfile,"rt")
	xml=f.read()
	data=fromxml(xml)
	return data
#}}}

#! /usr/bin/env python3
import sys
import getopt
import re


def getargs():
	margs = {}
	options,remainder = getopt.getopt(sys.argv[1:], '',['name=','file='])

	for opt,arg in options:
		if opt=='--name':
			margs['name'] = arg
		elif opt=='--file':
			margs['file'] = arg

	return margs

def main():
	args = getargs()
	ifile = args['file']
	mm = args['name']

	with open(ifile,'r') as f:
		contents = f.read()

	pattern = re.compile(r'(-config) (\w+)')
	matches = pattern.finditer(contents)
	for match in matches:
		print(match)
	#pp = pattern.sub(r'\1 '+ mm ,contents)
	#print(pp)

if __name__ == "__main__":
	main()

#!/usr/bin/python
from Parser.RuleParser import *
from Parser.SnortConf import *
from Generator.Payload import *
from optparse import OptionParser
import os,sys
import re

class r2a:
	#Initial function sets global variables used throughout the class
	#Calls parseConf and loadRules to parse the snort configuration
	#file as well as load in the snort rules to generate packets
	def __init__(self, options):
		#Command line options
		self.options = options
		#Snort conf variables
		self.snort_vars = SnortConf(self.options.snort_conf).parse()
		#Snort rules
		self.rules = self.loadRules(self.options.rule_file)
		#Packet generator
		self.ContentGen = ""

	def main(self):
		#Regexp for avoid comments and empty lines
		pcomments = re.compile('^\s*#')
		pemptylines = re.compile('^\s*$')
		rules_loaded = 0
		#Go through each snort rule
		for snort_rule in self.rules:
			snort_rule = snort_rule.strip()
			#Parse the snort rule using the snort parser
			comments = pcomments.search(snort_rule)
			emptylines = pemptylines.search(snort_rule)
			#If it's not a comment or an empty line...
			if not comments and not emptylines:
				try:
					r = Rule(snort_rule)
					self.ContentGen = PayloadGenerator(r.contents)

					self.ContentGen.src = self.snort_vars[r.rawsources[1:]]
					self.ContentGen.dst = self.snort_vars[r.rawdestinations[1:]]
					self.ContentGen.proto  = r.proto

					self.ContentGen.parseComm(r.rawsrcports, r.rawdesports, self.snort_vars)
					#packets = self.ContentGen.build()

					self.ContentGen.build_handshake()
					
					for p in self.ContentGen.packets:
						print p.summary()
		
					#ContentGen = PayloadGenerator(r.contents)
		
					#payload = ContentGen.build()
		
					#print ContentGen
					rules_loaded = rules_loaded + 1
				except:
					traceback.print_exc()
					print "Parser failed with rule: " + snort_rule
					continue
		print "Loaded "+str(rules_loaded)+" rules succesfully!"

	#Reads in the rule file specified by the user
	def loadRules(self, rule_file):
		f = open(rule_file, 'r')
		rules = f.read().splitlines()
		f.close()

		return rules

#Parses arguments that are passed in through the cli
def parseArgs():
	usage = "usage: ./r2a.py -f rule_file -c snort_config -w pcap"
	parser = OptionParser(usage)
	
	parser.add_option("-f", help="Read in snort rule file", action="store", type="string", dest="rule_file")
	parser.add_option("-c", help="Read in snort configuration file", action="store", type="string", dest="snort_conf")
	parser.add_option("-w", help="Name of pcap file", action="store", type="string", dest="pcap")

	(options, args) = parser.parse_args(sys.argv)

	r = r2a(options)
	r.main()

if __name__ == "__main__":
	parseArgs()



import os
import typing

import jk_json


from ..DirectedGraph import DirectedGraph
from ..ILink import ILink
from ..INode import INode






class SimpleEdgeListIO(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	@staticmethod
	def loadFromFile(filePath:str) -> DirectedGraph:
		jData = jk_json.loadFromFile(filePath)

		if isinstance(jData, dict):
			return SimpleEdgeListIO.loadFromJSONDict(jData)
		elif isinstance(jData, list):
			return SimpleEdgeListIO.loadFromJSONList(jData)
		else:
			raise TypeError(repr(type(jData)))
	#

	@staticmethod
	def loadFromJSONDict(jData:dict) -> DirectedGraph:
		return SimpleEdgeListIO.loadFromJSONList(jData["edges"])
	#

	@staticmethod
	def loadFromJSONList(jEdgeList:list) -> DirectedGraph:
		g = DirectedGraph()

		nodeIDs = set()
		for jEdge in jEdgeList:
			nodeIDs.add(jEdge[0])
			nodeIDs.add(jEdge[1])
		for nodeID in sorted(nodeIDs):
			g.createNode(str(nodeID))

		for jEdge in jEdgeList:
			assert isinstance(jEdge, list)
			fromNode = g.getCreateNode(str(jEdge[0]))
			toNode = g.getCreateNode(str(jEdge[1]))
			g.createLink(fromNode, toNode)

		return g
	#

#







import os
import typing
import collections

import jk_typing


from .Node import Node
from .Link import Link







class DirectedGraph(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self):
		self.__nodesByID:typing.Dict[int,Node] = {}
		self.__nodesByName:typing.Dict[str,Node] = {}
		self.__linksByID:typing.Dict[int,Link] = {}

		self.__nextNodeID = 0
		self.__nextLinkID = 0
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def __getNodeE(self, nodeIdentifier:typing.Union[str,int,Node]) -> Node:
		if isinstance(nodeIdentifier, str):
			return self.__nodesByName[nodeIdentifier]
		elif isinstance(nodeIdentifier, int):
			return self.__nodesByID[nodeIdentifier]
		elif isinstance(nodeIdentifier, Node):
			return nodeIdentifier
		else:
			raise TypeError(type(nodeIdentifier))
	#

	def __getNodeOrNodesE(self, nodeIdentifiers:typing.Union[str,int,Node,typing.Iterable[typing.Union[int,str,Node]]]) -> typing.List[Node]:
		if isinstance(nodeIdentifiers, str):
			return [ self.__nodesByName[nodeIdentifiers] ]
		elif isinstance(nodeIdentifiers, int):
			return [ self.__nodesByID[nodeIdentifiers] ]
		elif isinstance(nodeIdentifiers, Node):
			return [ nodeIdentifiers ]

		ret = []
		for nodeIdentifier in nodeIdentifiers:
			if isinstance(nodeIdentifier, str):
				ret.append(self.__nodesByName[nodeIdentifier])
			elif isinstance(nodeIdentifier, int):
				ret.append(self.__nodesByID[nodeIdentifier])
			elif isinstance(nodeIdentifier, Node):
				ret.append(nodeIdentifier)
			else:
				raise TypeError(type(nodeIdentifier))
		return ret
	#

	def __unlinkNode(self, node:Node):
		for link in node._incomingLinks.values():
			assert isinstance(link, Link)
			fromNode:Node = link.fromNode
			del fromNode._outgoingLinks[link.linkID]
			del self.__linksByID[link.linkID]

		for link in node._outgoingLinks.values():
			assert isinstance(link, Link)
			toNode:Node = link.toNode
			del toNode._incomingLinks[link.linkID]
			del self.__linksByID[link.linkID]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Create a new node.
	# 
	# You need to provide a unique name for the node.
	# If a node with this name already exists an exception is thrown.
	#
	@jk_typing.checkFunctionSignature()
	def createNode(self, name:str) -> Node:
		if name in self.__nodesByName:
			raise Exception("Node name already in use: " + repr(name))

		nodeID = self.__nextNodeID
		self.__nextNodeID += 1

		node = Node(self, nodeID, name)

		self.__nodesByID[nodeID] = node
		self.__nodesByName[name] = node

		return node
	#

	@jk_typing.checkFunctionSignature()
	def getCreateNode(self, name:str) -> Node:
		if name in self.__nodesByName:
			return self.__nodesByName[name]

		nodeID = self.__nextNodeID
		self.__nextNodeID += 1

		node = Node(self, nodeID, name)

		self.__nodesByID[nodeID] = node
		self.__nodesByName[name] = node

		return node
	#

	@jk_typing.checkFunctionSignature()
	def getNode(self, nodeIdentifier:typing.Union[str,int]) -> Node:
		if isinstance(nodeIdentifier, str):
			return self.__nodesByName.get(nodeIdentifier)
		else:
			return self.__nodesByID.get(nodeIdentifier)
	#

	@jk_typing.checkFunctionSignature()
	def getNodeE(self, nodeIdentifier:typing.Union[str,int]) -> Node:
		if isinstance(nodeIdentifier, str):
			node = self.__nodesByName.get(nodeIdentifier)
		else:
			node = self.__nodesByID.get(nodeIdentifier)
		if node is None:
			raise Exception("No such node: " + repr(nodeIdentifier))

		return node
	#

	@jk_typing.checkFunctionSignature()
	def unlinkNode(self, nodeIdentifier:typing.Union[str,int,Node]) -> Node:
		node = self.__getNodeE(nodeIdentifier)

		self.__unlinkNode(node)

		return node
	#

	@jk_typing.checkFunctionSignature()
	def removeNode(self, nodeIdentifier:typing.Union[str,int,Node]) -> Node:
		node = self.__getNodeE(nodeIdentifier)

		self.__unlinkNode(node)
		del self.__nodesByID[node.nodeID]
		del self.__nodesByName[node.name]

		return node
	#

	@jk_typing.checkFunctionSignature()
	def removeNodes(self,
			nodeIdentifiers:typing.Union[str,int,Node,typing.Iterable[typing.Union[int,str,Node]]],
		) -> None:
		nodes = self.__getNodeOrNodesE(nodeIdentifiers)

		for node in nodes:
			self.__unlinkNode(node)
			del self.__nodesByID[node.nodeID]
			del self.__nodesByName[node.name]
	#

	def iterateAllNodes(self) -> typing.Iterable[Node]:
		yield from self.__nodesByID.values()
	#

	def iterateAllLinks(self) -> typing.Iterable[Link]:
		yield from self.__linksByID.values()
	#

	@jk_typing.checkFunctionSignature()
	def createLink(self, fromNode:typing.Union[str,int,Node], toNode:typing.Union[str,int,Node]) -> Link:
		fromNode = self.__getNodeE(fromNode)
		toNode = self.__getNodeE(toNode)

		linkID = self.__nextLinkID
		self.__nextLinkID += 1

		link = Link(self, linkID, fromNode, toNode)

		fromNode._outgoingLinks[linkID] = link
		toNode._incomingLinks[linkID] = link
		self.__linksByID[linkID] = link

		return link
	#

	def iterateConnectedNodes(self,
			nodeIdentifiers:typing.Union[str,int,Node,typing.Iterable[typing.Union[int,str,Node]]],
			bIncludedStart:bool = False,
		) -> typing.Iterable[Node]:

		startNodes = self.__getNodeOrNodesE(nodeIdentifiers)

		if bIncludedStart:
			yield from startNodes

		nodesVisited:typing.Set[Node] = set()
		nodesToProcess = collections.deque(startNodes)

		while nodesToProcess:
			curNode = nodesToProcess.popleft()

			for link in curNode._outgoingLinks.values():
				assert isinstance(link, Link)
				nodeToAdd = link.toNode
				if nodeToAdd not in nodesVisited:
					yield nodeToAdd
					nodesVisited.add(nodeToAdd)
					nodesToProcess.append(nodeToAdd)
	#

	def iterateOutgoingLinks(self,
			nodeIdentifier:typing.Union[str,int,Node],
		) -> typing.Iterable[Link]:

		curNode = self.__getNodeE(nodeIdentifier)

		yield from curNode._outgoingLinks.values()
	#

	def iterateOutgoingNodes(self,
			nodeIdentifier:typing.Union[str,int,Node],
		) -> typing.Iterable[Node]:

		curNode = self.__getNodeE(nodeIdentifier)

		for link in curNode._outgoingLinks.values():
			assert isinstance(link, Link)
			yield link.toNode
	#

	def iterateStartNodes(self) -> typing.Iterable[Node]:
		for node in self.__nodesByID.values():
			if not node._incomingLinks:
				yield node
	#

	def iterateEndNodes(self) -> typing.Iterable[Node]:
		for node in self.__nodesByID.values():
			if not node._outgoingLinks:
				yield node
	#

#









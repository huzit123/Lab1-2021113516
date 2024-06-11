# -*- coding: utf-8 -*-
from bidict import bidict
from units import parse_input
import pytest


class Lab3bTest:
    def __init__(self):
        # 单词序号双向映射map
        self.wordIndexMap = bidict({})
        # word : 1
        # 顶点表
        self.vertexTable = []
        # 边表, 即邻接矩阵, n*n, 内部数字代表出现次数
        self.edgeTable = []
        # 当前顶点数
        self.vertexNum = 0
        # 当前边(弧)数
        self.edgeNum = 0
        self.open_file_and_parse()

    def dataInit(self):
        self.wordIndexMap = bidict({})
        self.vertexTable = []
        self.edgeTable = []
        self.vertexNum = 0
        self.edgeNum = 0

    # def connect_signals(self):
    #     self.openfile.triggered.connect(self.open_file_and_parse)
    #     self.pushButton_3.clicked.connect(self.showDirectedGraph)
    #     self.pushButton_2.clicked.connect(self.queryBridgeWords)
    #     self.pushButton_4.clicked.connect(self.generateNewText)
    #     self.pushButton.clicked.connect(self.calcShortestPath)
    #     self.pushButton_5.clicked.connect(self.randomWalk)

    def open_file_and_parse(self):
        # print("open_file_and_parse() : 数据初始化")
        self.dataInit()
        filePath = "./test.txt"
        # print("load file:", filePath)
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                sentence = []
                for line in file:
                    sentence.append(line.strip())
                wordList = parse_input(sentence)
                for idx, word in enumerate(wordList):
                    if word not in self.wordIndexMap:
                        self.wordIndexMap[word] = self.vertexNum
                        self.vertexTable.append(self.vertexNum)
                        self.vertexNum += 1
                # print(self.wordIndexMap)
                n = len(self.wordIndexMap)

                # 初始化邻接矩阵
                for i in range(0, n):
                    for j in range(0, n):
                        if len(self.edgeTable) <= i:
                            self.edgeTable.append([])
                        self.edgeTable[i].append(-1)
                        if i == j:
                            self.edgeTable[i][j] = 0
                lastWordIndex = -1
                for idx, word in enumerate(wordList):
                    nowWordIndex = self.wordIndexMap[word]
                    if idx > 0:
                        if self.edgeTable[lastWordIndex][nowWordIndex] == -1:
                            self.edgeTable[lastWordIndex][nowWordIndex] = 1
                        else:
                            self.edgeTable[lastWordIndex][nowWordIndex] += 1
                        self.edgeNum += 1
                    lastWordIndex = self.wordIndexMap[word]
                # print(self.edgeTable)
                assert len(self.wordIndexMap) > 0
        except FileNotFoundError:
            print("文件不存在")

    # 查询桥接词
    def queryBridgeWords(self, words):
        # print(type(self.textEdit.toPlainText()))
        wordList = parse_input(words)
        if len(wordList) == 2:
            word1 = wordList[0]
            word2 = wordList[1]
            if word1 not in self.wordIndexMap or word2 not in self.wordIndexMap:
                output_string = "No " + str(word1) + " or " + str(word2) + " in the graph!"
                return output_string
                # self.textEdit_2.setPlainText(output_string)
            else:
                bridgeList = self.queryBridge(word1, word2)
                if bridgeList:
                    output_string = ""
                    for i in range(len(bridgeList)):
                        output_string += bridgeList[i]
                        output_string += " "
                    output_string = output_string[0:-1]
                    return output_string
                    # self.textEdit_2.setPlainText(output_string)
                else:
                    return "No bridge words from " + str(word1) + " to " + str(word2) + "!"
        else:
            return "queryBridgeWords error: wrong words"
            # return "queryBridgeWords error: wrong words"
            # self.textEdit_2.setPlainText("queryBridgeWords error: wrong words")

    def queryBridge(self, word1, word2):
        bridgeList = []
        word1Index = self.wordIndexMap[word1]
        word2Index = self.wordIndexMap[word2]
        for bridgeIndex in range(self.vertexNum):
            if self.edgeTable[word1Index][bridgeIndex] > 0 and self.edgeTable[bridgeIndex][word2Index] > 0:
                bridgeList.append(self.wordIndexMap.inverse[bridgeIndex])
        return bridgeList


@pytest.mark.parametrize("words, expected",
                         [(["strange worlds"], "new"),
                          (["forest"], "queryBridgeWords error: wrong words"),
                          (["explore forest"],"No explore or forest in the graph!"),
                          # (["explore new"],"strange"),
                          (["to explore"], "No bridge words from to to explore!"),])
def test(words, expected):
    lab3bTest = Lab3bTest()
    # print(words)
    # print(parse_input(words))
    assert lab3bTest.queryBridgeWords(words) == expected


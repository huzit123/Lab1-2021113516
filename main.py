import random
import sys
import time

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QAction, QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap
from qtPages.mainWindow import Ui_MainWindow
import matplotlib.pyplot as plt
from bidict import bidict
import networkx as nx
import cv2
from units import parse_input, dijistra, get_one_word_path


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)  # 渲染页面控件
        # 补充菜单栏
        bar = self.menuBar()
        # 向菜单栏中添加新的QMenu对象，父菜单
        self.openfile = QAction('open', self)
        self.file = bar.addMenu('File')
        self.file.addAction(self.openfile)
        self.connect_signals()  # 设置信号槽
        # 单词序号双向映射map
        self.wordIndexMap = bidict({})
        # 顶点表
        self.vertexTable = []
        # 边表, 即邻接矩阵, n*n, 内部数字代表出现次数
        self.edgeTable = []
        # 当前顶点数
        self.vertexNum = 0
        # 当前边(弧)数
        self.edgeNum = 0
        # networkx 图像
        self.graph = nx.DiGraph()
        # networkx 全局样式
        self.pos = None
        # 是否进入随机游走
        self.randomWalkFlag = True
        self.randomWalkStr = ""

    def dataInit(self):
        self.wordIndexMap = bidict({})
        self.vertexTable = []
        self.edgeTable = []
        self.vertexNum = 0
        self.edgeNum = 0

    def connect_signals(self):
        self.openfile.triggered.connect(self.open_file_and_parse)
        self.pushButton_3.clicked.connect(self.showDirectedGraph)
        self.pushButton_2.clicked.connect(self.queryBridgeWords)
        self.pushButton_4.clicked.connect(self.generateNewText)
        self.pushButton.clicked.connect(self.calcShortestPath)
        self.pushButton_5.clicked.connect(self.randomWalk)

    def open_file_and_parse(self):
        self.dataInit()
        filePath, fileType = QFileDialog.getOpenFileName(self, 'open file', '/')
        # print("load file:", filePath)
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                sentence = []
                for line in file:
                    sentence.append(line.strip())
                wordList = parse_input(sentence)
                # print(wordList)
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
                # 添加添加节点
                for i in range(len(self.vertexTable)):
                    self.graph.add_node(i, desc=str(self.wordIndexMap.inverse[i]))
                # 添加边
                for i in range(len(self.wordIndexMap)):
                    for j in range(len(self.wordIndexMap)):
                        weight = self.edgeTable[i][j]
                        # -1 为无法到达， 0 为自身
                        if weight != -1 and weight != 0:
                            self.graph.add_edge(i, j, name=weight)
                self.pos = nx.spring_layout(self.graph, k=5, iterations=50)
                self.textEdit_2.setPlainText("load file success")
        except FileNotFoundError:
            print("文件不存在")

    # 展示有向图
    def showDirectedGraph(self):
        self.generateGraph(color_list=[])
        self.frashGraph()
        self.textEdit_2.setPlainText("show directed graph")

    def changeGraphColor(self, color_list):
        self.generateGraph(color_list=color_list)
        self.frashGraph()

    def generateGraph(self, color_list):
        plt.figure(3, figsize=(12, 12))  # 这里控制画布的大小，可以说改变整张图的布局
        if color_list:
            nx.draw(self.graph, self.pos, edge_color="black", node_color=color_list, node_size=4000)
        else:
            nx.draw(self.graph, self.pos, edge_color="black", node_color="white", node_size=4000)  # 画图，设置节点大小
        node_labels = nx.get_node_attributes(self.graph, 'desc')  # 获取节点的desc属性
        nx.draw_networkx_labels(self.graph, self.pos, labels=node_labels, font_size=20)  # 将desc属性，显示在节点上
        edge_labels = nx.get_edge_attributes(self.graph, 'name')  # 获取边的name属性，
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=edge_labels, font_size=20)  # 将name属性，显示在边上
        plt.savefig("images/graph.jpg")
        plt.close()

    def frashGraph(self):
        img = cv2.imread("images/graph.jpg")  # 读取图像
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
        x = img.shape[1]  # 获取图像大小
        y = img.shape[0]
        frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        item = QGraphicsPixmapItem(pix)  # 创建像素图元
        scene = QGraphicsScene()  # 创建场景
        scene.addItem(item)
        self.graphicsView.setScene(scene)  # 将场景添加至视图

    # 查询桥接词
    def queryBridgeWords(self):

        words = [self.textEdit.toPlainText()]
        wordList = parse_input(words)
        if len(wordList) == 2:
            word1 = wordList[0]
            word2 = wordList[1]
            if word1 not in self.wordIndexMap or word2 not in self.wordIndexMap:
                output_string = "No " + str(word1) + " or " + str(word2) + " in the graph!"
                self.textEdit_2.setPlainText(output_string)
                # return output_string
            else:
                bridgeList = self.queryBridge(word1, word2)
                if bridgeList:
                    output_string = "The bridge words from " + str(word1) + " to " + str(word2) + " are: "
                    for i in range(len(bridgeList)):
                        output_string = output_string + str(bridgeList[i])
                    # 修改颜色
                    color_list = ["white" for i in range(self.vertexNum)]
                    color_list[self.wordIndexMap[word1]] = "red"
                    color_list[self.wordIndexMap[word2]] = "red"
                    self.changeGraphColor(color_list=color_list)

                    self.textEdit_2.setPlainText(output_string)
                    # return output_string
                else:
                    self.textEdit_2.setPlainText("No bridge words from " + str(word1) + " to " + str(word2) + " !")
                    # return "No bridge words from " + str(word1) + " to " + str(word2) + " !"
        else:
            self.textEdit_2.setPlainText("queryBridgeWords error: wrong words")
            # return "queryBridgeWords error: wrong words"

    def queryBridge(self, word1, word2):
        bridgeList = []
        word1Index = self.wordIndexMap[word1]
        word2Index = self.wordIndexMap[word2]
        for bridgeIndex in range(self.vertexNum):
            if self.edgeTable[word1Index][bridgeIndex] > 0 and self.edgeTable[bridgeIndex][word2Index] > 0:
                bridgeList.append(self.wordIndexMap.inverse[bridgeIndex])
        return bridgeList

    # 根据bridge word生成新文本

    def generateNewText(self):
        newWordStr = ""
        words = [self.textEdit.toPlainText()]
        wordList = parse_input(words)
        lastWord = ""
        for idx, word in enumerate(wordList):
            if idx == 0:
                newWordStr += word + " "
            else:
                if word in self.wordIndexMap and lastWord in self.wordIndexMap:
                    bridgeList = self.queryBridge(lastWord, word)
                    if bridgeList:
                        # print(random.randint(0, len(bridgeList)-1))
                        # 随机添加新词
                        newWordStr += bridgeList[random.randint(0, len(bridgeList) - 1)] + " "
                newWordStr += word + " "
            lastWord = word
        newWordStr = newWordStr[0:-1]
        self.textEdit_2.setPlainText(newWordStr)

    # 计算两个单词之间的最短路径
    def calcShortestPath(self):
        words = [self.textEdit.toPlainText()]
        wordList = parse_input(words)

        # 输入两个词，
        if len(wordList) == 2:
            word1 = wordList[0]
            word2 = wordList[1]
            if word1 not in self.wordIndexMap or word2 not in self.wordIndexMap:
                output_string = "No " + str(word1) + " or " + str(word2) + " in the graph!"
                self.textEdit_2.setPlainText(output_string)
            else:
                path, dis = dijistra(self.edgeTable, self.wordIndexMap[word1])

                checkPath, pathStr, distense, pathList = get_one_word_path(path, dis, self.wordIndexMap[word1],
                                                                           self.wordIndexMap[word2], self.wordIndexMap)

                # 修改颜色
                color_list = ["white" for i in range(self.vertexNum)]
                for word in pathList:
                    color_list[self.wordIndexMap[word]] = "red"
                self.changeGraphColor(color_list=color_list)
                if checkPath:
                    self.textEdit_2.setPlainText(pathStr + "\n" + "total length: " + str(distense))
                else:
                    self.textEdit_2.setPlainText("No path from" + str(word1) + " to " + str(word2) + " in the graph!")

        # 可选功能，输入一个单词返回到所有单词的距离，暂时没做
        # elif len(wordList) == 1:
        #     word1 = wordList[0]
        #     if word1 not in self.wordIndexMap:
        #         output_string = "No " + str(word1) + " in the graph!"
        #         self.textEdit_2.setPlainText(output_string)
        #     else:
        #         path = dijistra(self.edgeTable, self.wordIndexMap[word1])
        #         print(path)
        else:
            self.textEdit_2.setPlainText("calcShortestPath error: wrong words")

    # 随机游走, 1秒走一步, 再点击就退出并保存字符串
    def randomWalk(self):
        if self.randomWalkFlag:
            self.randomWalkStr = ""
            self.randomWalkFlag = False
            # 修改颜色
            color_list = ["white" for i in range(self.vertexNum)]

            self.textEdit_2.setPlainText("start random walk")
            nowWordIndex = random.randint(0, self.vertexNum - 1)
            # 先显示一下随机选择的单词
            time.sleep(1)
            self.randomWalkStr = "" + self.wordIndexMap.inverse[nowWordIndex]
            self.textEdit_2.setPlainText(self.randomWalkStr)
            color_list[nowWordIndex] = "red"
            self.changeGraphColor(color_list=color_list)
            QApplication.processEvents()

            # 已访问边字典
            pathDic = {}
            # 可选下个节点列表
            newWordList = []
            for i in range(self.vertexNum):
                if self.edgeTable[nowWordIndex][i] > 0:
                    newWordList.append(i)
            nextWordIndex = None
            if newWordList:
                nextWordIndex = newWordList[random.randint(0, len(newWordList) - 1)]
            # 循环进行下一步迭代
            while nextWordIndex is not None and not self.randomWalkFlag:
                time.sleep(1)
                pathDic[str(nowWordIndex) + "&" + str(nextWordIndex)] = 1
                self.randomWalkStr += " " + self.wordIndexMap.inverse[nextWordIndex]
                self.textEdit_2.setPlainText(self.randomWalkStr)
                color_list[nextWordIndex] = "red"
                self.changeGraphColor(color_list=color_list)
                QApplication.processEvents()
                nowWordIndex = nextWordIndex

                newWordList = []
                for i in range(self.vertexNum):
                    if self.edgeTable[nowWordIndex][i] > 0:
                        newWordList.append(i)
                nextWordIndex = None
                # print(newWordList, self.wordIndexMap.inverse[nowWordIndex])
                if newWordList:
                    nextWordIndex = newWordList[random.randint(0, len(newWordList) - 1)]
                # 发现重复后仍执行一遍再退出
                if (str(nowWordIndex) + "&" + str(nextWordIndex)) in pathDic:
                    time.sleep(1)
                    self.randomWalkStr += " " + self.wordIndexMap.inverse[nextWordIndex]
                    self.textEdit_2.setPlainText(self.randomWalkStr)
                    color_list[nextWordIndex] = "red"
                    self.changeGraphColor(color_list=color_list)
                    QApplication.processEvents()
                    # print(randomWalkStr)
                    break

        else:
            self.randomWalkFlag = True
            with open('./strSave/randomWalk.txt', 'w', encoding='utf-8') as f:
                f.write(self.randomWalkStr)
                f.close()
            self.textEdit_2.setPlainText("stop random walk by user, save to file ./strSave/randomWalk.txt")
            QApplication.processEvents()


def main():
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

import math
import os
import random

from enchant.tokenize import get_tokenizer


# 解析输入
def parse_input(sentence):
    wordList = []
    for line in sentence:
        # print(line.lower())
        tknzr = get_tokenizer("en_US")
        wordList = [w[0] for w in tknzr(line.lower())]
    return wordList


# 单源最短路径，dijistra
def dijistra(edgeTable, src):
    N = len(edgeTable)
    # 用dis数组记录源点到与它相连接的顶点的距离
    dis = [-1 for i in range(N)]
    # 用visited数组记录访问过的节点
    visited = [False for i in range(N)]
    # path 记录数组
    path = [-1 for i in range(N)]
    path[src] = src
    # 初始化 dis, path
    for i in range(N):
        dis[i] = edgeTable[src][i]
    visited[src] = True
    for j in range(N):
        if not visited[j] and edgeTable[src][j] > 0:
            path[j] = src

    while True:
        # 在未访问中选择一个最小的距离加入
        min_dis = math.inf
        point = -1
        for i in range(N):
            if not visited[i] and dis[i] != -1 and dis[i] < min_dis:
                min_dis = dis[i]
                point = i
        # 找不到合适的点加入，可能是已经全节点访问完毕或者非连通图

        if point == -1:
            break
        visited[point] = True
        for j in range(N):
            if not visited[j] and edgeTable[point][j] > 0 and (
                    dis[point] + edgeTable[point][j] < dis[j] or dis[j] == -1):
                dis[j] = dis[point] + edgeTable[point][j]
                path[j] = point

    return path, dis


def get_one_word_path(path, dis, src, end, wordIndexMap):
    pathList = []
    nowIndex = end
    distense = 0
    if path[end] != -1:
        while nowIndex != src:
            pathList.append(wordIndexMap.inverse[nowIndex])
            nowIndex = path[nowIndex]
        pathList.append(wordIndexMap.inverse[nowIndex])
        pathList.reverse()
        pathStr = ""
        for word in pathList:
            pathStr += word + " "
        return True, pathStr, dis[end], pathList
    else:
        return False, "", distense, []


if __name__ == "__main__":
    # f = open('test.txt', encoding='utf-8')
    # sentence = []
    # for line in f:
    #     sentence.append(line.strip())
    # parse_input(sentence)

    # print(dijistra([[0, 10, 3, 10], [1, 0, -1, 3], [50, 3, 0, 100], [-1, -1, -1, 0]], 0))

    print(random.randint(0, 1))

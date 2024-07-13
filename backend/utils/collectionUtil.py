
getSubDict = lambda dic, sub : dic if sub == []  else getSubDict(dic.get(sub[0], {}), sub[1:])
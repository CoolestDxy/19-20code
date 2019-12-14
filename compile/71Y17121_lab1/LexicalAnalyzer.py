import argparse
#关键词表
basicWordTable = [
    "include","define","auto","bool","break","case","catch","char","class",
    "const","const_cast","continue","cstdlib","ctime","default","delete","do","double",
    "dynamic_cast","else","enum","explicit","extern","false","float","for",
    "friend","goto","if","inline","int","iostream","long","mutable","main","namespace","new",
    "operator","private","protected","public","register","reinterpret_cast",
    "return","short","signed","sizeof","static","static_cast","std","struct",
    "switch","template","this","throw","true","try","typedef","typeid",
    "typename","union","unsigned","using","virtual","void","volatile","while"
]
#对分隔符与操作符表中的各个token赋予属性值
separatorTable = [",",";",".","(",")","[","]","{","}","#"]#0-9
operatorTable = ["+", "-","++","--", "*", "/", "<", "<=", ">", ">=", "=", "==","!=","<<",">>","&&","||"]#10-26
identitierTable = list()
charTable = list()
stringTable = list()
integerTable = list()
floatTable = list()

#判断token类型
def isDigit(charactor):
    return charactor.isdigit()
def isLetter(charactor):
    return charactor.isalpha()
def isBasicWord(string):
    return string in basicWordTable
def isSeparator(charactor):
    return charactor in separatorTable
def isOperator(string):
    return string in operatorTable
def CanBeOperator(string):
    return string in "".join(operatorTable)
def isSpace(charactor):
    return charactor in " \n\r\t"

#数字分析器
def analyzeDigit(content,head):
    c=content
    h=head
    dot=0
    while h<len(c) and (isDigit(c[h]) or c[h] == '.') and dot<2:#识别连续的数字和小数点
        if c[h] == '.':
            dot=dot+1
        h=h+1
    morp=content[head:h]
    if '.' in morp:
        if morp not in floatTable:
            floatTable.append(morp)
        attr='floatTable'
    else:
        if morp not in integerTable:
            integerTable.append(morp)
        attr='integerTable'
    return (morp,'number',attr,h)
#字母分析器
def analyzeLetter(content,head):
    c = content
    h = head
    while h <len(content) and (isDigit(c[h]) or isLetter(c[h])):
        h=h+1
    morp=c[head:h]
    if isBasicWord(morp):
        attr='-'
        unit=morp
    else:
        if morp not in identitierTable:
            identitierTable.append(morp)
        unit='id'
        attr='identitierTable'
    return (morp,unit,attr,h)
#字符串分析器
def analyzeString(content,head):
    c=content
    h=head+1
    print(len(c),h)
    while h<len(content) and (c[h-1] == "\\" or c[h] != "\""):#判断字符串是否结束
        if c[h]=='\n':
            return('string missing \" at line ','Error','-',h)
        h=h+1
    if h>=len(content):
        return ('string missing \" at line ', 'Error', '-', h)
    string=content[head:h+1]
    stringTable.append(string)
    return (string,'String','stringTable',h+1)
#注释分析器
def analyzeComment(content,head):
    c=content
    h=head+1
    if h<len(content) and c[h]=='/':
        while h<len(content) and c[h] != '\n':
            h=h+1
        return (content[head:h],'Comment','-',h)
    elif h<len(content) and c[h]=='*':
        while h<= len(content) and (c[h- 1] != '*' or c[h] != '/'):
            h = h+1
        if h <= len(content):
            return(content[head:h+1],'Comments','-',h+1,content[head:h+1].count('\n'))
        else:
            return('Missing symbol of comment','Error','-',h)
    else:
        return ('/','Operator',operatorTable.index(content[head]) + 10,h)
#对文件进行扫描
def Scanner(content):
    head=0#读头所在位置
    end=len(content)#文件结尾
    line=1#记录程序行数（报错分析）
    tokenList=[]
    while head<end:
        #识别数字
        if isDigit(content[head]):
            r=analyzeDigit(content,head)
            tokenList.append((r[0],r[1],r[2]))
            head=r[3]
            continue
        #识别字母（变量和关键词）
        elif isLetter(content[head]):
            r=analyzeLetter(content,head)
            tokenList.append((r[0],r[1],r[2]))
            head = r[3]
            continue
        #识别分隔符
        elif isSeparator(content[head]):
            tokenList.append((content[head],'Separater',separatorTable.index(content[head])))
            head=head+1
            continue
        # 识别注释
        elif content[head] == '/':
            r = analyzeComment(content, head)
            if r[1] == 'Comments':
                line = line + r[4]
            tokenList.append((r[0], r[1], r[2]))
            head = r[3]
            continue
        #识别操作符
        elif CanBeOperator(content[head]):
            tryoperator=content[head:head+2]
            if isOperator(tryoperator):
                tokenList.append((tryoperator,'Operator',operatorTable.index(tryoperator)+10))
                head=head+2
                continue
            elif isOperator(content[head]):
                tokenList.append((content[head], 'Operator', operatorTable.index(content[head]) + 10))
                head=head+1
                continue
            else:
                tokenList.append(('unexpected '+content[head]+' at line '+str(line)+'!','Error','-'))
                head=head+1
                continue
        #识别字符
        elif content[head]=='\'':
            if head+2<end:
                if content[head+2]=='\'':
                    tokenList.append((content[head],'Char',content[head]))
                    head=head+2
                    continue
            tokenList.append(('missing \' after char ' +content[head+1]+' at line '+str(line)+'!','Error','-'))
            head=head+2
            continue
        #识别字符串
        elif content[head]=='\"':
            r=analyzeString(content,head)
            if r[1]=='Error':
                tokenList.append((r[0]+str(line),r[1],r[2]))
                head=r[3]
                continue
            else:
                tokenList.append((r[0],r[1],r[2]))
                head=r[3]
                continue
        #识别空格换行符：
        elif isSpace(content[head]):
            if content[head]=='\n':
                line=line+1
            head=head+1
            continue
        #识别失败
        else:
            tokenList.append(('unexpected '+content[head]+' at line '+str(line)+' !','Error','-'))
            head=head+1
            continue
    return tokenList
#分析文件
def analyseFile(filename):
    with open('TestAndOutPut/'+filename, encoding='utf-8')as input:
        content = input.read()
    tokenList=Scanner(content)
    with open('TestAndOutput/outputOf'+filename[:-3]+'.txt','w',encoding='utf-8')as output:
        for token in tokenList:
            out='< '+str(token[0])+' , '+str(token[1])+' , '+str(token[2])+' >'
            print(out)
            output.write(out+'\r')
#命令行使用方法
def cmdStart():
    parser=argparse.ArgumentParser()
    parser.description='输入要进行分析的文件名'
    parser.add_argument('--f',help='file name（in the TestAndOutput dir）')
    args=parser.parse_args()
    analyseFile(args.f)
if __name__ == "__main__":
    #analyseFile('test4.cpp')
    cmdStart()





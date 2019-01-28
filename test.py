from pya2l.a2lparser import A2LParser

a2l = A2LParser()
wk = a2l.parseFromFileName("1.a2l")
print("------------------------------")
for i in wk.instList:
    print(i)
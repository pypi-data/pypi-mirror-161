import numpy as np


def read_bin(path, fileName, nbBytes=[]): 

    if nbBytes==[]:
        nbBytes = [1,1,2,1,1,1,8]

    f = open(path+fileName, "rb")
    num = f.read(4)
    nbL = int.from_bytes(num, byteorder='little', signed=True)
    num = f.read(4)
    nbC = int.from_bytes(num, byteorder='little', signed=True)
    print("nb lines = ", nbL)
    print("nb col = ", nbC)


    Data = []
    for i in range(nbL):
        Data.append([])
        for j in range(nbC+1):
            if(nbBytes[j]!=8):
                numB = f.read(nbBytes[j])
                myNum = int.from_bytes(numB, byteorder='little', signed=True)
                Data[i].append(myNum)
            elif(nbBytes[j]==8):
                numB = f.read(8)
                temp = np.frombuffer(numB,dtype=np.float64)
                Data[i].append(temp[0])

    return Data

    f.close()
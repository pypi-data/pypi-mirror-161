import random

class matrix():
    def __init__(self, rows, cols,val,up=100,down=0):

        self.rows=rows
        self.cols=cols
        self.order=[rows,cols]
        if val=="null" or val=="NULL": self.matrix=[ [0 for i in range(self.cols)] for j in range(self.rows)]
        elif val=="identity" or val=="IDENTITY": 
            if rows==cols:
                self.matrix= [ [0 if i!=j else 1 for i in range(self.cols) ] for j in range(self.rows)]
            else:
                raise Exception("This is only available for square matrix")

        elif val=="random" or val=="RANDOM": self.matrix=[ [random.randint(down,up) for i in range(self.cols)] for j in range(self.rows)]

        elif val=="ltriangle" or val=="LTRIANGLE":  
            if rows==cols:
                self.matrix= [ [0 if i>j else random.randint(down,up) for i in range(self.cols) ] for j in range(self.rows)]
            else: raise Exception("This is only available for square matrix")

        elif val=="utriangle" or val=="UTRIANGLE":  
            if rows==cols:
                self.matrix= [ [0 if i<j else random.randint(down,up) for i in range(self.cols) ] for j in range(self.rows)]
            else: raise Exception("This is only available for square matrix")

        else: self.matrix=val



    def __add__(self,other):
        if self.order==other.order:
            result=matrix(other.order[0],other.order[1],"null")
            for row in range(other.order[0]):
                for col in range(other.order[1]):
                    result.matrix[row][col]=self.matrix[row][col]+other.matrix[row][col]
            return result
        else:
            raise Exception("Matrixes are not of the same size")

    def __sub__(self,other):
        if self.order==other.order:
            result=matrix(other.order[0],other.order[1],"null")
            for row in range(other.order[0]):
                for col in range(other.order[1]):
                    result.matrix[row][col]=self.matrix[row][col]-other.matrix[row][col]
            return result
        else:
            raise Exception("Matrixes are not of the same size")

    def __mul__(self,other):
        if self.order[1]==other.order[0]:
            result=matrix(self.order[0],other.order[1],"null")
            for row in range(self.order[0]):
                for col in range(other.order[1]):
                    for i in range(self.order[1]):
                        result.matrix[row][col]+=self.matrix[row][i]*other.matrix[i][col]
            return result
        else:
            raise Exception("Matrixes are not compatible")

    def __truediv__(self,other):
        raise Exception("operator not available")

    def __getitem__(self,pos):
        row,col=pos
        return self.matrix[row-1][col-1]

    def __call__(self,matrix):
        if len(matrix)==self.order[0] and list(set([len(i) for i in matrix]))[0]==self.order[1] and len(list(set([len(i) for i in matrix])))==1:
            self.matrix=matrix
        else: raise Exception("matrix given does not have the same order as matrix initialised")

    def __setitem__(self,pos,value):
        row,col=pos
        self.matrix[row-1][col-1]=value

    def __eq__(self, other):
        if self.order==other.order:
            for row in range(self.order[0]):
                for col in range(self.order[1]):
                    if self.matrix[row][col]!=other.matrix[row][col]: 
                        return False
            
            return True
        else: return False

    def __neg__(self):
        result=matrix(self.order[0],self.order[1],"null")
        for i in range(self.order[0]):
            for j in range(self.order[1]):
                result[i+1,j+1]=-(self.matrix[i][j])
            
        return result

    def __bool__(self):

        return matrix(self.order[0],self.order[1],self.matrix).nullity()


    def __str__(self):
        st=""
        for i in self.matrix:
            st= st+str(i)+"\n"
        return st
        
    def rows(self):
        return self.order[0]

    def cols(self):
        return self.order[1]

    def minor(self,row,col):

        if self.order[0]==2 and self.order[1]==2 and self.order[0]==self.order[1]:
 
            for i in range(2):
                if i!=row-1:
                    for j in range(2):
                        if j!=col-1:
                            return self.matrix[i][j]

        elif self.order[0]==self.order[1]:
 
            result=[]
            for i in range(self.order[0]):
                if i!=row-1:
                    temp_row=[]
                    for j in range(self.order[1]):
                        if j!=col-1:
                            temp_row.append(self.matrix[i][j])
                    result.append(temp_row)

            result_matrix=matrix(self.order[0]-1,self.order[1]-1,result)
 
            return result_matrix.determinant()

        else: raise Exception("minor method is only available on square matrix")

    def principal_diagonal(self):
        if self.order[0]==self.order[1]:
            pd=[]
            for i in range(self.order[0]):
                for j in range(self.order[1]):
                    if i==j:
                        pd.append(self.matrix[i][j])
            return pd

        else : raise Exception("method only available on square matrix")

    def cofactor(self,row,col):
        
        if self.order[0]==self.order[1]:
 
            return ((-1)**(row+col))*matrix(self.order[0],self.order[1],self.matrix).minor(row,col)

        else: raise Exception("cofactor method is only available on square matrix")

    def trace(self):
        if self.order[0]==self.order[1]:
            trace=0
            for i in range(self.order[0]):
                for j in range(self.order[1]):
                    if i==j:
                        trace+=self.matrix[i][j]
            return trace

        else : raise Exception("method only available on square matrix")

    def determinant(self):

        temp=matrix(self.order[0],self.order[1],self.matrix)

        if temp.isltriangle() or temp.isutriangle():
            x=temp.principal_diagonal()
            res=1
            for i in x:
                res*=i
            return res
        
        if self.order[0]==2 and self.order[1]==2 and self.order[0]==self.order[1]:
 
            return self.matrix[0][0]*self.matrix[1][1] - self.matrix[0][1]*self.matrix[1][0]

        elif self.order[0]==self.order[1]:

            det=0
            for i in range(self.order[1]):

                det+=(self.matrix[0][i]*temp.cofactor(1,i+1))

            return det

        else: raise Exception("determinant method is only available on square matrix")

    def transpose(self):
        result=matrix(self.order[1],self.order[0],"null")
        for i in range(self.order[0]):
            for j in range(self.order[1]):
                result[j+1,i+1]=self.matrix[i][j]
        return result

    def adjoint(self):
        temp=matrix(self.order[0],self.order[1],self.matrix)
        result=matrix(self.order[0],self.order[1],"null")
        for i in range(self.order[0]):
            for j in range(self.order[1]):
                result[i+1,j+1]=temp.cofactor(i+1,j+1)
        return result.transpose()

    def isutriangle(self):
        if self.order[0]==self.order[1]:
            for i in range(self.order[0]):
                for j in range(self.order[1]):
                    if i>j and self.matrix[i][j]!=0:
                        return False

            return True
        
        else: raise Exception("method only available on square matrix")

    def isltriangle(self):
        if self.order[0]==self.order[1]:
            for i in range(self.order[0]):
                for j in range(self.order[1]):
                    if i<j and self.matrix[i][j]!=0:
                        return False

            return True
        
        else: raise Exception("method only available on square matrix")

    def nullity(self):

        for i in range(self.order[0]):
            for j in range(self.order[1]):
                if self.matrix[i][j]!=0:
                    return False
        return True

    def inverse(self,precision=10):
        temp=matrix(self.order[0],self.order[1],self.matrix)
        result=matrix(self.order[0],self.order[1],"null")
        det=temp.determinant()
        adj=temp.adjoint()
        for i in range(self.order[0]):
            for j in range(self.order[1]):
                result[i+1,j+1]=round(adj[i+1,j+1]/det,precision)
        return result

    def squareness(self):
        if self.order[0]==self.order[1]:
            return True
        else: return False     


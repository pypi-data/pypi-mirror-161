# matrix

This is a module to replicate matrix object to python and all its mathematical operators

## Installation

>pip install matrix_object

## Documentation

Available methods
-   `.rows()`
-   `.cols()`
-   `.principal_diagonal()`
-   `.minor(row,col)`
-   `.cofactor(row,col)`
-   `trace()`
-   `.determinant()`
-   `.transpose()`
-   `.adjoint()`
-   `.inverse([presision])`
-   `.isutriangle()`
-   `.isltriangle()`
-   `nullity()`
-   `sqareness()`

Available operators
-   \+
-   \-
-   \*
-   ==
-   negation
-   bool
  

**NOTE:** Index of row and col start from 1

## creating a matrix object

```x=matrix(row,col,val)```

allows null,random, ltriangle,utriangle and identity instead of val in object creation.
-   >`null`: creates a null matrix
    >   `example: x=matrix(3,3,"null")`
-   >`random`: creates a random matrix
    >   ` example: x=matrix(3,3,"random")`
-   >`ltriangle`: creates a lower triangular matrix
    >   ` example: x=matrix(3,3,"ltriangle")`
-   >`utriangle`: creates a upper triangular matrix
    >   ` example: x=matrix(3,3,"utriangle")`
-   >`identity`: creates an identity matrix
    >   ` example: x=matrix(3,3,"identity")`

>**NOTE:** if you want to create a matrix with specific values, you can use the following syntax:
>x=matrix(row,col,val)
>where val is a list of lists with the values of the matrix.and appropriate dimensions.

## Accessing elements
>Allows value assignment using `matrix[row,col]=val`
>returns value at current index using `val=matrix[row,col]`

## .rows() 

returns number of rows in the matrix

## .cols()

returns number of columns in the matrix

## .principal_diagonal()
returns principal diagonal of the matrix

## .minor(row,col)

returns the minor of element at given row,col

## .cofactor(row,col)

returns the cofactor of element at given row,col

## .trace()
returns trace of the matrix

## .determinant()

returns determinant of the matrix

## .transpose()

returns transpose of the given matrix

## .adjoint

returns adjoint of the given matrix

## .inverse([precision])

returns inverse of the given matrix.allows precision of calculation.
**NOTE:** precision is optional.if not given,default precision is 10

## .isutriangle()
returns true if the matrix is upper triangular
otherwise returns false

## .isltriangle()
returns true if the matrix is lower triangular
otherwise returns false

## .nullity()
returns true if the matrix is null
otherwise returns false

## .squareness()
returns true if the matrix is square
otherwise returns false

## using operators

-   > x+y
    >returns addition of 2 matrix x and y


-   >x-y
    >returns subtraction of 2 matrix x and y


-   > x*y
    >returns multiplication of 2 matrix x and y


-   >x/y
    >raises exception *operator not available*

-   >x==y
    >returns true if x and y are equal
  
-   >-x
    >returns negative of matrix x

-   >bool(x)
    >returns true if x is not null
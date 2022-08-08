// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.q 
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

// Put your code here.

//set i = 0
@i 
M = 0

(loop1)
    //stopping condition loop 1
    @R15
    D = M
    D = D - 1
    @i
    D = D - M
    @END
    D;JLE

    @j
    M = 0
    (loop2)
        //stopping condition loop 2
        @R15
        D = M
        D = D - 1
        @i
        D = D - M
        @j
        D = D - M
        @increase_i
        D;JLE
        // inner loop
        @j
        D = M
        @R14
        D = D + M //D = j + r14
        A = D // A = j + r14
        D = M // D = arr[j+r14]
        A = A + 1 // A = j+1
        D = D - M // arr[j] - arr[j+1]
        @swap
        D; JLT
        (endofswap)
        @j
        M=M+1
        @loop2
        0;JMP


(swap)
@j
D = M //D = j 
@R14
D = D + M //D = j + r14
@jpointer
M = D // jpointer = j + r14

A = D // A = j + r14
D = M // D = arr[j+r14]
@temp
M = D // temp = arr[j+r14]


@j
D = M //D=j
@R14
D = D + M //D = j + r14
D = D + 1 // D = j + r14 + 1
A = D // A = j + r14 + 1
D = M // D = arr[j + r14 + 1]

@jplusone
M = D // jplusone = arr[j + r14 + 1]

@jpointer
A = M // A = j+r14
M = D //arr[j+r14] = arr[j+r14+1] swap!!

@temp
D=M // D = arr[j+r14]

@jpointer
M=M+1 // jpointer = j + r14 + 1
A=M // A = j + r14 + 1
M = D //arr[j + r14 + 1] = arr[j+r14] // swap!!
@endofswap
0;JMP





(increase_i)
@i
M=M+1
@loop1
0;JMP


(END)

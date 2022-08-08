// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// sets initial product stored at RAM[2]
@R2
M = 0 

// int i = 0 ; 
@i
M = 0 


(LOOP)
// if i == R1 go to STOP

@i
D = M 
@R1
D = D - M
@STOP
D ; JEQ 

// product = product + R0
@R0
D = M 
@R2
M = M + D

// i ++
@i
M = M + 1 
@LOOP
0 ; JMP

(STOP)

// infinite loop 
(END)
@END
0 ; JMP






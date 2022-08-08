// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(MAIN)
//set default screen color to white
@screencolor
M = 0 

// set position indicator to first screen address 
@SCREEN
D=A
@pos
M = D

// key_pressed indicator
@KBD
D=M

// key_pressed != 0 -> black
@black
D;JNE

(fillcolor)

// check if ps reached screen limits 
@pos
D=M
// last screen register
@KBD
D = A - D
//stopping condition
@MAIN
D; JLE


@screencolor
D = M

// set color of curr object to screencolor 
@pos
A = M
M = D

// increase curr pos
@pos
M = M + 1

// continue 
@fillcolor
0;JMP


// set screencolor to black
(black)
@screencolor
M=-1
@fillcolor
0;JMP


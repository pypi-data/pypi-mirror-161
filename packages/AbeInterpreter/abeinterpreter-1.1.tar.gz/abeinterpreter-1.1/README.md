# Abraham
Esoteric language interpreter

**************************************
Install:
--------
pip install abeinterpreter

**************************************

Basic Usage:
------------
0. Import:
	import abeinterpreter as ai

1. Instantiate the AbeInterpreter class:
	interp = ai.AbeInterpreter()

2. Interpret code with .interpret(code):
	interp.interpret(*some abe code here*)

3. Display output with print:
	print(interp.interpret(*some abe code here*))

**************************************
Types:	
------
String: "Hello World!"
Int: 42
Float: 3.14
Boolean: True, False

**************************************
Commands:
---------
Move right x cells:	Overhead, the geese flew x miles east.
Move left x cells:	Overhead, the geese flew x miles west.
Assign x to cell:	Preparing for the storm, he inscribed x into the stone.
Add to cell value:	He sold x sheep.
Subtract from cell value:	They paid for their x mistakes.
Print cell value:	And Abraham spoke!
While loop:	He ran into the mountains, but only when ___. This is what happened there:
Note:	Loop conditions act on current cell value.
Loop conditions:	If greater than cell val: they had more than x fish
If less than cell val: they had less than x fish
If equal to cell val: the stone said x
Signal loop end:	Alas, I digress.
Copy:	One day he stole his neighbor's goods.
Paste:	He repented and returned the property.

**************************************
Print even integers from 100 to zero:	
-------------------------------------
He sold 100 sheep. 
He ran into the mountains, but only when they had more than 0 fish. 
This is what happened there: 
And Abraham spoke! 
They paid for their 2 mistakes. 
Alas, I digress. 
And Abraham spoke!

**************************************
# Pickle Gomoku Agent
The Gomoku (Five in a Row) agent __Pickle__ for the project of Artificial Intelligence (DATA130008.01) @Fudan University  

Pickle is based on threat space search, which is a rather strong searching algorithm.  
Support [Gomocup](http://gomocup.org) protocol.  
  
Using Pyinstaller to get the exe package:  
```Python
pyinstaller.exe pickle_new.py pisqpipe.py utils.py threat_space_search.py --name pbrain-pickle.exe --onefile
```  
  
Download the standard interface [Piskvork](http://gomocup.org/download-gomocup-manager/) to start the game.

# Duel-52-Machine-Learning
**_A machine learning programme for the card game Duel 52._**

This project aims to build a Machine Learning (ML) model without the use of ML packages (instead using **Numpy**), in order to learn the basics of ML, and to see what strategies the model finds to be effective.

The model uses a **Temporal Difference (TD)** learning technique, inspired by the TD-Gammon programme which successfully learnt Backgammon to a world-class level ([Stanford: Temporal Difference Learning](https://web.stanford.edu/group/pdplab/pdphandbook/handbookch10.html)). This was applicable since there is no existing way to evaluate a given board-state for Duel 52, being a relatively unknown game, as there is for a game such as Chess which has various evaluatin functions. This meant the ML programme could only initially evaluate move-strength using the end result of the game, rather than through evaluating the quality of resulting positions. 

TD learning allows the programme to learn this way by keeping a record of the effect of all the moves made, and taking these into account once training the model at the end of the game. This allows the programme to learn over time what a good or bad gamestate might look like, rather than requiring the gamestate to be explicitly defined by an evaluation function. 

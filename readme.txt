Practice Project: Teaching an AI to Play Flappy Bird using an Evolutionary Algorithm
Watts Dietrich
Nov 9 2020

In this practice project, the evolutionary AI algorithm called NEAT (NeuroEvolution of Augmenting Topologies)
is used to teach an AI to play the game "Flappy Bird."

In Flappy Bird, a player controls a single bird and tries to guide it through a series of obstacles. The height of the
bird on the screen is controlled by the player, who can tell the bird when to flap its wings to increase its height.

In this code, the pygame library is used to build a basic implementation of Flappy Bird. 20 different birds, each
controlled by a different neural network, are instantiated simultaneously. These 20 birds comprise a "generation."
Each of the neural networks use randomized parameters, so each bird tends to behave differently from the others.
Once all 20 birds fail (i.e. hit an obstacle and lose the game), the best bird of the generation is chosen and its
neural net is used as a model for building those of the next generation of 20 birds. As in biological evolution,
some random mutations (variation in the parameters) are introduced. This process continues until we have a bird that
can successfully navigate every possible obstacle in the game.

In my testing, the number of generations needed to arrive at a "perfect" bird (one that never loses) has varied from
two to thirteen (the randomization involved in the algorithm means that some runs will happen upon on ideal bird
sooner than others). Most of the time, it takes 3-5 generations.

The Tech With Tim channel on youtube was an invaluable resource in figuring this out, see the link:
https://www.youtube.com/watch?v=OGHA-elMrxI
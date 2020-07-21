Current goals:
    [ ] run a game of normal chess
        [ ] make normal chess game loop
        [ ] make interface
        [ ] make normal chess topology
        [ ] make normal chess rules


a game has 1 window
	chess has 1 board
		which is a topology with its atlas
			the topology is on the set of all tiles
				a tile has a state
					in normal chess this state only holds a piece or None
						in normal chess a piece has movement rules (see rules)
						in normal chess a piece has a color (see rules)
	
a game is a rule based loop
	a turn based game only has a waiting state which is interrupted by input
		in chess an input needs to be valid to have an effect
			the validity is checked by a rule
				in normal chess the validity depends on the selected tile, its state, the topology, the target tile, and its state (movement rules)
				if it is valid another rule enforces the effect
					in normal chess a game is won if one player has no kings (color rules)
	a rule may call other rules or change the state of the game
	
	

We need:
	- interface
	- game loop
	- network capabilities
	- topology engine
	- state/rule/topology creation toolsets
	
	

Minimal demos:
	- normal chess
	- blind chess
	- normal chess a hexagonal grid
	- normal chess on a torus with N holes
	- "normal" chess on a irregular grid


Component requirements:
	Interface:
		- needs sufficient widgets to start a local or online game
		- needs to take input and send it to the topology and rule engine for translation
		- only needs to show the topology, the states of the tiles, and the states of the game (this is managed by the rulesets)
		
	Game loop:
		- needs to be able to be interrupted on:
			- user input
			- user interrupt
			- network input
			- timers or other callbacks
			
	Network capabilities:
		- communication over sockets (done), but ssl would be better
		
	Topology engine:
		- needs to translate from and to tiles and patches
		- needs to manage angles between tiles
		
	Toolsets:
		- optional:
			- tool to discretize a parametric manifold to a topology
			

Paradigms:
	For representation of states we should use the usual factored/object-oriented approach to maximize bundling of inherently linked concepts by meaning/function/type.
	However the objects need to have no methods, so that rules of the game can be separated from the representation of the game.
	Polymorphism should also be propagated through the requirements of the used rules rather than the usual subclass polymorphism.
	The rules should not reference eachother too much and should be written so that they can be chosen to interact or act entirely separately.
	A rule should mention which other rules are required and which restrictions should be applied to the state of the game (i.e. which fields need to exist)
	

Chosen implementations:
	Interface:
		tkinter with a main menu, sufficient space for extra widgets and one board
		
	Game loop:
		a while loop waiting on a bunch of locks, which can be notified from the gui thread, a network thread or another timer/callback thread
		
	Network capabilities:
		sockets
		
	Topology engine:
		topo = (tiles, atlas), where tiles = [tile], tile = (state, neighbours), neighbours = [neighbour], neighbour = (tile, vector), atlas = [patch], patch = [tile]
		and some fast search algorithms back and forth
		
	Toolsets:
		-
		

	
	
	
	

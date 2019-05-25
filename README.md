# BotimusPrime
A python offline Rocket League bot made with the RLBot framework.
Currently uses the pypi version of [RLUtilities](https://github.com/samuelpmish/RLUtilities/). Huge thanks to @chip!

This is the V2 (Wintertide) version. You can get the older version from the Releases tab.

## How to use
- Go to [rlbot.org](http://www.rlbot.org/) and download RLBot.
- Download/clone this repository.
- Click the ``+`` icon next to Player Types and select ``File``.
- Select the ``botimus.cfg`` file. New Player Type should show up.
- Make any match configuration you like and start the match. Have fun!

Note: If you aren't using the GUI version, you should also do ``pip install -r requirements.txt``

## Achievments
- 2nd place in [RLBot 2018 Tournament - 1v1](https://www.youtube.com/watch?v=TPb-6NzXkRw) (old version)
- 2nd place in [RLBot Wintertide Tournament - 1v1](https://www.youtube.com/watch?v=vRqfJO701oE)

## How it works
Botimus v2 is a very simple state-machine. It has one state (maneuver) active at a time, until it expires or gets cancelled due to another player hitting the ball. Then it chooses a new maneuver based on its strategy logic. Repeat.

Current strategy can be summarized as: Try to shoot on goal if able to hit the ball sooner than any other car, or if opponent is out of position. Otherwise shadow defense or grab boost.

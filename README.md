# RLBot
This repository is related to [RLBot](http://www.rlbot.org/), a framework for running offline Rocket League bots. You can try both Botimus and Bumblebee by downloading RLBotGUI and the BotPack.

# Botimus Prime & Bumblebee
This repository contains two bots: Botimus Prime and Bumblebee. They share most of the code, but use a different strategy. Botimus can play solo or with different bots, while Bumblebee is designed to play only with copies of itself as teammates. That's because it's a hivemind bot, which means one process is controlling all of the Bumblebees on one team. The ideal team is 3x Bumblebee.

# RLUtilities
The `rlutilities` folder contains a compiled pybind11 module. RLUtilities is a library with a lot of useful stuff for making Rocket League bots, such as querying the arena mesh, simulating the ball and partially the cars, linear algebra stuff and controllers for various mechanics.
- [the original RLUtilities by chip](https://github.com/samuelpmish/RLUtilities)
- [customized fork used in this repo](https://github.com/Darxeal/RLUtilities)

# Tournament appearances
Links to VODs where you can watch Botimus or Bumblebee play, from newest to oldest:
- [2020 Ultimate Battle League - 3v3](https://www.youtube.com/playlist?list=PL_MJp3c3rJVU2wrnozpNT2f6zex3YmcLB) - First appearance of Bumblebee
- [RLBot 2019 Lightfall - 1v1](https://youtu.be/2lA0uH_--Ko)
- [RLBot 2019 Triple Threat - 3v3](https://youtu.be/2lA0uH_--Ko)
- [RLBot 2019 Wintertide Tournament - 1v1](https://www.youtube.com/watch?v=vRqfJO701oE) - Botimus 2.0
- [RLBot 2018 August Tournament - 1v1](https://www.youtube.com/watch?v=TPb-6NzXkRw) - First appearance of Botimus

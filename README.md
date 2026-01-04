🐑 Shepherd and The Sheep 3D OpenGL Game

📌 Overview

Shepherd and The Sheep is a 3D survival strategy game developed using Python and PyOpenGL as part of the CSE423 – Computer Graphics course. The game takes place in a circular forest clearing where the player controls a shepherd whose main objective is to protect a group of sheep from attacking wolves across multiple day and night cycles. The game emphasizes survival, resource management, and strategic movement rather than direct combat.

During the daytime, the environment remains calm and safe, allowing the shepherd to collect resources such as wood and prepare for the coming night. As night falls, wolves appear from the forest and attempt to hunt the sheep. The shepherd must use tools, fire, stones, and positioning to keep at least one sheep alive for three consecutive nights in order to win the game.

🎮 Gameplay

The game alternates between day and night phases. During the day, sheep wander freely and the shepherd can move around the clearing, chop wood, and prepare defenses. At night, wolves spawn and aggressively chase sheep. A bonfire can be built at the center to repel wolves, and stones can be thrown to eliminate threats. Sheep can be called toward the shepherd using a whistle, allowing the player to gather and protect them more effectively.

The game ends in one of two ways. If all sheep die at any point, the game is over and the shepherd collapses on the ground. If the shepherd successfully protects at least one sheep for three consecutive nights, the game is won and a victory screen is displayed.

 🖥️ Controls

| Key            | Action                              |
|----------------|-------------------------------------|
| W              | Move Forward                        |
| S              | Move Backward                       |
| A              | Rotate Left                         |
| D              | Rotate Right                        |
| Arrow Left     | Rotate Camera Left                  |
| Arrow Right    | Rotate Camera Right                 |
| Arrow Up       | Zoom In                             |
| Arrow Down     | Zoom Out                            |
| Right Click    | Toggle First / Third Person View    |
| SPACE          | Chop Wood (Day)                     |
| E              | Throw Stone (Night)                 |
| F              | Build / Add Fire (Center)           |
| V              | Whistle (Call Sheep)                |
| C              | Toggle Cheat Mode (Night Only)      |
| R              | Restart Game                        |
| ENTER          | Start Game                          |


▶️ How to Run

Ensure that Python 3 is installed on your system along with the required OpenGL libraries. After installing PyOpenGL and PyOpenGL_accelerate, the game can be started by running the main Python file from the terminal.

🏆 Objective

Survive three consecutive nights while keeping at least one sheep alive. If the sheep are lost, the shepherd loses. If the sheep survive, the player wins.

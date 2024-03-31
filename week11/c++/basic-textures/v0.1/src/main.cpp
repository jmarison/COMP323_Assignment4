#include "Player.h"
#include <SFML/Graphics.hpp>

using namespace sf;

// initial bootstrap for game
int main() {

	/* 
	* create SFML window
	*/
	// set resolution of game window
	Vector2f screenRes;
	screenRes.x = VideoMode::getDesktopMode().width;
	screenRes.y = VideoMode::getDesktopMode().height;
	// render game window
	RenderWindow window (VideoMode(screenRes.x, screenRes.y), "BasicTextures", Style::Fullscreen);	

	// add initial player - place at foot of window, centred
	Player player(screenRes.x / 2, screenRes.y - 25);	

	/* main game loop */
	while (window.isOpen()) {

		// handle quitting game window
		if (Keyboard::isKeyPressed(Keyboard::Escape)) {
			window.close();
		}

		/*
		* draw
		* - player, display	
		*/
		window.clear();
		window.draw(player.getShape());
		window.display();

	}	// end of game loop

	return 0;
}

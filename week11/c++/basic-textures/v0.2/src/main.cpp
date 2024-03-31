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

	// initial view
	View mainView(sf::FloatRect(0, 0, screenRes.x, screenRes.y));

	// add initial player
	//Player player(screenRes.x / 2, screenRes.y - 25);	
	Player player;

	/* main game loop */
	while (window.isOpen()) {

		// handle quitting game window
		if (Keyboard::isKeyPressed(Keyboard::Escape)) {
			window.close();
		}

		player.spawn(screenRes);

		// update 
		player.update();

		/*
		* draw
		* - player, display	
		*/
		window.clear();
		// set main view to render in game window
		window.setView(mainView);
		// draw player
		window.draw(player.getSprite());

		// display rendered window
		window.display();

	}	// end of game loop

	return 0;
}

#pragma once
#include <SFML/Graphics.hpp>

using namespace sf;

class Player {

	private:
		// locate player
		Vector2f m_Posn;
		// player sprite
		Sprite m_Sprite;
		// player texture
		Texture m_Texture;

	public:
		Player();

		// set as player spawned
		void spawn(Vector2f screenRes);	

		// check player's position
		FloatRect getPosition();

		// get player's sprite
		Sprite getSprite();

		// update per frame
		void update();

};

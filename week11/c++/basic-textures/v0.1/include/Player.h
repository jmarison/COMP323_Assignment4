#pragma once
#include <SFML/Graphics.hpp>

using namespace sf;

class Player {

	private:
		Vector2f m_Posn;

		// rectangle shape
		RectangleShape m_RectShape;

	public:
		Player(float startX, float startY);

		FloatRect getPosition();

		RectangleShape getShape();

};

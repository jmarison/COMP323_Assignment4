#include "Player.h"

// define constructor for player
Player::Player(float startX, float startY) {
	m_Posn.x = startX;
	m_Posn.y = startY;

	m_RectShape.setSize((sf::Vector2f(50, 5)));
	m_RectShape.setPosition(m_Posn);
}

FloatRect Player::getPosition() {
	return m_RectShape.getGlobalBounds();
}

RectangleShape Player::getShape() {
	return m_RectShape;
}

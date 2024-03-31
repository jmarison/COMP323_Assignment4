#include "Player.h"

// define constructor for player
Player::Player() {
	// setup texture for player's sprite
	m_Texture.loadFromFile("../assets/graphics/player-square.png");
	m_Sprite.setTexture(m_Texture);

	// origin of sprite set to centre
	m_Sprite.setOrigin(25, 25);
}

// spawn function for loading player
// may be called multiple times in game lifecycle
void Player::spawn(Vector2f screenRes) {
	// set initial player posn to centre 
	m_Posn.x = screenRes.x / 2;
	m_Posn.y = screenRes.y / 2;
}

FloatRect Player::getPosition() {
	return m_Sprite.getGlobalBounds();
}

Sprite Player::getSprite() {
	return m_Sprite;
}

void Player::update() {
	// initial update per frame
	m_Sprite.setPosition(m_Posn);
}

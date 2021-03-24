CREATE TABLE emoji_usages
(
	server BIGINT UNSIGNED,
	channel BIGINT UNSIGNED,
	user BIGINT UNSIGNED,
	emoji VARCHAR(255),
	type ENUM('original', 'custom'),
	time TIMESTAMP
);

CREATE TABLE emojis
(
	guild BIGINT UNSIGNED,
	emojiID BIGINT UNSIGNED
);

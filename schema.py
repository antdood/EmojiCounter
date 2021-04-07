CREATE TABLE emoji_usages
(
	channel BIGINT UNSIGNED,
	user BIGINT UNSIGNED,
	emoji VARCHAR(255),
	type ENUM('original', 'custom'),
	time TIMESTAMP
);

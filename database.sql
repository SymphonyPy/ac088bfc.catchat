CREATE TABLE users (
	id  INTEGER NOT NULL,
	name  VARCHAR(255),
	password  VARCHAR(255),
	time_joined  INTEGER,
	age	INTEGER,
	gender	INTEGER,
	status	VARCHAR(255),
	school	VARCHAR(255),
	location	VARCHAR(255),
	email	VARCHAR(255),
	PRIMARY KEY (id)
);
CREATE TABLE rooms (
	id  INTEGER NOT NULL,
	name  VARCHAR(255),
	password  VARCHAR(255),
	created_time  INTEGER,
	announcement	VARCHAR(255),
	PRIMARY KEY (id)
);
CREATE TABLE friends(
	id1  INTEGER NOT NULL,
	id2	INTEGER NOT NULL,
	typeofid2	VARCHAR(255),
	foreign key (id1) references users(id)
);
CREATE TABLE members(
	room_id  INTEGER NOT NULL,
	user_id	INTEGER NOT NULL,
	joined_time	INTEGER,
	foreign key (room_id) references rooms(id),
	foreign key (user_id) references users(id)
);
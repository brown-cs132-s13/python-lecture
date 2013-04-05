drop table if exists entries;
drop table if exists comments;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);
create table comments (
	id integer primary key autoincrement,
	post integer,
	content text not null
);
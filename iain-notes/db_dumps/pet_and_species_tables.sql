drop table if exists pet;
drop table if exists person;

create table pet (
    id int primary_key not null,
    name text not null,
    age  int 
);

create table person (
    id int primary_key not null,
    first_name text not null,
    last_name text not null,
    age  int 
);

insert into pet values 
    (1, 'Titchy', 17),
    (2, 'Snufkin', 12),
    (3, 'Tiger', 4),
    (4, 'Kismet', 9);

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE pet (
    id int primary_key not null,
    name text not null,
    age  int 
);
INSERT INTO "pet" VALUES(1,'Titchy',17);
INSERT INTO "pet" VALUES(2,'Snufkin',12);
INSERT INTO "pet" VALUES(3,'Tiger',4);
INSERT INTO "pet" VALUES(4,'Kismet',9);
CREATE TABLE person (
    id int primary_key not null,
    first_name text not null,
    last_name text not null,
    age  int 
);
COMMIT;

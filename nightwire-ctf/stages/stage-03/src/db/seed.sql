CREATE DATABASE solace;
USE solace;

CREATE TABLE users (id INT, username VARCHAR(50), password_hash VARCHAR(32), role VARCHAR(20));
-- MD5 hash for 'qwerty' (a weak rockyou.txt password)
INSERT INTO users VALUES (1, 'support', MD5('support123'), 'agent');
INSERT INTO users VALUES (2, 'admin', 'd8578edf8458ce06fbc5bb76a58c5ca4', 'admin');

CREATE TABLE tickets (ticket_id VARCHAR(20), notes TEXT);
INSERT INTO tickets VALUES ('INC-4471', 'Next move: Pivot to 10.20.1.2. FLAG: NIGHTWIRE{b4ckd00r_p0rt4l_sqli_m4st3r}');

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS `teams` (
  `team_name` varchar(255) NOT NULL PRIMARY KEY,
  `color` varchar(7) NOT NULL,
  `banner` varchar(255) NOT NULL,
  `rank` varchar(50) NULL
);

CREATE TABLE IF NOT EXISTS `players` (
  `player_id` int(11) NOT NULL,
  `team_name` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  FOREIGN KEY (`team_name`) REFERENCES `teams`(`team_name`)
);
--
-- Mamba SQL dump 0.3.5
--
-- Database Backend: mysql
-- Host: localhost	Database: auto_torrent
-- Application: torrent
-- Application Version: 1.0
-- Application Description: Auto Torrent Downloader
-- ---------------------------------------------------------
-- Dumped on: 2014-04-26T18:47:27.395619
--
-- Disable foreign key checks for table creation
--
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `torrent_queue`;
CREATE TABLE IF NOT EXISTS `torrent_queue` (
  `id` int(11) AUTO_INCREMENT,
  `media_type` enum('MOVIE', 'TV_SHOW'),
  `query` varchar(256),
  `download_when` datetime,
  `status` enum('FINISHED', 'DOWNLOADING', 'WATCHED', 'DELETED', 'FOUND', 'NOT_FOUND', 'PENDING'),
  `date_added` datetime,
  `torrent_hash` varchar(256) default NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `tv_shows`;
CREATE TABLE IF NOT EXISTS `tv_shows` (
  `id` int(11) AUTO_INCREMENT,
  `torrent_queue_id` int(11),
  `name` varchar(256),
  `season_number` int,
  `episode_number` int,
  `air_date` datetime default NULL,
  `episode_name` text default NULL,
  `rating` int default NULL,
  PRIMARY KEY(`id`)
, INDEX `torrent_queue_id_torrent_queue_fk_ind` (`torrent_queue_id`), FOREIGN KEY (`torrent_queue_id`) REFERENCES `torrent_queue` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `movies`;
CREATE TABLE IF NOT EXISTS `movies` (
  `id` int(11) AUTO_INCREMENT,
  `torrent_queue_id` int(11),
  `name` varchar(256),
  `dvd_release` datetime default NULL,
  `theater_release` datetime default NULL,
  `rating` int default NULL,
  PRIMARY KEY(`id`)
, INDEX `torrent_queue_id_torrent_queue_fk_ind` (`torrent_queue_id`), FOREIGN KEY (`torrent_queue_id`) REFERENCES `torrent_queue` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Enable foreign key checks
--
SET FOREIGN_KEY_CHECKS = 1;


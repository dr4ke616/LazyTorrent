SET foreign_key_checks = 0;

DROP TABLE IF EXISTS `torrent_queue`;
DROP TABLE IF EXISTS `tv_shows`;
DROP TABLE IF EXISTS `movies`;

--
-- Table structure for table `torrent_queue`
--

CREATE TABLE IF NOT EXISTS `torrent_queue` (
  `torrent_queue_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `media_type` enum('MOVIE','TV_SHOW') NOT NULL,
  `query` varchar(256) DEFAULT NULL,
  `force_download` tinyint(1) NOT NULL DEFAULT '1',
  `status` enum('PENDING','FOUND','FINISHED') NOT NULL,
  `date_added` datetime NOT NULL,
  PRIMARY KEY (`torrent_queue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Table structure for table `tv_shows`
--

CREATE TABLE IF NOT EXISTS `tv_shows` (
  `tv_show_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `torrent_queue_id` int(10) unsigned NOT NULL,
  `name` varchar(256) NOT NULL,
  `season_number` int(11) NOT NULL,
  `episode_number` int(11) NOT NULL,
  `air_date` datetime DEFAULT NULL,
  `episode_name` varchar(256) DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  PRIMARY KEY (`tv_show_id`),
  FOREIGN KEY (`torrent_queue_id`) REFERENCES torrent_queue(`torrent_queue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


--
-- Table structure for table `movies`
--

CREATE TABLE IF NOT EXISTS `movies` (
  `movie_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `torrent_queue_id` int(10) unsigned NOT NULL,
  `name` varchar(256) NOT NULL,
  `dvd_release` datetime DEFAULT NULL,
  `theater_release` datetime DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  PRIMARY KEY (`movie_id`),
  FOREIGN KEY (`torrent_queue_id`) REFERENCES torrent_queue(`torrent_queue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

SET foreign_key_checks = 1;

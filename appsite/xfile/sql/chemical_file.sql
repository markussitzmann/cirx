-- MySQL dump 10.13  Distrib 5.1.61, for redhat-linux-gnu (x86_64)
--
-- Host: 129.43.27.122    Database: chemical_file
-- ------------------------------------------------------
-- Server version	5.1.61

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `upload_user_structure`
--

DROP TABLE IF EXISTS `upload_user_structure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `upload_user_structure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `structure_id` int(11) DEFAULT NULL,
  `user_file_id` int(10) unsigned DEFAULT NULL,
  `event_id` int(10) unsigned DEFAULT NULL,
  `image_id` int(10) unsigned DEFAULT NULL,
  `record` int(11) NOT NULL,
  `hashisy` bigint(20) unsigned DEFAULT NULL,
  `packstring` longtext NOT NULL,
  `date_added` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `error` int(10) unsigned DEFAULT NULL,
  `blocked` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_file_id` (`user_file_id`,`record`)
) ENGINE=MyISAM AUTO_INCREMENT=6859 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `upload_user_structure_field_value`
--

DROP TABLE IF EXISTS `upload_user_structure_field_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `upload_user_structure_field_value` (
  `user_structure_id` int(10) unsigned NOT NULL DEFAULT '0',
  `field_id` int(10) unsigned NOT NULL DEFAULT '0',
  `value` text,
  PRIMARY KEY (`user_structure_id`,`field_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `upload_user_structure_image`
--

DROP TABLE IF EXISTS `upload_user_structure_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `upload_user_structure_image` (
  `user_structure_id` int(10) unsigned NOT NULL,
  `small` blob,
  `medium` blob,
  `large` blob,
  PRIMARY KEY (`user_structure_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_file`
--

DROP TABLE IF EXISTS `user_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `records` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `display_name` varchar(255) DEFAULT NULL,
  `comment` longtext,
  `date_added` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `date_invalid` datetime DEFAULT NULL,
  `created_from_search_result` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id_refs_id_fef975d9` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=162 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_file_field`
--

DROP TABLE IF EXISTS `user_file_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_file_field` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_file_id` int(10) unsigned DEFAULT NULL,
  `original_name` varchar(64) DEFAULT NULL,
  `display_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `file_id` (`user_file_id`,`original_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1031 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_file_key`
--

DROP TABLE IF EXISTS `user_file_key`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_file_key` (
  `user_file_id` int(10) unsigned NOT NULL,
  `upload` char(32) DEFAULT NULL,
  `public` char(32) DEFAULT NULL,
  `private` char(32) DEFAULT NULL,
  PRIMARY KEY (`user_file_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_file_status`
--

DROP TABLE IF EXISTS `user_file_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_file_status` (
  `user_file_id` int(10) unsigned NOT NULL,
  `string` varchar(768) DEFAULT NULL,
  `progress` int(10) unsigned DEFAULT NULL,
  `date_blocked` datetime DEFAULT NULL,
  PRIMARY KEY (`user_file_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure`
--

DROP TABLE IF EXISTS `user_structure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `structure_id` int(11) DEFAULT NULL,
  `user_file_id` int(10) unsigned DEFAULT NULL,
  `event_id` int(10) unsigned DEFAULT NULL,
  `image_id` int(10) unsigned DEFAULT NULL,
  `record` int(11) NOT NULL,
  `hashisy` bigint(20) unsigned DEFAULT NULL,
  `packstring` longtext NOT NULL,
  `date_added` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `error` int(10) unsigned DEFAULT NULL,
  `blocked` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_file_id` (`user_file_id`,`record`)
) ENGINE=MyISAM AUTO_INCREMENT=6859 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure_database`
--

DROP TABLE IF EXISTS `user_structure_database`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure_database` (
  `user_structure_id` int(10) unsigned NOT NULL DEFAULT '0',
  `user_file_id` int(10) unsigned NOT NULL DEFAULT '0',
  `database_id` int(10) unsigned NOT NULL DEFAULT '0',
  `association_type_id` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_structure_id`,`user_file_id`,`database_id`,`association_type_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure_field_value`
--

DROP TABLE IF EXISTS `user_structure_field_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure_field_value` (
  `user_structure_id` int(10) unsigned NOT NULL DEFAULT '0',
  `field_id` int(10) unsigned NOT NULL DEFAULT '0',
  `value` text,
  PRIMARY KEY (`user_structure_id`,`field_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure_identifier`
--

DROP TABLE IF EXISTS `user_structure_identifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure_identifier` (
  `user_structure_id` int(10) unsigned NOT NULL,
  `ficts_hashcode` char(16) DEFAULT NULL,
  `ficus_hashcode` char(16) DEFAULT NULL,
  `uuuuu_hashcode` char(16) DEFAULT NULL,
  `ficts_parent_structure` blob,
  `ficus_parent_structure` blob,
  `uuuuu_parent_structure` blob,
  `valid` int(10) unsigned DEFAULT '0',
  `blocked` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`user_structure_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure_image`
--

DROP TABLE IF EXISTS `user_structure_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure_image` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `hashisy` bigint(20) unsigned DEFAULT NULL,
  `small` blob,
  `medium` blob,
  `large` blob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hashisy` (`hashisy`)
) ENGINE=MyISAM AUTO_INCREMENT=433 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure_inchi`
--

DROP TABLE IF EXISTS `user_structure_inchi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure_inchi` (
  `user_structure_id` int(10) unsigned NOT NULL,
  `inchikey` char(27) DEFAULT NULL,
  `inchi` text,
  `valid` int(10) unsigned DEFAULT '0',
  `blocked` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`user_structure_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_structure_data_source`
--

DROP TABLE IF EXISTS `user_structure_data_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_structure_data_source` (
  `user_structure_id` int(10) unsigned NOT NULL,
  `string` varchar(768) DEFAULT NULL,
  PRIMARY KEY (`user_structure_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_file_event`
--

DROP TABLE IF EXISTS `user_file_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_file_event` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_file_id` int(10) unsigned NOT NULL,
  `string` varchar(768) DEFAULT NULL,
  `date_added` datetime DEFAULT NULL,
  `date_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-02-16 18:06:08

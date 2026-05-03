/*
SQLyog Community v13.1.1 (64 bit)
MySQL - 5.5.29 : Database - careerconnect
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`careerconnect` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;

USE `careerconnect`;

/*Table structure for table `admin_logs` */

DROP TABLE IF EXISTS `admin_logs`;

CREATE TABLE `admin_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `details` text COLLATE utf8_unicode_ci,
  `user_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `admin_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `admin_logs` */

insert  into `admin_logs`(`id`,`action`,`details`,`user_id`,`created_at`) values 
(1,'Approved job: Software Engineer',NULL,1,'2025-11-07 07:53:56');

/*Table structure for table `applications` */

DROP TABLE IF EXISTS `applications`;

CREATE TABLE `applications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `graduate_id` int(11) NOT NULL,
  `job_id` int(11) NOT NULL,
  `cover_letter` text COLLATE utf8_unicode_ci,
  `status` enum('pending','reviewed','shortlisted','rejected','hired') COLLATE utf8_unicode_ci DEFAULT 'pending',
  `match_score` float DEFAULT NULL,
  `applied_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_application` (`graduate_id`,`job_id`),
  KEY `idx_graduate_id` (`graduate_id`),
  KEY `idx_job_id` (`job_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `applications_ibfk_1` FOREIGN KEY (`graduate_id`) REFERENCES `graduates` (`id`) ON DELETE CASCADE,
  CONSTRAINT `applications_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `applications` */

insert  into `applications`(`id`,`graduate_id`,`job_id`,`cover_letter`,`status`,`match_score`,`applied_at`,`updated_at`) values 
(1,1,1,'Dear Sir/Madam,\r\n\r\nI am applying for the Software Developer position in your organization. I have skills in Python, HTML, and CSS and a strong interest in software and web development. I am eager to contribute my knowledge, learn new technologies, and grow with your team.\r\n\r\nThank you for considering my application.','shortlisted',60,'2025-11-07 08:16:39','2025-11-07 08:18:26');

/*Table structure for table `employers` */

DROP TABLE IF EXISTS `employers`;

CREATE TABLE `employers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `company_name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `company_description` text COLLATE utf8_unicode_ci,
  `industry` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `website` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `employers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `employers` */

insert  into `employers`(`id`,`user_id`,`company_name`,`company_description`,`industry`,`website`,`phone`,`created_at`,`updated_at`) values 
(1,3,'TCS','Tata Consultancy Services (TCS) is a global IT services, consulting, and business solutions organization. Headquartered in Mumbai, India, TCS is part of the Tata Group and operates in over 45 countries. The company provides services such as software development, digital transformation, cloud computing, data analytics, and IT consulting to clients across various industries.','Technology','https://www.tcs.com/','8989876789','2025-11-07 07:45:45','2025-11-07 07:47:45');

/*Table structure for table `graduates` */

DROP TABLE IF EXISTS `graduates`;

CREATE TABLE `graduates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `education` text COLLATE utf8_unicode_ci,
  `skills` text COLLATE utf8_unicode_ci,
  `resume_text` text COLLATE utf8_unicode_ci,
  `resume_file` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `graduates_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `graduates` */

insert  into `graduates`(`id`,`user_id`,`full_name`,`phone`,`education`,`skills`,`resume_text`,`resume_file`,`created_at`,`updated_at`) values 
(1,2,'aravind','9603373433','Bachelor’s degree in Computer Science',' \r\n                                        \r\n                                    \r\nPython, HTML, CSS, JavaScript, SQL      \r\n                                    \r\n                                        \r\n                                    \r\n                                        \r\n                                    ','Career Objective:\r\nTo obtain a position where I can apply my skills in Python, HTML, and CSS to develop efficient, user-friendly, and responsive applications while continuing to learn and grow in the software development field.\r\n\r\nTechnical Skills:\r\nProgramming Languages: Python\r\nWeb Technologies: HTML, CSS\r\nTools: VS Code, GitHub\r\nOperating System: Windows\r\n\r\nAcademic Qualification:\r\nBachelor’s Degree in Computer Science / Information Technology\r\nJNTU,2025\r\n\r\nProjects:\r\nPortfolio Website: Designed and developed a personal portfolio using HTML and CSS.\r\nPython Mini Project: Created a small Python application for data processing/automation.\r\n\r\nStrengths:\r\nQuick learner and problem solver\r\nStrong logical and analytical skills\r\nGood communication and teamwork',NULL,'2025-11-07 07:43:24','2025-11-07 08:10:40');

/*Table structure for table `jobs` */

DROP TABLE IF EXISTS `jobs`;

CREATE TABLE `jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employer_id` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `requirements` text COLLATE utf8_unicode_ci,
  `location` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `salary_range` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `job_type` enum('full-time','part-time','internship','contract') COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_approved` tinyint(1) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_employer_id` (`employer_id`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_is_approved` (`is_approved`),
  CONSTRAINT `jobs_ibfk_1` FOREIGN KEY (`employer_id`) REFERENCES `employers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `jobs` */

insert  into `jobs`(`id`,`employer_id`,`title`,`description`,`requirements`,`location`,`salary_range`,`job_type`,`is_active`,`is_approved`,`created_at`,`updated_at`) values 
(1,1,'Software Engineer','Job Description:\r\nWe are seeking a talented Software Engineer to design, develop, and maintain high-quality software solutions. The candidate should have strong coding, problem-solving, and teamwork skills.\r\n\r\nResponsibilities:\r\nDevelop and maintain software applications.\r\nCollaborate with team members on design and implementation.\r\nWrite clean, efficient, and testable code.\r\nTroubleshoot and fix software issues.\r\nStay updated with new technologies.\r\n\r\nRequirements:\r\nBachelor’s degree in Computer Science or related field.\r\nProficient in Python, HTML, CSS, JavaScript or similar.\r\nKnowledge of frameworks, databases, and APIs.\r\nStrong analytical and communication skills.','Python, HTML, CSS, JavaScript, SQL','Hyderabad','90000','full-time',1,1,'2025-11-07 07:51:30','2025-11-07 07:53:56');

/*Table structure for table `match_analytics` */

DROP TABLE IF EXISTS `match_analytics`;

CREATE TABLE `match_analytics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `graduate_id` int(11) DEFAULT NULL,
  `job_id` int(11) DEFAULT NULL,
  `skill_match_score` float DEFAULT NULL,
  `text_similarity_score` float DEFAULT NULL,
  `overall_match_score` float DEFAULT NULL,
  `algorithm_version` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_graduate_id` (`graduate_id`),
  KEY `idx_job_id` (`job_id`),
  CONSTRAINT `match_analytics_ibfk_1` FOREIGN KEY (`graduate_id`) REFERENCES `graduates` (`id`) ON DELETE SET NULL,
  CONSTRAINT `match_analytics_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `match_analytics` */

insert  into `match_analytics`(`id`,`graduate_id`,`job_id`,`skill_match_score`,`text_similarity_score`,`overall_match_score`,`algorithm_version`,`created_at`) values 
(1,1,1,100,0,60,'v1.2','2025-11-07 08:01:22');

/*Table structure for table `notifications` */

DROP TABLE IF EXISTS `notifications`;

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `message` text COLLATE utf8_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `notifications` */

insert  into `notifications`(`id`,`user_id`,`title`,`message`,`is_read`,`created_at`) values 
(1,3,'New Application','aravind applied for your job: Software Engineer',0,'2025-11-07 08:16:39'),
(2,2,'Application Status Updated','Your application for Software Engineer has been shortlisted',0,'2025-11-07 08:18:26');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(120) COLLATE utf8_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `user_type` enum('graduate','employer','admin') COLLATE utf8_unicode_ci NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_email` (`email`),
  KEY `idx_user_type` (`user_type`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*Data for the table `users` */

insert  into `users`(`id`,`email`,`password_hash`,`user_type`,`is_active`,`created_at`,`updated_at`) values 
(1,'admin@gmail.com','pbkdf2:sha256:260000$aE7tdMqnv9J0ZQNY$39ce53726612f230d274b5f0c9a0bf15dcbe0d68ad1e2ab68ff47bc4eda21a94','admin',1,'2025-11-07 07:40:49','2025-11-07 07:40:49'),
(2,'aravind@gmail.com','pbkdf2:sha256:260000$jDZSswMrxrusQXiS$0d21a22ab67a4c3969a6ee2ecdeea4530a09458ef380d15355ebaea4e7ca08ca','graduate',1,'2025-11-07 07:43:24','2025-11-07 07:43:24'),
(3,'hr.jobs@tcs.com','pbkdf2:sha256:260000$wc8gAAwSZNHDv2fS$2f600830f89750b296fde5f6dec8a5b08ac4e1913c7348ae9d0ac6f2a4040e4c','employer',1,'2025-11-07 07:45:45','2025-11-07 07:45:45');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

/*
 Navicat Premium Data Transfer

 Source Server         : bj.muztak.cn ehua
 Source Server Type    : MySQL
 Source Server Version : 80018
 Source Host           : bj.muztak.cn:63306
 Source Schema         : www_ehua_ru

 Target Server Type    : MySQL
 Target Server Version : 80018
 File Encoding         : 65001

 Date: 13/06/2022 15:24:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for eh_thread
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread`;
CREATE TABLE `eh_thread`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `title` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `ip` char(39) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `has_enroll` tinyint(1) NOT NULL,
  `has_fee` tinyint(1) NOT NULL,
  `has_comment` tinyint(1) NOT NULL,
  `cover` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `video` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `photos` json NULL,
  `files` json NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `logs` json NULL,
  `auth_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `classify_id` int(11) NULL DEFAULT NULL,
  `show_id` int(11) NULL DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `author` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `is_original` tinyint(1) NOT NULL,
  `price` decimal(32, 8) NULL DEFAULT NULL,
  `more` json NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `eh_thread_auth_id_4ba1b73f_fk_eh_thread_auth_id`(`auth_id`) USING BTREE,
  INDEX `eh_thread_category_id_83d71a7b_fk_eh_thread_category_id`(`category_id`) USING BTREE,
  INDEX `eh_thread_classify_id_6d669669_fk_eh_thread_classify_id`(`classify_id`) USING BTREE,
  INDEX `eh_thread_show_id_bd20d39c_fk_eh_thread_show_id`(`show_id`) USING BTREE,
  INDEX `eh_thread_title_91293eff`(`title`) USING BTREE,
  INDEX `eh_thread_user_id_9f31dde5`(`user_id`) USING BTREE,
  INDEX `eh_thread_price_e356e61e`(`price`) USING BTREE,
  CONSTRAINT `eh_thread_auth_id_4ba1b73f_fk_eh_thread_auth_id` FOREIGN KEY (`auth_id`) REFERENCES `eh_thread_auth` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_thread_category_id_83d71a7b_fk_eh_thread_category_id` FOREIGN KEY (`category_id`) REFERENCES `eh_thread_category` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_thread_classify_id_6d669669_fk_eh_thread_classify_id` FOREIGN KEY (`classify_id`) REFERENCES `eh_thread_classify` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_thread_show_id_bd20d39c_fk_eh_thread_show_id` FOREIGN KEY (`show_id`) REFERENCES `eh_thread_show` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 75 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_auth
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_auth`;
CREATE TABLE `eh_thread_auth`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_category
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_category`;
CREATE TABLE `eh_thread_category`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_classify
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_classify`;
CREATE TABLE `eh_thread_classify`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `show_id` int(11) NOT NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `category_id` int(11) NULL DEFAULT NULL COMMENT '父类别',
  `icon` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '图标',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `value`(`value`) USING BTREE,
  INDEX `eh_thread_classify_show_id_65500964_fk_eh_thread_show_id`(`show_id`) USING BTREE,
  INDEX `eh_thread_classify_category_id_0001_fk_eh_thread_category_id`(`category_id`) USING BTREE,
  CONSTRAINT `eh_thread_classify_category_id_0001_fk_eh_thread_category_id` FOREIGN KEY (`category_id`) REFERENCES `eh_thread_category` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_thread_classify_show_id_65500964_fk_eh_thread_show_id` FOREIGN KEY (`show_id`) REFERENCES `eh_thread_show` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 417 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_extend_data
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_extend_data`;
CREATE TABLE `eh_thread_extend_data`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `field_1` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `field_2` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_3` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_4` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_5` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_6` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_7` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_8` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_9` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_10` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_11` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_12` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_13` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_14` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_15` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_16` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_17` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_18` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_19` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `field_20` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `thread_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `eh_thread_extend_data_thread_id_89eebd4a_fk_eh_thread_id`(`thread_id`) USING BTREE,
  CONSTRAINT `eh_thread_extend_data_thread_id_89eebd4a_fk_eh_thread_id` FOREIGN KEY (`thread_id`) REFERENCES `eh_thread` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_extend_field
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_extend_field`;
CREATE TABLE `eh_thread_extend_field`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `field` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `value` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `classify_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `eh_thread_extend_field_classify_id_field_537821d6_uniq`(`classify_id`, `field`) USING BTREE,
  CONSTRAINT `eh_thread_extend_fie_classify_id_b341a273_fk_eh_thread` FOREIGN KEY (`classify_id`) REFERENCES `eh_thread_classify` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_image_auth
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_image_auth`;
CREATE TABLE `eh_thread_image_auth`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_resource
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_resource`;
CREATE TABLE `eh_thread_resource`  (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `url` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `filename` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `filetype` smallint(6) NULL DEFAULT NULL,
  `format` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `price` decimal(32, 8) NULL DEFAULT NULL,
  `snapshot` json NULL,
  `logs` json NULL,
  `image_auth_id` int(11) NULL DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `eh_thread_resource_user_id_647f8542_fk_mz_user_id`(`user_id`) USING BTREE,
  INDEX `eh_thread_resource_image_auth_id_2662cb84_fk_eh_thread`(`image_auth_id`) USING BTREE,
  INDEX `eh_thread_resource_price_9bc424eb`(`price`) USING BTREE,
  CONSTRAINT `eh_thread_resource_image_auth_id_2662cb84_fk_eh_thread` FOREIGN KEY (`image_auth_id`) REFERENCES `eh_thread_image_auth` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_show
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_show`;
CREATE TABLE `eh_thread_show`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `config` json NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT ' ',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_statistic
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_statistic`;
CREATE TABLE `eh_thread_statistic`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `flag_classifies` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `flag_weights` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `weight` double NOT NULL,
  `views` int(11) NOT NULL,
  `plays` int(11) NOT NULL,
  `comments` int(11) NOT NULL,
  `likes` int(11) NOT NULL,
  `favorite` int(11) NOT NULL,
  `shares` int(11) NOT NULL,
  `thread_id_id` bigint(20) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `thread_id_id`(`thread_id_id`) USING BTREE,
  INDEX `eh_thread_statistic_weight_3752b28a`(`weight`) USING BTREE,
  CONSTRAINT `eh_thread_statistic_thread_id_id_7763ffcc_fk_eh_thread_id` FOREIGN KEY (`thread_id_id`) REFERENCES `eh_thread` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_tag
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_tag`;
CREATE TABLE `eh_thread_tag`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_tag_mapping
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_tag_mapping`;
CREATE TABLE `eh_thread_tag_mapping`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_id` int(11) NOT NULL,
  `thread_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `eh_thread_tag_mapping_tag_id_0e339c9b_fk_eh_thread_tag_id`(`tag_id`) USING BTREE,
  INDEX `eh_thread_tag_mapping_thread_id_eceb96e8_fk_eh_thread_id`(`thread_id`) USING BTREE,
  CONSTRAINT `eh_thread_tag_mapping_tag_id_0e339c9b_fk_eh_thread_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `eh_thread_tag` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_thread_tag_mapping_thread_id_eceb96e8_fk_eh_thread_id` FOREIGN KEY (`thread_id`) REFERENCES `eh_thread` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 456 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_thread_to_resource
-- ----------------------------
DROP TABLE IF EXISTS `eh_thread_to_resource`;
CREATE TABLE `eh_thread_to_resource`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resource_id` bigint(20) NOT NULL,
  `thread_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `eh_thread_to_resourc_resource_id_ab2eab84_fk_eh_thread`(`resource_id`) USING BTREE,
  INDEX `eh_thread_to_resource_thread_id_9d5d277d_fk_eh_thread_id`(`thread_id`) USING BTREE,
  CONSTRAINT `eh_thread_to_resourc_resource_id_ab2eab84_fk_eh_thread` FOREIGN KEY (`resource_id`) REFERENCES `eh_thread_resource` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_thread_to_resource_thread_id_9d5d277d_fk_eh_thread_id` FOREIGN KEY (`thread_id`) REFERENCES `eh_thread` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_transact
-- ----------------------------
DROP TABLE IF EXISTS `eh_transact`;
CREATE TABLE `eh_transact`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `amount` decimal(32, 2) NOT NULL,
  `balance` decimal(32, 2) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `snapshot` json NULL,
  `currency_id` int(11) NOT NULL,
  `pay_mode_id` int(11) NOT NULL,
  `thread_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `eh_transact_currency_id_a6ec55bb_fk_eh_transact_currency_id`(`currency_id`) USING BTREE,
  INDEX `eh_transact_pay_mode_id_3ca69012_fk_eh_transact_paymode_id`(`pay_mode_id`) USING BTREE,
  INDEX `eh_transact_thread_id_f492b164_fk_eh_thread_id`(`thread_id`) USING BTREE,
  INDEX `eh_transact_user_id_7723fcf3_fk_mz_user_id`(`user_id`) USING BTREE,
  INDEX `eh_transact_amount_a5ca65d2`(`amount`) USING BTREE,
  INDEX `eh_transact_balance_18c9a594`(`balance`) USING BTREE,
  CONSTRAINT `eh_transact_currency_id_a6ec55bb_fk_eh_transact_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `eh_transact_currency` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_transact_pay_mode_id_3ca69012_fk_eh_transact_paymode_id` FOREIGN KEY (`pay_mode_id`) REFERENCES `eh_transact_paymode` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_transact_thread_id_f492b164_fk_eh_thread_id` FOREIGN KEY (`thread_id`) REFERENCES `eh_thread` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `eh_transact_user_id_7723fcf3_fk_mz_user_id` FOREIGN KEY (`user_id`) REFERENCES `del_mz_user_v3` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_transact_currency
-- ----------------------------
DROP TABLE IF EXISTS `eh_transact_currency`;
CREATE TABLE `eh_transact_currency`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `is_virtual` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for eh_transact_paymode
-- ----------------------------
DROP TABLE IF EXISTS `eh_transact_paymode`;
CREATE TABLE `eh_transact_paymode`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;

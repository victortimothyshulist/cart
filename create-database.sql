CREATE SCHEMA <DB_NAME>;
CREATE TABLE `<DB_NAME>`.`concepts` (
  `tid` INT NOT NULL AUTO_INCREMENT,  
  `description` VARCHAR(255) NOT NULL,
 PRIMARY KEY (`tid`));
CREATE TABLE `<DB_NAME>`.`concept_symbols` (
  `tidref` INT NOT NULL,
  `idx` TINYINT NULL,
  `type` TINYINT NULL,
  `name` VARCHAR(160) NULL);
CREATE TABLE `<DB_NAME>`.`rr_catalogue` (
  `cidref` INT NOT NULL,
  `id` TINYINT NOT NULL,
  `name` VARCHAR(160) NULL);
CREATE TABLE `<DB_NAME>`.`rr_relations` (
  `cidref` INT NOT NULL,
  `rr_catalogue_id` TINYINT NOT NULL,
  `class_text_lines_type` CHAR(2) NOT NULL,
  `class_text_lines_idx` TINYINT NULL,
  `vn` TINYINT NOT NULL);
CREATE TABLE `<DB_NAME>`.`class` (
  `cid` INT NOT NULL AUTO_INCREMENT,
  `cnt_i` TINYINT NOT NULL,
  `cnt_c1` TINYINT NOT NULL,
  `cnt_c2` TINYINT NOT NULL,
  `cnt_o1` TINYINT NOT NULL,
  `cnt_o2` TINYINT NOT NULL,
  `cnt_o3` TINYINT NOT NULL,
  `cnt_o4` TINYINT NOT NULL,
  PRIMARY KEY (`cid`));
CREATE TABLE `<DB_NAME>`.`class_text_lines` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cidref` INT NOT NULL,
  `type` CHAR(3) NOT NULL,
  `idx` TINYINT NOT NULL,
  `tidref` INT NULL,
  `domain` CHAR NULL,
  `exist` CHAR NULL,
  `text` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`));
CREATE TABLE `<DB_NAME>`.`class_select_statements` (
  `cidref` INT NOT NULL,
  `idx` TINYINT NOT NULL,
  `sql_select_statement` VARCHAR(255) NULL);
CREATE TABLE `<DB_NAME>`.`class_extra_conditions` (
  `cidref` INT NOT NULL,
  `type` CHAR NOT NULL,
  `idx` TINYINT NOT NULL,
  `vn` TINYINT NOT NULL,
  `name` VARCHAR(40) NOT NULL,
  `is_cons` CHAR NULL);
CREATE TABLE `<DB_NAME>`.`rr_group_member_conditions` (
  `cidref` INT NOT NULL,
  `rr_catalogue_id` TINYINT NOT NULL,
  `group_name` VARCHAR(60) NOT NULL,
  `exist` CHAR(1) NOT NULL);
CREATE TABLE `<DB_NAME>`.`sr_group_member_conditions` (
  `cidref` INT NOT NULL,
  `sr_name` VARCHAR(40) NOT NULL,
  `group_name` VARCHAR(60) NOT NULL,
  `exist` CHAR(1) NOT NULL);
CREATE TABLE `<DB_NAME>`.`smol_variables` (
  `class_text_lines_id_ref` INT NOT NULL,
  `vn` TINYINT NOT NULL,
  `vtype` CHAR NULL,
  `sr_name` CHAR(40) NULL,
  `is_cons` CHAR NULL,
   FOREIGN KEY(`class_text_lines_id_ref`) REFERENCES class_text_lines(id)
);
CREATE TABLE `<DB_NAME>`.`syn_rr_to_rr` (
   `cidref` INT NOT NULL,
   `rr_catalogue_id_1` TINYINT NOT NULL,
   `rr_catalogue_id_2` TINYINT NOT NULL,
   `polarity` CHAR NOT NULL
);
CREATE TABLE `<DB_NAME>`.`syn_rr_to_sr` (
   `cidref` INT NOT NULL,
   `rr_catalogue_id` TINYINT NOT NULL,
   `sr_name` CHAR(80) NOT NULL,
   `is_cons` CHAR NOT NULL,
   `polarity` CHAR NOT NULL
);
CREATE TABLE `<DB_NAME>`.`syn_sr_to_sr` (
   `cidref` INT NOT NULL,
   `sr_name_1` CHAR(80) NOT NULL,
   `sr_name_2` CHAR(80) NOT NULL,
   `second_sr_is_cons` CHAR NOT NULL,
   `polarity` CHAR NOT NULL
);
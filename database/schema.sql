CREATE TABLE `f_b0c04c39__decisions` (
  `id` CHAR(36) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_4912e07a__app_state` (
  `id` CHAR(36) NOT NULL,
  `has_completed_welcome` TINYINT(1) NOT NULL,
  `welcome_completed_at` TIMESTAMP NULL DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_5842f653__options` (
  `id` CHAR(36) NOT NULL,
  `decision_id` CHAR(36) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_317af9dd__decisions` (
  `id` CHAR(36) NOT NULL,
  `title` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE `f_317af9dd__options` (
  `id` CHAR(36) NOT NULL,
  `decision_id` CHAR(36) NOT NULL,
  `title` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_options_decision` FOREIGN KEY (`decision_id`) REFERENCES `f_317af9dd__decisions`(`id`)
) ENGINE=InnoDB;

CREATE TABLE `f_317af9dd__pros_and_cons` (
  `id` CHAR(36) NOT NULL,
  `option_id` CHAR(36) NOT NULL,
  `type` VARCHAR(3) NOT NULL,
  `text` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_pros_cons_option` FOREIGN KEY (`option_id`) REFERENCES `f_317af9dd__options`(`id`)
) ENGINE=InnoDB;


CREATE TABLE `f_46c88fe8__options` (
  `id` CHAR(36) NOT NULL,
  `decision_id` CHAR(36) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `f_46c88fe8__pros_cons` (
  `id` CHAR(36) NOT NULL,
  `option_id` CHAR(36) NOT NULL,
  `type` VARCHAR(3) NOT NULL,
  `text` LONGTEXT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_pros_cons_option` FOREIGN KEY (`option_id`) REFERENCES `f_46c88fe8__options`(`id`) ON DELETE CASCADE,
  CHECK (`type` IN ('pro','con'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE f_65ce57ac__options (
  id CHAR(36) NOT NULL,
  decision_id CHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE f_65ce57ac__pros_cons (
  id CHAR(36) NOT NULL,
  option_id CHAR(36) NOT NULL,
  type ENUM('pro','con') NOT NULL,
  text TEXT NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_pros_cons_option FOREIGN KEY (option_id) REFERENCES f_65ce57ac__options(id)
) ENGINE=InnoDB;


CREATE TABLE `f_c4ce6dc3__decisions` (
  `id` CHAR(36) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `created_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `f_da734ec2__pro_con_item` (
  `id` CHAR(36) NOT NULL,
  `option_id` CHAR(36) NOT NULL,
  `type` ENUM('pro','con') NOT NULL,
  `text` LONGTEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- No database tables are required for feature: capability_compare_options_view_26824870

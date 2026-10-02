-- Clean MySQL schema for Decision Tracker.
-- Replaces the generated Zorentia schema that duplicated tables and FK names.

CREATE TABLE IF NOT EXISTS `decisions` (
  `id` CHAR(36) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `created_at` DATETIME(6) NOT NULL,
  `updated_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `decision_options` (
  `id` CHAR(36) NOT NULL,
  `decision_id` CHAR(36) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `is_selected` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME(6) NOT NULL,
  `updated_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_decision_options_decision_id` (`decision_id`),
  CONSTRAINT `fk_decision_options_decision`
    FOREIGN KEY (`decision_id`) REFERENCES `decisions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `pros_cons` (
  `id` CHAR(36) NOT NULL,
  `option_id` CHAR(36) NOT NULL,
  `type` VARCHAR(3) NOT NULL,
  `text` TEXT NOT NULL,
  `created_at` DATETIME(6) NOT NULL,
  `updated_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_pros_cons_option_id` (`option_id`),
  CONSTRAINT `fk_pros_cons_option`
    FOREIGN KEY (`option_id`) REFERENCES `decision_options` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_pros_cons_type` CHECK (`type` IN ('pro', 'con'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

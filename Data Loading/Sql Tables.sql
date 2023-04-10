CREATE TABLE `listing_detail_stage` (
  `listing_id` bigint(20) DEFAULT NULL,
  `listing_url` varchar(255) DEFAULT NULL,
  `scrape_id` bigint(20) DEFAULT NULL,
  `last_scraped` date DEFAULT NULL,
  `listing_name` varchar(255) DEFAULT NULL,
  `description` text,
  `neighborhood_overview` text,
  `picture_url` varchar(255) DEFAULT NULL,
  `host_id` bigint(20) DEFAULT NULL,
  `host_url` varchar(100) DEFAULT NULL,
  `host_name` varchar(50) DEFAULT NULL,
  `host_since` date DEFAULT NULL,
  `host_location` varchar(50) DEFAULT NULL,
  `host_about` text,
  `host_response_time` varchar(50) DEFAULT NULL,
  `host_response_rate` double DEFAULT NULL,
  `host_acceptance_rate` double DEFAULT NULL,
  `host_is_superhost` smallint(6) DEFAULT NULL,
  `host_thumbnail_url` varchar(150) DEFAULT NULL,
  `host_picture_url` varchar(150) DEFAULT NULL,
  `host_neighbourhood` varchar(100) DEFAULT NULL,
  `host_listings_count` smallint(6) DEFAULT NULL,
  `host_total_listings_count` smallint(6) DEFAULT NULL,
  `host_verifications` varchar(100) DEFAULT NULL,
  `host_has_profile_pic` smallint(6) DEFAULT NULL,
  `host_identity_verified` smallint(6) DEFAULT NULL,
  `neighbourhood` varchar(100) DEFAULT NULL,
  `neighbourhood_cleansed` int(11) DEFAULT NULL,
  `neighbourhood_group_cleansed` int(11) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `property_type` varchar(50) DEFAULT NULL,
  `room_type` varchar(50) DEFAULT NULL,
  `accommodates` smallint(6) DEFAULT NULL,
  `bathrooms` smallint(6) DEFAULT NULL,
  `bathrooms_text` varchar(100) DEFAULT NULL,
  `bedrooms` smallint(6) DEFAULT NULL,
  `beds` smallint(6) DEFAULT NULL,
  `amenities` varchar(3000) DEFAULT NULL,
  `price` double DEFAULT NULL,
  `minimum_nights` smallint(6) DEFAULT NULL,
  `maximum_nights` int(11) DEFAULT NULL,
  `minimum_minimum_nights` int(11) DEFAULT NULL,
  `maximum_minimum_nights` int(11) DEFAULT NULL,
  `minimum_maximum_nights` int(11) DEFAULT NULL,
  `maximum_maximum_nights` int(11) DEFAULT NULL,
  `minimum_nights_avg_ntm` int(11) DEFAULT NULL,
  `maximum_nights_avg_ntm` int(11) DEFAULT NULL,
  `calendar_updated` smallint(6) DEFAULT NULL,
  `has_availability` smallint(6) DEFAULT NULL,
  `availability_30` int(11) DEFAULT NULL,
  `availability_60` int(11) DEFAULT NULL,
  `availability_90` int(11) DEFAULT NULL,
  `availability_365` int(11) DEFAULT NULL,
  `calendar_last_scraped` date DEFAULT NULL,
  `number_of_reviews` int(11) DEFAULT NULL,
  `number_of_reviews_ltm` int(11) DEFAULT NULL,
  `number_of_reviews_l30d` int(11) DEFAULT NULL,
  `first_review` date DEFAULT NULL,
  `last_review` date DEFAULT NULL,
  `review_scores_rating` double DEFAULT NULL,
  `review_scores_accuracy` double DEFAULT NULL,
  `review_scores_cleanliness` double DEFAULT NULL,
  `review_scores_checkin` double DEFAULT NULL,
  `review_scores_communication` double DEFAULT NULL,
  `review_scores_location` double DEFAULT NULL,
  `review_scores_value` double DEFAULT NULL,
  `license` smallint(6) DEFAULT NULL,
  `instant_bookable` smallint(6) DEFAULT NULL,
  `calculated_host_listings_count` smallint(6) DEFAULT NULL,
  `calculated_host_listings_count_entire_homes` smallint(6) DEFAULT NULL,
  `calculated_host_listings_count_private_rooms` smallint(6) DEFAULT NULL,
  `calculated_host_listings_count_shared_rooms` smallint(6) DEFAULT NULL,
  `reviews_per_month` double DEFAULT NULL,
  `scrape_city` varchar(50) DEFAULT NULL,
  KEY `listing_detail_stage_listing_id_IDX` (`listing_id`) USING BTREE,
  KEY `listing_detail_stage_scrape_city_IDX` (`scrape_city`) USING BTREE,
  KEY `listing_detail_stage_listing_id_scraped_IDX` (`listing_id`,`last_scraped`) USING BTREE,
  KEY `listing_detail_stage_listing_id_scraped_date_IDX` (`listing_id`,`last_scraped`) USING BTREE,
  KEY `listing_detail_stage_amenities_IDX` (`amenities`) USING BTREE,
  KEY `listing_detail_stage_listing_id_scraped_city_IDX` (`listing_id`,`scrape_city`,`last_scraped`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



CREATE TABLE `reviews_stage` (
  `listing_id` bigint(20) DEFAULT NULL,
  `id` bigint(20) DEFAULT NULL,
  `review_date` date DEFAULT NULL,
  `reviewer_id` bigint(20) DEFAULT NULL,
  `reviewer_name` text,
  `comments` text,
  `scrape_city` varchar(100) DEFAULT NULL,
  KEY `reviews_stage_listing_id_IDX` (`listing_id`) USING BTREE,
  KEY `reviews_stage_scrape_city_IDX` (`scrape_city`) USING BTREE,
  KEY `reviews_stage_listing_id_scrape` (`listing_id`,`scrape_city`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `listing_calendar` (
  `listing_id` bigint(20) DEFAULT NULL,
  KEY `listing_calendar_listing_id_IDX` (`listing_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `listing_last_scraped` (
  `listing_id` bigint(20) DEFAULT NULL,
  `last_scraped_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `listing_occup` (
  `listing_id` bigint(20) DEFAULT NULL,
  `avg_occup` double DEFAULT NULL,
  KEY `listing_occup_listing_id_IDX` (`listing_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `pricing_features` (
  `scrape_city` varchar(100) DEFAULT NULL,
  `amenity` varchar(100) DEFAULT NULL,
  `score` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `top_amenities` (
  `amenity` text,
  `score` double DEFAULT NULL,
  `scrape_city` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `top_reviews` (
  `pos_word` text,
  `pos_score` double DEFAULT NULL,
  `neg_word` text,
  `neg_score` double DEFAULT NULL,
  `scrape_city` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
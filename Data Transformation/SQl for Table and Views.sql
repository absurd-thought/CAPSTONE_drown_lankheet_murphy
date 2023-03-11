/*creating table with specific column detail*/
Create table listing_detail_stage (
	listing_id bigint,
	listing_url varchar(255),
	scrape_id bigint,
	last_scraped date,

	listing_name varchar(255),
	description text,
	neighborhood_overview text,
	picture_url varchar(255),
	host_id bigint,
	host_url varchar(100),
	host_name varchar(50),
	host_since date,
	host_location varchar(50),
	host_about text,
	host_response_time varchar(50),
	host_response_rate double,
	host_acceptance_rate double,
	host_is_superhost smallint,
	host_thumbnail_url varchar(150),
	host_picture_url varchar(150),
	host_neighbourhood varchar(100),
	host_listings_count smallint,
	host_total_listings_count smallint,
	host_verifications varchar(100),
	host_has_profile_pic smallint,
	host_identity_verified smallint,
	neighbourhood varchar(100),
	neighbourhood_cleansed int,
	neighbourhood_group_cleansed int,
	latitude double,
	longitude double,
	property_type varchar(50),
	room_type varchar(50),
	accommodates smallint,
	bathrooms smallint,
	bathrooms_text varchar(100),
	bedrooms smallint,
	beds smallint,
	amenities text,
	price double,
	minimum_nights smallint,
	maximum_nights int,
	minimum_minimum_nights int,
	maximum_minimum_nights int,
	minimum_maximum_nights int,
	maximum_maximum_nights int,
	minimum_nights_avg_ntm int,
	maximum_nights_avg_ntm int,
	calendar_updated smallint,
	has_availability smallint,
	availability_30 int,
	availability_60 int,
	availability_90 int,
	availability_365 int,
	calendar_last_scraped date,
	number_of_reviews int,
	number_of_reviews_ltm int,
	number_of_reviews_l30d int,
	first_review date,
	last_review date,
	review_scores_rating double,
	review_scores_accuracy double,
	review_scores_cleanliness double,
	review_scores_checkin double,
	review_scores_communication double,
	review_scores_location double,
	review_scores_value double,
	license smallint,
	instant_bookable smallint,
	calculated_host_listings_count smallint,
	calculated_host_listings_count_entire_homes smallint,
	calculated_host_listings_count_private_rooms smallint,
	calculated_host_listings_count_shared_rooms smallint,
	reviews_per_month double,
	scrape_city varchar(50)
)

/*deleting records that were corrupted in loading, totals 15 (out of a million plus)*/
Delete from listing_detail_stage 
where calendar_last_scraped ='0000-00-00'


/*creating a small table that has the last listing and scraped date*/
create table listing_last_scraped (
listing_id bigint
,last_scraped_date date
)

/*inserting into that table the max scrape date*/
insert into listing_last_scraped
Select listing_id
, max(last_scraped) as last_scraped_date 
from listing_detail_stage
group by listing_id  


/*creating a view that returns the latest listing*/
create view recent_listings as
select lds.* from listing_detail_stage lds 
inner join listing_last_scraped lls on lls.listing_id =lds.listing_id and lls.last_scraped_date = lds.last_scraped 

# View that combines current listings with occupancy calculation.  
alter view recent_listings_occup as
select lds.*
,lo.avg_occup
from listing_detail_stage lds 
inner join listing_last_scraped lls on lls.listing_id =lds.listing_id and lls.last_scraped_date = lds.last_scraped 
inner JOIN listing_occup AS lo ON lo.listing_id=lds.listing_id
where minimum_nights <=10

/*creating a view that contains all the listings*/
create view listings as
select lds.* from listing_detail_stage lds 

/*creating a view that contains all the reviews*/
create view reviews as 
select r.* from reviews_stage r

/*replacing bad coding*/
update reviews_stage 
set comments = replace(comments, 'u2013', '-')

/*statement to get average availability*/
select distinct
listing_id 
from listings
where minimum_nights <=10
and availability_90  <> 0
and (availability_90 >10
or last_review >'2022-09-01')

-- insert into listing_occup
Select 
lds.listing_id 
,avg(1-availability_30/30) as avg_occup
from listing_detail_stage lds 
inner join listing_calendar lc on lc.listing_id =lds.listing_id 
group by lds.listing_id

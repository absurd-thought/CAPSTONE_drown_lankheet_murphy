
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

/*replacing
u2013
u2019
’
\
[]
*/

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

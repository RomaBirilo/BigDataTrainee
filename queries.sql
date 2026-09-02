--1.Output the number of movies in each category, sorted descending.
select c.name, count(f.film_id) as film_number
from category as c
inner join film_category as fc on c.category_id = fc.category_id
inner join film as f on fc.film_id = f.film_id
group by c.name
order by film_number desc;

--2.Output the number of movies in each category, sorted descending.
select a.first_name, a.last_name, count(r.rental_id) as rental_count
from actor as a
inner join film_actor as fa on a.actor_id = fa.actor_id
inner join film as f on fa.film_id = f.film_id
inner join inventory as i on f.film_id = i.film_id
inner join rental as r on i.inventory_id = r.inventory_id
group by a.first_name, a.last_name
order by rental_count desc
limit 10;

--3.Output the category of movies on which the most money was spent.
select c.name, sum(p.amount) as total_amount
from category as c 
inner join film_category as fc on c.category_id = fc.category_id
inner join film as f on fc.film_id = f.film_id
inner join inventory as i on f.film_id = i.film_id
inner join rental as r on i.inventory_id = r.inventory_id
inner join payment as p on r.rental_id = p.rental_id
group by c.name
order by total_amount desc
limit 1;

--4.Print the names of movies that are not in the inventory. Write a query without using the IN operator.
select f.title
from film as f 
left join inventory as i on f.film_id = i.film_id
where i.inventory_id is null

--5.Output the top 3 actors who have appeared the most in movies in the “Children” category. If several actors have the same number of movies, output all of them.
with ranked_actors as (
select a.first_name, a.last_name, count(fa.film_id) as number_of_occurrences,
dense_rank() over(order by count(fa.film_id) desc) as rnk
from actor as a
inner join film_actor as fa on a.actor_id = fa.actor_id
inner join film_category as fc on fa.film_id = fc.film_id
inner join category as c on fc.category_id = c.category_id
where c.name = 'Children'
group by a.first_name, a.last_name
)
select * from ranked_actors
where rnk <= 3;

--6.Output cities with the number of active and inactive customers (active - customer.active = 1). Sort by the number of inactive customers in descending order.
select c.city,
count(*) filter (where cs.active = 1) as number_active,
count(*) filter (where cs.active = 0) as number_inactive
from city as c
inner join address as a on c.city_id = a.city_id
inner join customer as cs on a.address_id = cs.address_id
group by c.city
order by number_inactive desc;

--7.Output the category of movies that have the highest number of total rental hours in the city (customer.address_id in this city) and that start with the letter “a”. Do the same for cities that have a “-” in them. Write everything in one query.
with rental_hours_by_city_category as (
select 
c.city,
cat.name as category,
sum(extract(epoch from (r.return_date - r.rental_date)) / 3600) as total_hours
from city as c
inner join address as a on c.city_id = a.city_id
inner join customer as cu on a.address_id = cu.address_id
inner join rental as r on cu.customer_id = r.customer_id
inner join inventory as i on r.inventory_id = i.inventory_id
inner join film as f on i.film_id = f.film_id
inner join film_category as fc on f.film_id = fc.film_id
inner join category as cat on fc.category_id = cat.category_id
where r.return_date is not null
group by c.city, cat.name
),
ranked_categories as (
select 
city,
category,
total_hours,
rank() over (partition by city order by total_hours desc) as rnk
from rental_hours_by_city_category
)
select city, category, total_hours
from ranked_categories
where rnk = 1
and (city ilike 'a%' or city like '%-%')
order by city;


## Check View ##
 Check if a view named **"top_articles"** is excisted or not.
```
SELECT EXISTS (SELECT 1 FROM information_schema.Views WHERE table_name = 'top_articles');
```           
## Create a View ##
Create a view named **'top_articles'** Includes (**author_id ,articles_id ,articles_title and `count(articles.slug))`**.
Method `[count(articles.slug)]` is used for counting all views of all articles written by each authour.
```
CREATE VIEW top_articles AS 
        SELECT authors.id AS author_id ,articles.id AS article_id ,
        articles.title AS article_name,count(articles.slug) AS views 
        FROM articles 
        JOIN log 
        ON ('/article/'::text || articles.slug) = log.path 
        JOIN authors 
        ON articles.author = authors.id 
        GROUP BY 1,2,3
        ORDER BY 4 DESC;
```
## First Query: What are the most popular three articles of all time? ##
Use the View **top_articles** to get the 3 articles
```
SELECT article_name,views 
FROM top_articles 
LIMIT 3;
 ```
    
## Second Query: Who are the most popular article authors of all time?
```
SELECT u.name AS author,SUM(ta.views) AS views 
FROM authors u 
JOIN top_articles ta 
ON u.id = ta.author_id 
GROUP BY 1 
ORDER BY 2 DESC;
 ```
## Third Query: Who are the most popular article authors of all time? ##
Creat a **subquery** that counts the errors in log table for each day.Errors are the status rows that are not like ** '200 OK'. **
```
SELECT DATE_TRUNC('day',time)AS err_time ,COUNT(status) AS err_sum 
	    FROM log 
            WHERE status !='200 OK' 
	    GROUP BY 1
```
Then  create a second subquery that count all status rows in log table for each day.
```
SELECT DATE_TRUNC('day',time)AS req_time ,COUNT(status) AS req_sum 
	    FROM log 
            GROUP BY 1
```
By using those two queries,you can get the days which more than 1% of requests lead to errors.
Using this method `ROUND((err.err_sum*1.0 / req.req_sum)*100,2)` to get the errors percentage and round them up to 2 decimals
```
WITH 
	err AS (SELECT DATE_TRUNC('day',time)AS err_time,COUNT(status) AS err_sum 
	        FROM log 
            	WHERE status !='200 OK' 
	    	GROUP BY 1 ) ,
	req AS (SELECT DATE_TRUNC('day',time)AS req_time ,COUNT(status) AS req_sum 
		FROM log 
            	GROUP BY 1  )  
SELECT req_time,ROUND((err.err_sum*1.0 / req.req_sum)*100,2) AS errors_percentage
FROM req
JOIN err
ON err_time = req_time
GROUP BY 1,2
HAVING ROUND((err.err_sum*1.0 / req.req_sum)*100,2) > 1 ;
```


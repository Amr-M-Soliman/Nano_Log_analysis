#!/usr/bin/env python3
import psycopg2 as psycopg2

DBNAME = 'news'
NAME_PASS = 'postgres'

check_view = "SELECT EXISTS (SELECT 1 FROM information_schema.Views" \
             " WHERE table_name = 'top_articles');"

new_view = "CREATE VIEW top_articles AS SELECT authors.id AS author_id," \
           "articles.id AS article_id ,articles.title AS " \
           "article_name,count(articles.slug) AS views " \
           "FROM articles JOIN log " \
           "ON ('/article/'::text || articles.slug) = log.path " \
           "JOIN authors on  articles.author = authors.id " \
           "GROUP BY 1,2,3 " \
           "ORDER BY 4 DESC ;"

first_query = "SELECT article_name,views FROM top_articles LIMIT 3;"

second_query = "SELECT u.name AS author ,SUM(ta.views) AS views " \
               "FROM authors u JOIN top_articles ta " \
               "ON u.id = ta.author_id GROUP BY 1 ORDER BY 2 DESC;"

third_query = "WITH err AS (SELECT DATE_TRUNC('day',time)AS err_time," \
              "COUNT(status) AS err_sum FROM log " \
              "WHERE status !='200 OK' GROUP BY 1 )," \
              "req AS (SELECT DATE_TRUNC('day',time)AS req_time ," \
              "COUNT(status) AS req_sum FROM log GROUP BY 1)" \
              "SELECT req_time," \
              "ROUND((err.err_sum*1.0 / req.req_sum)*100,2) " \
              "AS errors_percentage " \
              "FROM req JOIN err " \
              "ON err_time = req_time GROUP BY 1,2 " \
              "HAVING ROUND((err.err_sum*1.0 / req.req_sum)*100,2) > 1 "


def create_view():
    try:
        # Connect to news database
        db = psycopg2.connect(database=DBNAME, user=NAME_PASS,
                              password=NAME_PASS)
        c = db.cursor()
        # First you check the view named'top_articles'
        c.execute(check_view)
        view_bool = c.fetchone()[0]
        # If the view is not existed
        if not view_bool:
            # Create a new view named'top_articles'
            c.execute(new_view)
            # add the view to news database
            db.commit()
        # close connection
        db.close()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL using get_query()", error)


def get_query(q):
    try:
        # Connect to news database
        db = psycopg2.connect(database=DBNAME, user=NAME_PASS,
                              password=NAME_PASS)
        # Check the view table named'top_articles'
        create_view()
        c = db.cursor()
        # execute the query
        c.execute(q)
        data = c.fetchall()
        # close connection
        db.close()
        # return query result
        return data
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL using get_query()", error)


# First Query: What are the most popular three articles of all time?
print("First_Query: " + str(get_query(first_query)))
# Second Query: Who are the most popular article authors of all time?
print("Second_Query: " + str(get_query(second_query)))
# Third Query: Who are the most popular article authors of all time?
print("Third_Query: " + str(get_query(third_query)))

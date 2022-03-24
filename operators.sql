-- IN Operator returns products id 2,3,4,5
SELECT p.id AS product_id, p.name AS product_name
FROM public.products p
WHERE p.id IN (2,3,4,5)
ORDER BY p.id ASC;

-- LIKE Operator - returns all names where it starts with TV
SELECT p.id AS product_id, p.name AS product_name
FROM public.products p
WHERE p.name LIKE 'TV%'
ORDER BY p.id ASC;

-- ORDER BY Operator
SELECT p.id AS product_id, p.name AS product_name
FROM public.products p
WHERE p.is_sale=true AND p.name='keyboard'
ORDER BY p.id ASC, p.price DESC;

-- Normal Operators(=/>/</>=/<=)
SELECT p.id AS product_id, p.name AS product_name
FROM public.products p
WHERE p.name='TV' AND p.price>=10
ORDER BY p.id ASC;


-- LIMIT Operator - returns only top 2 results
SELECT p.id AS product_id, p.name AS product_name
FROM public.products p
WHERE p.name='TV' AND p.price>=10
ORDER BY p.id ASC
LIMIT 2;

-- OFFSET Operator - skips by the offset, then returns only top 2 results
SELECT p.id AS product_id, p.name AS product_name
FROM public.products p
WHERE p.name='TV' AND p.price>=10
ORDER BY p.id ASC
LIMIT 2 OFFSET 2;

-- ----------------------------------------------------------------------------------------
-- INSERT OPERATOR - To insert a new row/entry into the database
INSERT INTO products (name, price, stock) VALUES ('tortilla',4,1000)
-- INSERT 0 1 -> means insert worked and 1 row added
-- Query returned successfully in 46 msec.

-- In a CRUD API, when creating a new entry/POSTING, we usually want to return the newly created entry in the response body, but inserting in postgres does not automatically return the newly inserted row. How do we do that?
-- add RETURNING <columns to return> after the statement;

-- returns all columns
INSERT INTO products (name, price, stock) VALUES ('new tortilla',4,1000) RETURNING *; 
-- returns id and name columns
INSERT INTO products (name, price, stock) VALUES ('newer tortilla',4,1000) RETURNING id, name; 

-- can also add more than one row at a time by chaining VALUES portion
INSERT INTO products (name, price, stock) VALUES ('new tortilla',4,1000), ('dog',4,1000), ('new cat',4,1000) RETURNING *; 

-- ----------------------------------------------------------------------------------------
-- DELETE OPERATOR - To delete a row/entry in the database
DELETE FROM products WHERE id = 11 RETURNING *; -- will delete row with id = 11
DELETE FROM products WHERE stock = 0 RETURNING *; -- will delete ALL rows with stock = 0
-- note: can remove returning keyword if not needed

-- ----------------------------------------------------------------------------------------
-- UPDATE OPERATOR - To update a row/entry in the database
-- New values to change to is indicated in the SET portion
-- What to change is indicated in the WHERE portion 
UPDATE products SET name = 'Flour tortilla', price=40 WHERE name='tortilla' RETURNING *;
UPDATE products SET is_sale = true, price=40 WHERE id>5 RETURNING *;
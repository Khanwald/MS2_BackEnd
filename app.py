from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import request, jsonify
import config
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"

db = SQLAlchemy(app)

def getQuery(query, cond=None):
    if cond == None:
        cond={}
        
    result = db.session.execute(text(query), cond)
    output = []
    for row in result:
        output.append(dict(row._mapping)) 
    return output

@app.route('/api/topFilms')
def films():
    result = "SELECT f.film_id,f.title, COUNT(DISTINCT r.rental_id) AS rental_count FROM film f JOIN film_actor fa ON f.film_id = fa.film_id JOIN actor a ON fa.actor_id = a.actor_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.film_id, f.title ORDER BY rental_count desc limit 5"
    ouput = getQuery(result)
    return jsonify({"films": ouput})

@app.route('/api/getTopActors')
def topActors():
    result = "SELECT a.actor_id, a.first_name, a.last_name, COUNT(DISTINCT i.film_id) AS film_count FROM actor a JOIN film_actor fa ON a.actor_id = fa.actor_id JOIN film f ON fa.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id GROUP BY a.actor_id, a.first_name, a.last_name ORDER BY film_count DESC LIMIT 5"
    output = getQuery(result)
    return jsonify({"actors": output})

@app.route('/api/members', methods=['GET'])
def member():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    value = request.args.get('value', '', type=str)
    items = 10
    index = (page - 1) * items
    end = page * items
    
    
    result = "select customer_id, store_id, first_name, last_name from customer"
    cond={}
    if value == 'fname':
        result = "select customer_id, store_id, first_name, last_name from customer where first_name like :search"
        cond = {"search" : f"{search}%"}
    elif value == 'lname':
        result = "select customer_id, store_id, first_name, last_name from customer where last_name like :search"
        cond = {"search" : f"{search}%"}
    elif value == 'id':
        result = "select customer_id, store_id, first_name, last_name from customer where customer_id like :search"
        cond = {"search" : f"{search}%"}
        
    output = getQuery(result, cond)
    pages = output[index:end]
    totalPages= math.ceil(len(output)/items)
    
    return jsonify({
        "page": page,
        "customerNum": items,
        "total": len(output),
        "customers": pages,
        "totalPages": totalPages
    })

@app.route('/api/memberProfile/<int:customer_id>', methods=['GET'])
def profile(customer_id):
    customerDetails= "select * from customer where customer_id = :id"
    result = "select r.rental_id, r.rental_date, r.return_date, f.title from customer c join rental r on r.customer_id = c.customer_id join inventory i on i.inventory_id = r.inventory_id join film f on i.film_id = f.film_id where c.customer_id = :id"
    cond = {"id" : customer_id}
    output = getQuery(result, cond)
    output2= getQuery(customerDetails, cond)
    return jsonify({"rental": output,
                    "details": output2})

@app.route('/api/getMovie', methods=['GET'])
def getMovie():
    title = request.args.get('title', '', type=str)
    type = request.args.get('type', '', type=str)
    
    if type == "Title":
        result = "select * from film where title LIKE :film_name"
        cond = {"film_name" : f"{title}%"}
    elif type == "Actor":
        result = "select distinct f.film_id, f.title, CONCAT(a.first_name, ' ',a.last_name) as name from film_actor fa join actor a on fa.actor_id = a.actor_id join film f on f.film_id = fa.film_id where CONCAT(a.first_name, ' ', a.last_name) LIKE :actor_name or a.first_name like :actor_name or a.last_name like :actor_name order by f.film_id"
        cond = {"actor_name" : f"{title}%"}
    elif type == "Genre":
        result="select f.film_id, f.title, fc.category_id, c.name from film f join film_category fc on f.film_id = fc.film_id join category c on fc.category_id = c.category_id where c.name like :genre"
        cond = {"genre" : f"{title}%"}
    else:
        return jsonify({"movies": []})
    
    output = getQuery(result, cond)
    return jsonify({"movies": output})

@app.route('/api/getMovieDetails/<int:film_id>')
def getMovieDetails(film_id):
    querya="select f.film_id, f.title, f.description, f.release_year, f.rating, f.special_features, fc.category_id, c.name from film f join film_category fc on f.film_id = fc.film_id join category c on fc.category_id = c.category_id where f.film_id = :id"
    queryb="select a.first_name, a.last_name, f.title from actor a join film_actor fa on a.actor_id = fa.actor_id join film f on f.film_id = fa.film_id where fa.film_id = :id"
    cond = {"id" : film_id}
    
    movieDetails=getQuery(querya,cond)
    actorsInMovie=getQuery(queryb,cond)
    
    return jsonify({"details":movieDetails, "actors":actorsInMovie})
    
if __name__ == "__main__":
    app.run(debug=True)



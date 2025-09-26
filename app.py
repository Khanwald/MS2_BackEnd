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

@app.route('/api/films')
def films():
    result = db.session.execute(text("select f.film_id, f.title, fc.category_id, c.name from film f join film_category fc on f.film_id = fc.film_id  join category c on fc.category_id = c.category_id"))
    output = []
    for row in result:
        output.append({
            "film_id": row.film_id,
            "title": row.title,
            "category_id": row.category_id,
            "category_name": row.name
        })
    
    return jsonify({"films": output})

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
    result = "select c.customer_id, c.first_name, c.last_name, r.rental_id, r.rental_date, r.return_date from customer c join rental r on r.customer_id = c.customer_id where c.customer_id = :id"
    cond = {"id" : customer_id}
    output = getQuery(result, cond)
    return jsonify({"rental": output})

@app.route('/api/getMovie', methods=['GET'])
def getMovie():
    title = request.args.get('title', '', type=str)
    type = request.args.get('type', '', type=str)
    
    if type == "Title":
        result = "select * from film where title LIKE :film_name"
        cond = {"film_name" : f"{title}%"}
    elif type == "Actor":
        result = "select distinct f.film_id, f.title, CONCAT(a.first_name, ' ',a.last_name) as name from film_actor fa join actor a on fa.actor_id = a.actor_id join film f on f.film_id = fa.film_id where CONCAT(a.first_name, ' ', a.last_name) LIKE :actor_name order by f.film_id"
        cond = {"actor_name" : f"{title}%"}
    elif type == "Genre":
        result="select f.film_id, f.title, fc.category_id, c.name from film f join film_category fc on f.film_id = fc.film_id join category c on fc.category_id = c.category_id where c.name like :genre"
        cond = {"genre" : f"{title}%"}
    else:
        return jsonify({"movies": []})
    
    output = getQuery(result, cond)
    return jsonify({"movies": output})

if __name__ == "__main__":
    app.run(debug=True)
    
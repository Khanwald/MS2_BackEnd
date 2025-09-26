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
    items = 10
    index = (page - 1) * items
    end = page * items
    
    result = "select customer_id, store_id, first_name, last_name from customer"
    output = getQuery(result)
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


if __name__ == "__main__":
    app.run(debug=True)
    
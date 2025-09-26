from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import request, jsonify
import config
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"

db = SQLAlchemy(app)


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

@app.route('/api/members')
def member():
    page = request.args.get('page', 1, type=int)
    items = 10
    index = (page - 1) * items
    end = page * items
    
    result = db.session.execute(text("select customer_id, store_id, first_name, last_name from customer"))
    output = []
    for row in result:
        output.append({
            "customer_id": row.customer_id,
            "store_id": row.store_id,
            "first_name": row.first_name,
            "last_name": row.last_name
        })
    pages = output[index:end]
    totalPages= math.ceil(len(output)/items)
    
    return jsonify({
        "page": page,
        "customerNum": items,
        "total": len(output),
        "customers": pages,
        "totalPages": totalPages
    })
    
if __name__ == "__main__":
    app.run(debug=True)
    
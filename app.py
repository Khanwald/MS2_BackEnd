from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import jsonify
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"

db = SQLAlchemy(app)


@app.route('/films')
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

@app.route('/members')
def member():
    return {"members": ["Member1", "Member2", "Member3"]}
    
if __name__ == "__main__":
    app.run(debug=True)
    
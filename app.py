from flask import Flask, render_template, request, flash
from models import db, Category, Product, ProductInfo
from config import BaseConfig

# Application definition
app = Flask(__name__)

# Application configuration
app.config.from_object(BaseConfig)

db.init_app(app)

# Creating database tables and columns

with app.app_context():
    db.create_all()


# Application endpoints


@app.route("/", methods=["GET", "POST"])
def index():
    categories = Category.query.all()
    products = []
    if request.method == "POST":
        product_shops = (
            ProductInfo.query.join(Product, ProductInfo.product == Product.id)
            .join(Category, Product.category == Category.id)
            .filter(Product.name.like("%{}%".format(request.form.get("name"))))
            .filter(Category.id == int(request.form.get("category")))
            .add_columns(
                Product.id,
                Category.name.label("category"),
                Product.name.label("product"),
                ProductInfo.source,
                ProductInfo.source_type,
                ProductInfo.price,
                ProductInfo.url,
            )
            .order_by(ProductInfo.price)
            .all()
        )
        products = product_shops
    return render_template("index.html", categories=categories, products=products)


@app.route("/products")
def product_list():
    products = (
        Product.query.join(Category, Product.category == Category.id)
        .add_columns(
            Category.name.label("category"),
            Product.name.label("product_name"),
            Product.id,
        )
        .all()
    )
    return render_template("products.html", products=products)


@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    categories = Category.query.all()
    if request.method == "POST":
        product = Product(
            name=request.form.get("name"),
            category=int(request.form.get("category")),
            description=request.form.get("description"),
        )
        db.session.add(product)
        db.session.commit()
        flash("Successfully saved product " + str(request.form.get("name")))
    return render_template("add-product.html", categories=categories)


@app.route("/add-category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        name = request.form.get("name")
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash("Successfully saved category")
    return render_template("add-category.html")


@app.route("/products/<id>")
def get_product_info(id):
    product = (
        Product.query.join(Category, Product.category == Category.id)
        .filter(Product.id == id)
        .first()
    )
    return render_template("view-product.html", product=product)


@app.route("/product/<id>/add-info-source", methods=["GET", "POST"])
def add_source_info(id):
    product = (
        Product.query.join(Category, Product.category == Category.id)
        .filter(Product.id == id)
        .first()
    )
    if request.method == "POST":
        product_info = ProductInfo(
            source=request.form.get("name"),
            product=id,
            source_type=request.form.get("type"),
            price=request.form.get("price"),
            url=request.form.get("url"),
        )
        db.session.add(product_info)
        db.session.commit()
        flash("Successfully saved information")
    return render_template("add-shop.html", product=product)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

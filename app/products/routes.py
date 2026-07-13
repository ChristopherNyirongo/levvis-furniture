from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Product, Category, QuoteRequest
from app.extensions import db
products_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../templates/products')
from app.models import Product, Category, QuoteRequest, Testimonial


@products_bp.route('/')
def list_products():
    query = Product.query.filter_by(is_available=True)

    search_term = request.args.get('q', '').strip()
    if search_term:
        like_pattern = f'%{search_term}%'
        query = query.filter(
            db.or_(
                Product.name.ilike(like_pattern),
                Product.material.ilike(like_pattern),
                Product.description.ilike(like_pattern)
            )
        )

    category_id = request.args.get('category', type=int)
    selected_category_obj = None
    if category_id:
        query = query.filter_by(category_id=category_id)
        selected_category_obj = Category.query.get(category_id)

    material = request.args.get('material', '').strip()
    if material:
        query = query.filter(Product.material.ilike(f'%{material}%'))

    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    sort_by = request.args.get('sort', 'featured')
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc().nullslast())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc().nullslast())
    elif sort_by == 'newest':
        query = query.order_by(Product.date_created.desc())
    else:
        query = query.order_by(Product.date_created.desc())

    products = query.all()
    categories = Category.query.all()

    return render_template(
        'products/list.html',
        products=products,
        categories=categories,
        search_term=search_term,
        selected_category=category_id,
        selected_category_obj=selected_category_obj,
        selected_material=material,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    reviews = sorted(product.reviews, key=lambda r: r.date, reverse=True)
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
    recent_reviews = reviews[:2]

    return render_template(
        'products/detail.html',
        product=product,
        related_products=related_products,
        avg_rating=avg_rating,
        recent_reviews=recent_reviews,
        review_count=len(reviews)
    )

@products_bp.route('/<int:product_id>/review', methods=['POST'])
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    rating = request.form.get('rating', type=int) or 5

    review = Testimonial(
        customer_name=request.form.get('customer_name'),
        rating=max(1, min(5, rating)),
        review=request.form.get('review'),
        product_id=product.id
    )
    db.session.add(review)
    db.session.commit()
    flash('Thank you for your review!', 'success')
    return redirect(url_for('products.product_detail', product_id=product.id) + '#reviews')
def submit_quote(product_id):
    product = Product.query.get_or_404(product_id)

    quote = QuoteRequest(
        customer_name=request.form.get('customer_name'),
        phone_number=request.form.get('phone_number'),
        email=request.form.get('email'),
        product_id=product.id,
        quantity=request.form.get('quantity', type=int, default=1),
        delivery_address=request.form.get('delivery_address'),
        notes=request.form.get('notes')
    )

    db.session.add(quote)
    db.session.commit()

    flash('Your quote request has been submitted! We\'ll contact you shortly.', 'success')
    return redirect(url_for('products.product_detail', product_id=product.id))

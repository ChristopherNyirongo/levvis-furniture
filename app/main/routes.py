from flask import Blueprint, render_template
from app.models import Product, Testimonial, Project, Category
from flask import send_from_directory
from flask import current_app


main_bp = Blueprint('main', __name__, template_folder='../templates/main')


@main_bp.route('/')
def home():
    featured_products = Product.query.filter_by(is_available=True).order_by(Product.date_created.desc()).limit(4).all()
    testimonials = Testimonial.query.filter_by(product_id=None).order_by(Testimonial.date.desc()).limit(6).all()
    featured_project = Project.query.order_by(Project.date_created.desc()).first()
    return render_template('main/home.html', featured_products=featured_products, testimonials=testimonials, featured_project=featured_project)


@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')


@main_bp.route('/portfolio')
def portfolio():
    projects = Project.query.order_by(Project.date_created.desc()).all()
    return render_template('main/portfolio.html', projects=projects)

@main_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Product, Category, QuoteRequest, ContactMessage
from app.extensions import db
import os
from werkzeug.utils import secure_filename
from app.models import Product, Category, QuoteRequest, ContactMessage, GalleryImage, Project
from app.models import Product, Category, QuoteRequest, ContactMessage, GalleryImage, Project, ProductImage

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
GALLERY_CATEGORIES = ['Bedrooms', 'Living Rooms', 'Dining Rooms', 'Offices', 'Commercial Spaces']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file):
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        from flask import current_app
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Avoid overwriting existing files with the same name
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(upload_path):
            filename = f"{base}_{counter}{ext}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            counter += 1

        file.save(upload_path)
        return f"/static/uploads/{filename}"
    return None


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_products': Product.query.count(),
        'total_categories': Category.query.count(),
        'total_projects': Project.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)
@admin_bp.route('/products')
@login_required
def manage_products():
    products = Product.query.order_by(Product.date_created.desc()).all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()

    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            material=request.form.get('material'),
            dimensions=request.form.get('dimensions'),
            size_label=request.form.get('size_label'),
            colours=request.form.get('colours'),
            price=request.form.get('price', type=float),
            is_available='is_available' in request.form,
            category_id=request.form.get('category_id', type=int)
        )

        image_file = request.files.get('featured_image')
        image_url = save_uploaded_image(image_file)
        if image_url:
            product.featured_image = image_url

        db.session.add(product)
        db.session.commit()
        flash('Product added successfully.', 'success')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/product_form.html', categories=categories, product=None)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.material = request.form.get('material')
        product.dimensions = request.form.get('dimensions')
        product.size_label = request.form.get('size_label')
        product.colours = request.form.get('colours')
        product.price = request.form.get('price', type=float)
        product.is_available = 'is_available' in request.form
        product.category_id = request.form.get('category_id', type=int)

        image_file = request.files.get('featured_image')
        image_url = save_uploaded_image(image_file)
        if image_url:
            product.featured_image = image_url

        db.session.commit()

        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin/product_form.html', categories=categories, product=product)


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/categories')
@login_required
def manage_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name', '').strip()
    if name:
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('That category already exists.', 'error')
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Category added.', 'success')
    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    if category.products:
        flash(f'Cannot delete "{category.name}" — it still has {len(category.products)} product(s) assigned.', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted.', 'success')

    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/quotes')
@login_required
def manage_quotes():
    quotes = QuoteRequest.query.order_by(QuoteRequest.date_submitted.desc()).all()
    return render_template('admin/quotes.html', quotes=quotes)


@admin_bp.route('/quotes/<int:quote_id>/status', methods=['POST'])
@login_required
def update_quote_status(quote_id):
    quote = QuoteRequest.query.get_or_404(quote_id)
    new_status = request.form.get('status')

    if new_status in ['pending', 'contacted', 'closed']:
        quote.status = new_status
        db.session.commit()
        flash('Quote status updated.', 'success')

    return redirect(url_for('admin.manage_quotes'))

@admin_bp.route('/messages')
@login_required
def manage_messages():
    messages = ContactMessage.query.order_by(ContactMessage.date.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/gallery')
@login_required
def manage_gallery():
    images = GalleryImage.query.order_by(GalleryImage.date_uploaded.desc()).all()
    return render_template('admin/gallery.html', images=images, categories=GALLERY_CATEGORIES)


@admin_bp.route('/gallery/add', methods=['POST'])
@login_required
def add_gallery_image():
    category = request.form.get('category')
    caption = request.form.get('caption')
    image_file = request.files.get('image')
    image_url = save_uploaded_image(image_file)

    if image_url and category in GALLERY_CATEGORIES:
        gallery_image = GalleryImage(image_url=image_url, category=category, caption=caption)
        db.session.add(gallery_image)
        db.session.commit()
        flash('Image added to gallery.', 'success')
    else:
        flash('Please select a valid category and image.', 'error')

    return redirect(url_for('admin.manage_gallery'))


@admin_bp.route('/gallery/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_gallery_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Image removed.', 'success')
    return redirect(url_for('admin.manage_gallery'))

@admin_bp.route('/portfolio')
@login_required
def manage_portfolio():
    projects = Project.query.order_by(Project.date_created.desc()).all()
    return render_template('admin/portfolio.html', projects=projects)


@admin_bp.route('/portfolio/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        before_url = save_uploaded_image(request.files.get('before_image'))
        after_url = save_uploaded_image(request.files.get('after_image'))

        completion_date_str = request.form.get('completion_date')
        completion_date = None
        if completion_date_str:
            from datetime import datetime as dt
            completion_date = dt.strptime(completion_date_str, '%Y-%m-%d').date()

        project = Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            before_image=before_url,
            after_image=after_url,
            completion_date=completion_date
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added.', 'success')
        return redirect(url_for('admin.manage_portfolio'))

    return render_template('admin/project_form.html', project=None)


@admin_bp.route('/portfolio/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')

        before_url = save_uploaded_image(request.files.get('before_image'))
        if before_url:
            project.before_image = before_url

        after_url = save_uploaded_image(request.files.get('after_image'))
        if after_url:
            project.after_image = after_url

        completion_date_str = request.form.get('completion_date')
        if completion_date_str:
            from datetime import datetime as dt
            project.completion_date = dt.strptime(completion_date_str, '%Y-%m-%d').date()

        db.session.commit()
        flash('Project updated.', 'success')
        return redirect(url_for('admin.manage_portfolio'))

    return render_template('admin/project_form.html', project=project)


@admin_bp.route('/portfolio/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.manage_portfolio'))

@admin_bp.route('/products/<int:product_id>/images', methods=['GET', 'POST'])
@login_required
def manage_product_images(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        files = request.files.getlist('images')
        added = 0
        for file in files:
            image_url = save_uploaded_image(file)
            if image_url:
                db.session.add(ProductImage(image_url=image_url, product_id=product.id))
                added += 1
        if added:
            db.session.commit()
            flash(f'{added} image(s) added.', 'success')
        return redirect(url_for('admin.manage_product_images', product_id=product.id))

    return render_template('admin/product_images.html', product=product)


@admin_bp.route('/products/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_product_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id
    db.session.delete(image)
    db.session.commit()
    flash('Image removed.', 'success')
    return redirect(url_for('admin.manage_product_images', product_id=product_id))
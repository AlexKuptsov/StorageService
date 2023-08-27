import datetime
import app
from flask import Blueprint, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField, FloatField, IntegerField, HiddenField
from wtforms.validators import DataRequired, NumberRange

storage = Blueprint('storage', __name__)


class SellForm(FlaskForm):
    product_id = IntegerField('Count', validators=[DataRequired(), NumberRange(min=1)])
    count = IntegerField('Count', validators=[DataRequired(), NumberRange(min=1)])
    comment = StringField('Comment')
    summ = FloatField('Summ', validators=[DataRequired()])
    additional_expanses = FloatField('Additional Expenses', default=0.0)


class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    count = IntegerField('Count', validators=[DataRequired()])


@storage.route('/storage')
def storage_list():
    products_list = app.Product.query.filter(app.Product.count != 0).all()
    return render_template('storage.html',
                           product_list=products_list)


@storage.route('/products/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        new_product = app.Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            count=form.count.data
        )
        app.db.session.add(new_product)
        app.db.session.commit()

        # Create a new Buy object
        new_buy = app.Buy(
            product=new_product.id,
            user=current_user.id,
            data=datetime.datetime.utcnow()
        )
        app.db.session.add(new_buy)
        app.db.session.commit()

        return redirect(url_for('storage.storage_list'))
    return render_template('add_product.html', form=form)


@storage.route('/add_sell', methods=['GET', 'POST'])
def add_sell():
    product_id = request.args.get('product_id')
    product = app.Product.query.get(product_id)

    form = SellForm(product_id=product_id)  # Pass product_id to pre-fill the form

    if form.validate_on_submit():
        new_sell = app.Sell(
            product=form.product_id.data,
            comment=form.comment.data,
            user=current_user.id,
            count=form.count.data,
            summ=form.summ.data,
            additional_expanses=form.additional_expanses.data,
            data=datetime.datetime.utcnow()
        )
        app.db.session.add(new_sell)
        app.db.session.commit()

        product = app.Product.query.get(new_sell.product)
        # calculate margin
        buying_summ = product.price * new_sell.count
        new_sell.margin = new_sell.summ - new_sell.additional_expanses - buying_summ
        app.db.session.add(new_sell)
        app.db.session.commit()

        # update product count
        product.count = product.count - new_sell.count
        app.db.session.add(product)
        app.db.session.commit()

        return redirect(url_for('storage.storage_list'))  # Redirect to your product list page

    return render_template('add_sell.html', form=form, product=product)


@storage.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    product_id = request.args.get('product_id')
    product = app.Product.query.get(product_id)

    if product:
        app.db.session.delete(product)
        app.db.session.commit()

    return redirect(url_for('storage.storage_list'))
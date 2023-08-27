import app
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/statistics', methods=['GET'])
@login_required
def statistics():

    filter_month = request.args.get('filter_month')

    if filter_month:
        # If a specific month is filtered, calculate total sell sum for that month
        # Assuming that 'data' field in Sell model is the date of the sell
        total_sell_sum = app.db.session.query(app.db.func.sum(app.Sell.summ)).filter(
            app.Sell.user == current_user.id,
            app.db.extract('month', app.Sell.data) == filter_month.split("-")[-1]).scalar()
        # Calculate total sell margin
        total_sell_margin = app.db.session.query(app.db.func.sum(app.Sell.margin)).filter(
            app.Sell.user == current_user.id,
            app.db.extract('month', app.Sell.data) == filter_month.split("-")[-1]).scalar()
        # calculate total count of sell objects
        total_sell_number = app.Sell.query.filter(
            app.Sell.user == current_user.id,
            app.db.extract('month', app.Sell.data) == filter_month.split("-")[-1]).count()
        # get Sell records list
        sell_list = app.Sell.query.filter(
            app.Sell.user == current_user.id,
            app.db.extract('month', app.Sell.data) == filter_month.split("-")[-1])
        # get Buy records list
        buy_list = app.Buy.query.filter(
            app.Buy.user == current_user.id,
            app.db.extract('month', app.Sell.data) == filter_month.split("-")[-1])
    else:
        # calculate total sell sum for all time
        total_sell_sum = app.db.session.query(
            app.db.func.sum(app.Sell.summ)
        ).filter(
            app.Sell.user == current_user.id
        ).scalar()
        # Calculate total margin of all time
        total_sell_margin = app.db.session.query(
            app.db.func.sum(app.Sell.margin)
        ).filter(
            app.Sell.user == current_user.id
        ).scalar()
        # Calculate total sell number
        total_sell_number = app.Sell.query.filter(
            app.Sell.user == current_user.id
        ).count()
        # get Sell records list
        sell_list = app.Sell.query.filter(
            app.Sell.user == current_user.id
        ).all()
        # get Buy records list
        buy_list = app.Buy.query.filter(
            app.Buy.user == current_user.id
        ).all()

    return render_template('statistics.html', name=current_user.name,
                           total_sell_number=total_sell_number,
                           total_sell_sum=total_sell_sum,
                           total_sell_margin=total_sell_margin,
                           sell_list=sell_list,
                           buy_list=buy_list,
                           filter_month=filter_month)

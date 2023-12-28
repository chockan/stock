from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import requests
import plotly.express as px

# Configure Flask app
def my12():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db = SQLAlchemy(app)

    class Stock(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(200), nullable=False)
        price_data = db.Column(db.String(200), nullable=False)
        date_created = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return '<Ticker %r>' % self.id
    with app.app_context():
        # This line will create tables based on the defined models
        db.create_all()
    # index
    @app.route('/', methods=['POST', 'GET'])
    def index():
        if request.method == 'POST':
            ticker_content = request.form['content']
            price_content = get_stock_price(ticker_content)
            new_ticker = Stock(content=ticker_content, price_data=price_content)

            try:
                db.session.add(new_ticker)
                db.session.commit()
                return redirect('/')
            except:
                return 'There was an issue adding your ticker'

        else:
            tickers = Stock.query.order_by(Stock.date_created).all()
            return render_template('index.html', tickers=tickers)
    # Update
    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    def update(id):
        ticker = Stock.query.get_or_404(id)

        if request.method == 'POST':
            new_ticker_content = request.form['content']
            new_price_data = get_stock_price(new_ticker_content)

            if new_price_data != 'Not Available':
                ticker.content = new_ticker_content
                ticker.price_data = new_price_data

                try:
                    db.session.commit()
                    return redirect('/')
                except:
                    return 'There was an issue updating your task'
            else:
                return 'Unable to fetch price data for the updated ticker'
        else:
            return render_template('my1/update.html', ticker=ticker)


    # Delete
    @app.route('/delete/<int:id>')
    def delete(id):
        ticker_to_delete = Stock.query.get_or_404(id)

        try:
            db.session.delete(ticker_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem deleting that task'

    # Function to get stock price using IEX Cloud API
    def get_stock_price(ticker):
        try:
            api_key = 'pk_926bc85cf8044080acbb9bec704a2749'
            url = f'https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={api_key}'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('latestPrice', 'Not Available')
            else:
                return 'Not Available'
        except requests.RequestException:
            return 'Not Available'

    # ... (Other routes for delete, update, etc.)

    # Charting using Plotly
    @app.route('/chart/<int:id>', methods=['GET', 'POST'])
    def chart(id):
        ticker = Stock.query.get_or_404(id)
        try:
            api_key = 'pk_926bc85cf8044080acbb9bec704a2749'
            # Replace with the actual endpoint to fetch historical stock data from IEX Cloud
            url = f'https://cloud.iexapis.com/stable/stock/{ticker.content}/chart/1y?token={api_key}'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Process the data to prepare for Plotly chart (for example, selecting relevant columns)
                # Let's assume the JSON structure has 'date' and 'close' columns
                processed_data = [{'Date': entry['date'], 'Close': entry['close']} for entry in data]
                
                # Create a Plotly line chart using Plotly Express (px)
                fig = px.line(processed_data, x='Date', y='Close', title=f'{ticker.content} Share Prices')
                fig.show()
                return redirect('/')
            else:
                return 'Unable to fetch historical data for the chart'
        except requests.RequestException:
            return 'Error occurred while fetching data from IEX Cloud'
        
    return app











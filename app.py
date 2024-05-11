from flask import Flask, render_template, request, redirect, url_for, flash
from sec_edgar_downloader import Downloader
import os
from project.llm import get_summary
from project.data_processing import run


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key; ensure this key remains constant across sessions for production

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    It manages the submission of ticker symbols for either downloading or analyzing SEC 10-K filings.
    Based on the user's action, it either downloads the filings or processes and displays a summary.
    """
    summary = None
    if request.method == 'POST':
        ticker = request.form['ticker']
        email = request.form['email']
        action = request.form.get('action', 'download')

        if action == 'download':
            try:
                download_10k_filings(ticker, 1995, 2023, email)
                flash(f'Successfully downloaded 10-K filings for {ticker} from 1995 to 2023.')
            except Exception as e:
                flash(str(e))
        elif action == 'analyze':
            try:
                run(ticker)  # assuming you process and save data first
                print(ticker)
                summary = get_summary()
                #flash(summary)
                print(summary)
            except Exception as e:
                flash(str(e))
    return render_template('index.html', summary=summary)


def download_10k_filings(ticker, start_year, end_year, email):
    """
    Downloads SEC 10-K filings for a given ticker symbol from a specified start year to an end year.
    The filings are saved to a directory within the current working directory.

    Args:
    ticker (str): The ticker symbol of the company whose filings are to be downloaded.
    start_year (int): The beginning year of the filing period.
    end_year (int): The ending year of the filing period.
    email (str): The email address to be used for SEC EDGAR access.
    """

    dl = Downloader(os.path.join(os.getcwd(), "sec_filings"), email)
    for year in range(start_year, end_year + 1):
        dl.get("10-K", ticker, after=f"{year}-01-01", before=f"{year}-12-31")

if __name__ == '__main__':
    app.run(debug=True)

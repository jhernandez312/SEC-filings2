from sec_edgar_downloader import Downloader
import os

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

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol of the company: ")

    email = input("Enter your email address (required for SEC EDGAR access): ")

    start_year = 1995
    current_year = 2023

    # call the function to download filings
    download_10k_filings(ticker, start_year, current_year, email)

    print(f"Completed downloading 10-K filings for {ticker} from {start_year} to {current_year}.")

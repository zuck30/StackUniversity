# StackUniversity

## Overview

StackUniversity is a Streamlit-based web application designed to help students explore, compare, and discover universities and colleges in Tanzania. It scrapes data from the Tanzania Commission for Universities (TCU) website, stores it in a SQLite database, and provides an interactive interface for filtering universities, comparing their features, and viewing detailed information. The app also includes a guided wizard for personalized university recommendations and data insights visualizations using ECharts.

## Features

- **University Exploration**: Browse a list of Tanzanian universities with filters for region, type, fees, and program search.
- **Comparison Tool**: Compare up to 4 universities side-by-side based on key features like fees, difficulty, and programs.
- **Guided Wizard**: Answer questions to receive personalized university recommendations based on preferences.
- **Data Scraping**: Fetch real-time university data from the TCU website, with fallback to sample data.
- **Insights Dashboard**: Visualize university distributions by region, type, and difficulty using interactive charts.
- **Responsive Design**: Clean, modern UI with custom CSS for a polished user experience.

## Technologies Used

- **Python 3.8+**
- **Streamlit**: For the web application framework.
- **Pandas**: For data manipulation.
- **SQLite3**: For local database storage.
- **Requests & BeautifulSoup**: For web scraping.
- **Streamlit-ECharts**: For interactive visualizations.
- **CSS**: For custom styling.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Steps

1. **Clone the Repository** (or download the source code):
   ```bash
   git clone https://github.com/your-username/stackuniversity.git
   cd stackuniversity
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install streamlit pandas sqlite3 requests beautifulsoup4 streamlit-echarts
   ```

4. **Delete Existing Database** (if any):
   - Remove the `universities.db` file in the project directory to ensure a fresh database schema.

## Usage

1. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   - The app will open in your default web browser at `http://localhost:8501`.

2. **Navigate the App**:
   - **Home Page**: Choose to explore all universities or start the guided wizard.
   - **Explore Universities**: Filter universities by region, type, fees, or search for programs. Use "View Details" to see more info or "Add to Compare" to include in comparisons.
   - **Compare Tab**: View selected universities side-by-side.
   - **Data Insights**: Explore visualizations of university data.
   - **Update Data**: Click "Update Data" to scrape the latest university list from the TCU website.

3. **Notes**:
   - The scraper fetches basic university data (name, region, type) from the TCU website. Detailed program and admission data uses placeholders unless enhanced.
   - If scraping fails, the app falls back to a sample dataset of 15 universities.
   - Ensure an active internet connection for scraping to work.

## Project Structure

```
stackuniversity/
├── app.py              # Main Streamlit application
├── universities.db     # SQLite database (generated on first run)
├── README.md           # Project documentation
└── venv/               # Virtual environment (if created)
```

## Database Schema

The `universities` table in `universities.db` has the following columns:

- `id` (INTEGER, PRIMARY KEY): Unique identifier.
- `name` (TEXT): University name.
- `acronym` (TEXT): University acronym.
- `region` (TEXT): Region of operation.
- `type` (TEXT): Public or Private.
- `avg_fees` (INTEGER): Average annual fees in TZS.
- `difficulty` (TEXT): Admission difficulty (Low, Medium, High, Very High).
- `location` (TEXT): Specific location.
- `description` (TEXT): Brief description.
- `facilities` (TEXT): JSON-encoded list of facilities.
- `programs` (TEXT): JSON-encoded list of programs.
- `admission_requirements` (TEXT): Admission criteria.

## Troubleshooting

- **Buttons Not Working**:
  - Clear browser cache or try a different browser.
  - Ensure Streamlit is up-to-date: `pip install --upgrade streamlit`.
  - Check the terminal for error messages.

- **Few Universities Displayed**:
  - Click "Update Data" to scrape from TCU.
  - If scraping fails, check internet connectivity or TCU website availability.
  - Reset filters in the "Explore" tab to ensure they aren’t too restrictive.

- **Scraping Errors**:
  - The TCU website may have changed its structure. Update the `scrape_university_data()` function in `app.py`.
  - Increase the `time.sleep` delay in the scraper if blocked by the server.

## Future Improvements

- Enhance the scraper to fetch detailed program and admission data from university subpages.
- Implement automatic pagination detection for the TCU website.
- Add export functionality for comparison data (e.g., CSV, PDF).
- Introduce user authentication for saving preferences.
- Expand the sample dataset with more universities and realistic program details.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit: `git commit -m "Add your feature"`.
4. Push to your branch: `git push origin feature/your-feature`.
5. Open a pull request with a description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, contact [your-email@example.com](mailto:your-email@example.com) or open an issue on the GitHub repository.
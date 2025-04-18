# Customer Analytics Dashboard

A multi-page Streamlit application that visualizes customer sentiment, support operations, and product-review insights by querying Snowflake directly.

## Features

- **Sentiment & Experience**: Track customer sentiment trends and distribution
- **Support Operations**: Monitor ticket volumes and resolution metrics
- **Product Feedback**: Analyze product reviews and ratings
- **Customer Journey**: Visualize customer interaction patterns
- **Segmentation & Value**: Identify customer segments and value metrics
- **Insights & Summaries**: Access key insights and data summaries

## Prerequisites

- Python 3.11 or higher
- Snowflake account with appropriate access
- Node.js 20 LTS (for development tooling)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd customer-analytics-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Snowflake credentials:
```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Snowflake credentials
```

## Configuration

Create a `.streamlit/secrets.toml` file with your Snowflake credentials:

```toml
[snowflake]
user = "your_username"
password = "your_password"
account = "your_account"
warehouse = "CX_WH"
database = "ANALYTICS"
schema = "PUBLIC"
role = "CUSTOMER_ANALYTICS_APP"
```

## Running the Application

Start the Streamlit development server:
```bash
streamlit run app.py
```

The application will be available at http://localhost:8501

## Development

### Project Structure

```
customer-analytics-dashboard/
├── app.py                  # Main application entry point
├── pages/                  # Streamlit page modules
│   ├── sentiment.py        # Sentiment analysis page
│   ├── support.py          # Support operations page
│   ├── reviews.py          # Product feedback page
│   ├── journey.py          # Customer journey page
│   ├── segments.py         # Segmentation page
│   └── insights.py         # Insights page
├── src/                    # Source code modules
│   ├── data/              # Data access and processing
│   ├── ui/                # UI components and themes
│   └── utils/             # Utility functions
├── tests/                  # Test suite
├── .streamlit/            # Streamlit configuration
└── requirements.txt       # Python dependencies
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Document all functions with docstrings
- Run `black` and `isort` before committing

### Testing

Run the test suite:
```bash
pytest
```

## Deployment

The application can be deployed to:
- Streamlit Cloud
- Streamlit in Snowflake
- Self-hosted environment

### Streamlit Cloud Deployment

1. Push your code to a GitHub repository
2. Connect the repository to Streamlit Cloud
3. Configure environment variables in Streamlit Cloud
4. Deploy the application

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or create an issue in the repository. 
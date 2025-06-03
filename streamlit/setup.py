from setuptools import setup, find_packages

setup(
    name="customer_analytics",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.33",
        "snowflake-connector-python",
        "pandas",
        "numpy",
        "plotly>=5",
        "altair>=5",
        "seaborn",
        "streamlit-extras"
    ],
) 
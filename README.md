# Banking Analytics Workbench (BAW)

A comprehensive, end-to-end **local** retail banking analytics platform built with modern data stack technologies. This project demonstrates a complete banking analytics pipeline from data generation through machine learning insights, all running locally on synthetic data.

## 🖼️ Dashboard Screenshots

### 🎯 **Main Dashboard Overview**
![Dashboard Overview](screenshots/01-dashboard.png)
*Comprehensive overview of the Banking Analytics Workbench with enhanced KPI cards and modern glass-morphism design*

### 📊 **Key Performance Indicators**
![KPI Cards](screenshots/02-kpi.png)
*Interactive KPI cards with trend indicators, hover effects, and beautiful gradient styling*

### 📈 **Transaction Analytics**
![Transaction Analytics](screenshots/03-transactions.png)
*Multi-panel transaction visualization showing volume trends and transaction counts over time*

### 🏧 **ATM Cash Demand Forecast**
![ATM Forecast](screenshots/04-atm.png)
*3D surface visualization of ATM cash demand forecasting with interactive controls*

### 🕵️ **Fraud Detection & Risk Analysis**
![Fraud Detection](screenshots/05-fraud.png)
*Advanced fraud detection dashboard with risk scoring, alerts, and distribution analysis*

---

## 🚀 Project Overview

BAW is designed to showcase best practices in banking analytics by providing:
- **Synthetic Data Generation**: Realistic banking data for development and testing
- **Modern Data Stack**: DuckDB + dbt + Airflow + Python ML stack
- **End-to-End Pipeline**: From raw data ingestion to ML-powered insights
- **Banking-Specific Analytics**: Fraud detection, churn prediction, ATM demand forecasting
- **Interactive Dashboards**: Streamlit-based visualization and exploration tools

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Data     │    │   DuckDB        │    │   dbt Models    │
│   (CSV Files)  │───▶│   Warehouse     │───▶│   (Staging,     │
│                 │    │                 │    │    Marts)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ML Models    │    │   Airflow       │    │   Streamlit     │
│   (Fraud,      │◀───│   DAGs          │◀───│   Dashboard     │
│    Churn,      │    │                 │    │                 │
│    ATM)        │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

## 📊 Data Models

### Source Tables
- **accounts.csv**: Customer account information
- **customers.csv**: Customer demographics and profiles
- **transactions.csv**: Financial transaction records
- **atm_withdrawals.csv**: ATM usage patterns
- **branches.csv**: Branch location and metadata
- **digital_sessions.csv**: Online banking session logs
- **support_tickets.csv**: Customer service interactions

### dbt Model Structure
```
models/
├── staging/           # Raw data cleaning and standardization
│   ├── stg_accounts.sql
│   ├── stg_customers.sql
│   ├── stg_transactions.sql
│   └── stg_branches.sql
├── marts/            # Business-ready data models
│   ├── dims/         # Dimension tables
│   │   ├── dim_customer.sql
│   │   ├── dim_account.sql
│   │   └── dim_branch.sql
│   └── facts/        # Fact tables
│       ├── fact_transactions.sql
│       ├── fact_sessions.sql
│       └── fact_atm_demand.sql
└── sources.yml       # Source definitions and metadata
```

## 🤖 Machine Learning Capabilities

### Fraud Detection
- **Model**: Isolation Forest for anomaly detection
- **Features**: Transaction patterns, amount distributions, time-based anomalies
- **Output**: Fraud risk scores and flagged transactions

### Customer Churn Prediction
- **Model**: Baseline classification models
- **Features**: Account activity, transaction frequency, support interactions
- **Output**: Churn probability scores

### ATM Demand Forecasting
- **Model**: Time series forecasting
- **Features**: Historical withdrawal patterns, seasonal trends
- **Output**: Predicted ATM demand by location and time

## 🛠️ Technology Stack

- **Data Storage**: DuckDB (local analytical database)
- **Data Transformation**: dbt (data build tool)
- **Workflow Orchestration**: Apache Airflow
- **Machine Learning**: Python (scikit-learn, pandas, numpy)
- **Data Visualization**: Streamlit
- **Data Quality**: Custom validation scripts
- **Version Control**: Git with dbt snapshots

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Git
- Basic knowledge of SQL and Python

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd rbc-baw

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# $env:DBT_PROFILES_DIR="$PWD/.venv\Scripts\Activate.ps1"

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Set dbt profiles directory
# macOS/Linux:
export DBT_PROFILES_DIR=$(pwd)/.dbt
# Windows PowerShell:
# $env:DBT_PROFILES_DIR="$PWD/.dbt"
```

### 3. Data Pipeline Execution
```bash
# Generate synthetic banking data
python scripts/generate_data.py

# Load data into DuckDB warehouse
python scripts/load_to_duckdb.py

# Run dbt transformations
dbt deps && dbt run && dbt test
```

### 4. Machine Learning Models
```bash
# Run fraud detection
python scripts/fraud_isoforest.py

# Run churn prediction
python scripts/churn_baseline.py

# Run ATM demand forecasting
python scripts/atm_forecast.py
```

### 5. Launch Dashboard
```bash
streamlit run dashboards/app.py
```

## 📁 Project Structure

```
rbc-baw/
├── airflow/                 # Airflow DAGs for workflow orchestration
│   └── dags/
│       └── baw_pipeline.py
├── dashboards/             # Streamlit dashboard application
│   └── app.py
├── data/                   # Data storage
│   ├── raw/               # Source CSV files
│   ├── warehouse/         # DuckDB database files
│   └── outputs/           # Generated outputs and results
├── dbt_packages/          # dbt dependencies
├── models/                 # dbt data models
│   ├── staging/           # Data cleaning and standardization
│   ├── marts/             # Business-ready models
│   └── sources.yml        # Source definitions
├── scripts/                # Python utility scripts
│   ├── generate_data.py   # Synthetic data generation
│   ├── load_to_duckdb.py  # Data loading
│   ├── fraud_isoforest.py # Fraud detection
│   ├── churn_baseline.py  # Churn prediction
│   ├── atm_forecast.py    # ATM demand forecasting
│   └── data_quality.py    # Data validation
├── snapshots/              # dbt snapshots for change tracking
├── target/                 # dbt compilation artifacts
├── dbt_project.yml         # dbt project configuration
├── requirements.txt         # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### dbt Configuration
The project uses a local DuckDB profile configured in `.dbt/profiles.yml`:
```yaml
baw:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: data/warehouse/baw.duckdb
      schema: main
```

### Environment Variables
- `DBT_PROFILES_DIR`: Path to dbt profiles directory
- `PYTHONPATH`: Python path for module imports

## 📊 Data Quality & Testing

### dbt Tests
- **Generic tests**: Unique, not_null, relationships
- **Custom tests**: Business logic validation
- **Data quality checks**: Custom Python scripts for comprehensive validation

### Quality Metrics
- Data completeness
- Data consistency
- Business rule compliance
- Anomaly detection

## 🚀 Advanced Usage

### Custom Data Generation
Modify `scripts/generate_data.py` to:
- Adjust data volumes
- Change data distributions
- Add new data types
- Modify business rules

### Extending dbt Models
Add new models in the appropriate directory:
- `staging/` for new source tables
- `marts/dims/` for new dimensions
- `marts/facts/` for new fact tables

### Adding ML Models
Create new scripts in the `scripts/` directory following the existing pattern:
- Data loading and preprocessing
- Model training and evaluation
- Results storage and visualization

## 🐛 Troubleshooting

### Common Issues

**dbt Connection Errors**
- Verify DuckDB database exists
- Check dbt profile configuration
- Ensure correct working directory

**Python Import Errors**
- Verify virtual environment activation
- Check PYTHONPATH configuration
- Install missing dependencies

**Data Quality Issues**
- Review data generation parameters
- Check dbt test results
- Validate source data integrity

### Debug Mode
Enable verbose logging in dbt:
```bash
dbt run --verbose
dbt test --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern data stack technologies
- Inspired by real-world banking analytics challenges
- Designed for educational and development purposes

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Review dbt and DuckDB documentation
- Open an issue in the repository

---

**Happy Banking Analytics! 🏦📊**

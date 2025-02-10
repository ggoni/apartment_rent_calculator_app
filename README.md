# Apartment Rent Calculator

## Overview

The Apartment Rent Calculator is a project that provides an API for calculating apartment rent based on various parameters. Additionally, it features a Streamlit app that allows users to interactively input data and receive rent calculations in real-time.

## Features

- **API**: A robust API that handles requests for rent calculations based on user-defined criteria.
- **Streamlit App**: A user-friendly web application built with Streamlit, enabling users to easily input their apartment details and view the calculated rent.

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd apartment-rent-calculator
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the API

To start the API, run the following command:
```bash
python api/main.py
```
This will launch the API on `http://localhost:5000`.

### Using the API

The API provides a `POST` endpoint for calculating rent. Here's how to use it:

1. **Endpoint**: `http://localhost:5000/calculate-rent`
2. **Method**: `POST`
3. **Request Body**: The request should be in JSON format. Here's an example of the expected input:
   ```json
   {
       "bedrooms": 2,
       "bathrooms": 1,
       "location": "Downtown",
       "square_feet": 800
   }
   ```

4. **Example cURL Command**:
   You can use the following cURL command to test the API:
   ```bash
   curl -X POST http://localhost:5000/calculate-rent \
   -H "Content-Type: application/json" \
   -d '{"bedrooms": 2, "bathrooms": 1, "location": "Downtown", "square_feet": 800}'
   ```

5. **Response**: The API will return a JSON response with the calculated rent. An example response might look like this:
   ```json
   {
       "estimated_rent": 1500
   }
   ```

### Running the Streamlit App

To start the Streamlit app, use the following command:
```bash
streamlit run app/app.py
```
This will open the Streamlit app in your default web browser.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
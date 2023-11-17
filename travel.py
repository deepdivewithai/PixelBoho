import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

def data_process_in(file_path):
    try:
        data = pd.read_csv(file_path)
        data = data.dropna(axis=1, how="all")        
        desired_country_code = input("Enter the country code you want to analyze and get a report: ")
        
        row_data, input_code, code_exists, column_name = country_code(desired_country_code, data)
        
        if code_exists:
            print(f"The country code '{desired_country_code}' exists in the data.")
            print(f"It is located in the column '{column_name}'.")
            print(f"The data for this country is: {row_data}")
        else:
            print(f"The country code '{desired_country_code}' does not exist in the data.")
        return data
    except FileNotFoundError:
        print("Error: File not found. Please check the file path and try again.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty. Please provide a valid CSV file.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

def country_code(cuncode, data):
    try:
        for column in data.columns:
            if cuncode in data[column].tolist():
                column_name = column
                code_exists = True
                break
        else:
            code_exists = False
            column_name = None
        
        if code_exists:
            row_data = data.loc[data[column_name] == cuncode].values.tolist()[0]
        else:
            row_data = None
        
        return row_data, cuncode, code_exists, column_name
    except Exception as e:
        print(f"An unexpected error occurred in country_code function: {str(e)}")
        return None, None, None, None

def calculate_growth_rate(data, method='median'):

    # Calculate the growth rate for each country
    growth_rates = data.loc[:, '1995':'2020'].pct_change(axis=1)

    # Handle missing values by filling them with 0
    growth_rates = growth_rates.fillna(0)

    # Aggregate growth rates based on the specified method
    if method == 'median':
        data['Growth_Rate'] = growth_rates.median(axis=1)
    elif method == 'mean':
        data['Growth_Rate'] = growth_rates.mean(axis=1)
    elif method == 'std':
        data['Growth_Rate'] = growth_rates.std(axis=1)
    else:
        raise ValueError("Invalid method. Use 'median', 'mean', or 'std'.")

    # Calculate additional statistics
    data['Mean_Growth_Rate'] = growth_rates.mean(axis=1)
    data['Std_Growth_Rate'] = growth_rates.std(axis=1)

    generate_growth_report(data)

    return data

def generate_growth_report(data, start_year="1995", end_year="2020"):
    # Calculate growth rate for the specified range of years
    data['Growth_Rate'] = data.loc[:, start_year:end_year].pct_change(axis=1).median(axis=1)

    # Sort the DataFrame by growth rate
    data_sorted = data.sort_values('Growth_Rate', ascending=False)
    top_10_countries = data_sorted.head(10)

    # Create a bar plot for the top 10 countries with the highest growth rates
    plt.figure(figsize=(12, 8))
    colors = sns.color_palette("viridis", len(top_10_countries))
    sns.barplot(x='Country Name', y='Growth_Rate', data=top_10_countries, palette=colors)
    plt.xlabel('Country')
    plt.ylabel('Growth Rate (%)')
    plt.title(f'Top 10 Countries with Highest Growth in International Tourist Arrivals ({start_year}-{end_year})')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def compare_events_impact(data):
    
    economic_crisis_years = [2008]  # Economic crisis in 2008
    pandemic_years = [2003, 2009, 2019]

    # Convert relevant columns to numeric
    travel_numeric = data.loc[:, '1995':].apply(pd.to_numeric, errors='coerce')

    # Calculate average tourist arrivals before and after economic crises
    average_before_economic_crisis = travel_numeric.loc[:, :'{}'.format(economic_crisis_years[0]-1)].mean(axis=1)
    average_after_economic_crisis = travel_numeric.loc[:, '{}'.format(economic_crisis_years[0]):].mean(axis=1)

    # Calculate average tourist arrivals before and after pandemics
    average_before_pandemic = travel_numeric.loc[:, :'{}'.format(pandemic_years[-1]-1)].mean(axis=1)
    average_after_pandemic = travel_numeric.loc[:, '{}:'.format(pandemic_years[-1]):].mean(axis=1)  # Fixed the indexing here

    # Create a DataFrame for comparative analysis
    comparative_analysis = pd.DataFrame({
        'Country_Name': data['Country Name'],
        'Average Before Economic Crisis': average_before_economic_crisis,
        'Average After Economic Crisis': average_after_economic_crisis,
        'Average Before Pandemic': average_before_pandemic,
        'Average After Pandemic': average_after_pandemic
    })

    plot_comparative_analysis(comparative_analysis)

    return comparative_analysis


def plot_comparative_analysis(comparative_data):

    sns.set(style="whitegrid")

    plot_data = pd.DataFrame({
        'Event': ['Economic Crisis', 'Pandemic'],
        'Average Before': [
            comparative_data['Average Before Economic Crisis'].mean(),
            comparative_data['Average Before Pandemic'].mean()
        ],
        'Average After': [
            comparative_data['Average After Economic Crisis'].mean(),
            comparative_data['Average After Pandemic'].mean()
        ]
    })

    plot_data_melted = pd.melt(plot_data, id_vars='Event', var_name='Period', value_name='Average Tourist Arrivals')

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Event', y='Average Tourist Arrivals', hue='Period', data=plot_data_melted, palette="viridis")
    plt.title('Average Tourist Arrivals Before and After Global Events')
    plt.show()

def top_revenue_countries(data, year='2020', top_n=10):
    # Sort the DataFrame by revenue in the specified year
    top_countries = data.sort_values(by=year, ascending=False).head(top_n)[["Country Name", year]]
    countryList = top_countries["Country Name"].values
    print(f"Task 1: Top 10 best Performing Countries in year {year}: ",countryList)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Country Name', y=year, data=top_countries, palette='viridis')
    
    # Customize plot appearance
    plt.title(f'Top {top_n} Revenue Generating Countries in {year}', fontsize=16)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Revenue', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.show()

file_path = "clean_travel_data.csv"
processed_data = data_process_in(file_path)

if processed_data is not None:
    calculate_growth_rate(processed_data)
    top_countries_in_year = input("Get the top countries in a year: ")
    top_revenue_countries(processed_data, top_countries_in_year)
    compare_events_impact(processed_data)
    


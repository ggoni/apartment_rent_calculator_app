from faker import Faker
import pandas as pd
import numpy as np

def generate_apartment_data(n_samples=1000):
    fake = Faker()
    
    # Define possible values for categorical features
    floor_materials = ['Hardwood', 'Carpet', 'Tile', 'Laminate', 'Vinyl']
    styles = ['Modern', 'Contemporary', 'Traditional', 'Industrial', 'Minimalist']
    
    data = {
        'rooms': np.random.randint(1, 6, n_samples),
        'bathrooms': np.random.randint(1, 4, n_samples),
        'total_surface': np.random.uniform(30, 200, n_samples),  # in square meters
        'building_age': np.random.randint(0, 50, n_samples),
        'floor_material': np.random.choice(floor_materials, n_samples),
        'style': np.random.choice(styles, n_samples),
        'monthly_rent': []
    }
    
    # Generate monthly rent based on features
    for i in range(n_samples):
        base_rent = 1000
        # Add value for each room
        base_rent += data['rooms'][i] * 300
        # Add value for each bathroom
        base_rent += data['bathrooms'][i] * 200
        # Add value based on surface
        base_rent += data['total_surface'][i] * 10
        # Subtract value for building age
        base_rent -= data['building_age'][i] * 10
        # Add random variation
        base_rent *= np.random.uniform(0.8, 1.2)
        
        data['monthly_rent'].append(max(base_rent, 500))  # Ensure minimum rent
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_apartment_data()
    df.to_csv('apartment_data.csv', index=False)
    print("Dataset generated and saved to apartment_data.csv")
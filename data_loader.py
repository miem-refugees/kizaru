from datasets import load_dataset
import pandas as pd
from typing import Dict, List
import json

def load_kizaru_data() -> Dict:
    """
    Load the kizaru dataset from Hugging Face.
    Returns a dictionary containing the dataset.
    """
    try:
        dataset = load_dataset("huggingartists/kizaru")
        return dataset
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def process_data(dataset: Dict) -> pd.DataFrame:
    """
    Process the dataset into a pandas DataFrame.
    Args:
        dataset: The loaded dataset dictionary
    Returns:
        A pandas DataFrame containing the processed data
    """
    if dataset is None:
        return None
    
    # Convert the dataset to a pandas DataFrame
    df = pd.DataFrame(dataset['train'])
    return df

def save_to_json(data: pd.DataFrame, output_file: str = "kizaru_data.json"):
    """
    Save the processed data to a JSON file.
    Args:
        data: The pandas DataFrame to save
        output_file: The name of the output file
    """
    if data is not None:
        data.to_json(output_file, orient='records', lines=True)
        print(f"Data saved to {output_file}")

def main():
    # Load the dataset
    print("Loading kizaru dataset...")
    dataset = load_kizaru_data()
    
    if dataset:
        # Process the data
        print("Processing data...")
        df = process_data(dataset)
        
        if df is not None:
            # Save the processed data
            print("Saving data...")
            save_to_json(df)
            print("Done!")
            
            # Print some basic statistics
            print("\nDataset Statistics:")
            print(f"Number of entries: {len(df)}")
            print("\nColumns in the dataset:")
            print(df.columns.tolist())
        else:
            print("Failed to process the data.")
    else:
        print("Failed to load the dataset.")

if __name__ == "__main__":
    main() 
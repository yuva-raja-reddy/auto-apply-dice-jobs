import pandas as pd
from collections import Counter
import re

def get_word_count_from_job_titles(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Extract the "Job Title" column
    job_titles = df["Job Title"].dropna().astype(str)

    # Split job titles into words and count occurrences
    word_counts = Counter()
    for title in job_titles:
        words = title.lower().split()  # Convert to lowercase and split into words
        words = [word for word in words if re.search(r"[a-zA-Z]", word)]  # Filter out words without letters
        word_counts.update(words)

    # Convert the counter to a DataFrame for better visualization
    word_count_df = pd.DataFrame(word_counts.items(), columns=["Word", "Count"]).sort_values(by="Count", ascending=False)

    return word_count_df

if __name__ == "__main__":
    file_path = "applied_jobs.xlsx"  # Update the file path as needed
    word_count_df = get_word_count_from_job_titles(file_path)
    print(word_count_df)
    
    # Save filtered word count to a text file
    with open("word_count_results.txt", "w") as file:
        for word, count in word_count_df.itertuples(index=False):
            file.write(f"{word}: {count}\n")

    print("Filtered word count saved to word_count_results.txt")

#****
from fulltime import full_time
import pandas as pd

if __name__ == "__main__":
  df = pd.read_csv('barista_1103.csv')
  new_df = full_time(df)
  new_df.to_csv('final_1103.csv')

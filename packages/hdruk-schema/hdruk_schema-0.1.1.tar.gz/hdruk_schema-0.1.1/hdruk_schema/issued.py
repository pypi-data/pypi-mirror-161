


def check_issued(df, schema_df):
  
    issued = df['summary'].iloc[2]['issued']
    return isinstance(issued, str)


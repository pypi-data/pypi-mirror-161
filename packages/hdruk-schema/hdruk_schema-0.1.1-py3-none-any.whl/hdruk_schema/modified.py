




def check_modified(df, schema_df):
  
    modified = df['summary'].iloc[2]['modified']
    return isinstance(modified, str)


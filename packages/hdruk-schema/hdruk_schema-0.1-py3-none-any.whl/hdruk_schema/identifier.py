


import pandas as pd
import validators


def check_identifier(identifier, schema_df):

  identifier_req_1 = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith('properties.identifier')]]['properties.identifier.anyOf'][0][0]['$ref']
  identifier_req_2 = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith('properties.identifier')]]['properties.identifier.anyOf'][0][1]['$ref']
  identifier_def_1 = identifier_req_1.strip('#/').replace('/','.')
  identifier_def_2 = identifier_req_2.strip('#/').replace('/','.')

  identifier_uuid_pattern = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith(identifier_def_1)]]['definitions.uuidv4.pattern']
  identifier_uuid_type = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith(identifier_def_1)]]['definitions.uuidv4.type']
  identifier_uuid_min_length = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith(identifier_def_1)]]['definitions.uuidv4.minLength'].values[0]
  identifier_uuid_max_length = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith(identifier_def_1)]]['definitions.uuidv4.maxLength'].values[0]
  identifier_url_type = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith(identifier_def_2)]]['definitions.url.type']
  identifier_url_format = schema_df[schema_df.columns[pd.Series(schema_df.columns).str.startswith(identifier_def_2)]]['definitions.url.format']

  return validators.url(identifier)


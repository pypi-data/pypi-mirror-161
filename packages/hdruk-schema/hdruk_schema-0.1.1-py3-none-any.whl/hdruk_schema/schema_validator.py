from .accessibility import check_accessibility
from .documentation import check_documentation
from .identifier import check_identifier
from .revisions import check_revisions
from .summary import check_summary
from .version import check_version
from .issued import check_issued
from .modified import check_modified
from .observations import check_observations
from collections import defaultdict
import pandas as pd
import json
from termcolor import colored



def parse_json_file(metadata_path, data_model_col='dataModels'):

    df_json = pd.read_json(metadata_path)

    data_models = df_json[data_model_col]
    df_list = defaultdict(list)
    nrows = data_models.shape[0]

    for i in range(nrows):
      for k, v in zip(data_models.iloc[i].keys(), data_models.iloc[i].values()):
        df_list[k].append(v)
    
    df = pd.DataFrame.from_dict(dict(df_list.items()), orient='index').T
    
    return df

# df = parse_json_file(metadata_path)

def load_schema(schema_file_path):
    # schema_path = "dataset.schema.json"

    with open(schema_file_path, 'r') as j:
        schema_contents = json.loads(j.read())

    schema_df = pd.json_normalize(schema_contents)

    return schema_df


def validate_property(df, schema_df, col, validator):
        
        print(colored(f'Checking {col} for conformitiy', 'red'))

        result = df[col].apply((lambda x: validator(x, schema_df)))

        print(colored(f"Checking {col} complete", 'green'), colored(u'\u2713', 'green'))

        return result




def schema_validator(metadata_path, schema_file_path):
     df = parse_json_file(metadata_path)
     schema_df = load_schema(schema_file_path)
     checklist = list(df.columns)
     validated_dict = {}

     for col in checklist:
        

        # if col == 'identifier':
        #     result = validate_property(df, schema_df, col, check_identifier)
        #     validated_dict[col] = result


        if col == 'version':
            result = validate_property(df, schema_df, col, check_version)
            validated_dict[col] = result
        
        if col == 'documentation':
            result = validate_property(df, schema_df, col, check_documentation)
            validated_dict[col] = result

        if col == 'accessibility':
            result = validate_property(df, schema_df, col, check_accessibility)
            validated_dict[col] = result        

     return validated_dict






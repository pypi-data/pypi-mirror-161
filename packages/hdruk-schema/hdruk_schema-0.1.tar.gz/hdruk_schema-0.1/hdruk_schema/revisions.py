



import validators









def check_length(property, min_length, max_length):
  if len(property) >= min_length and len(property) <= max_length:
    return True
  return False

def is_in_list(item, list):
  if item in list:
    return True
  return False

def regex_match(pattern, string):
  pattern = re.compile(pattern)
  if re.fullmatch(pattern, string):
    return True
  return False


def validate_revisions(revisions):

  for k,v in revisions.items():

    if k == 'version':
        pattern = r'^([0-9]+)\.([0-9]+)\.([0-9]+)$'
        result = regex_match(pattern, v)

    if k == 'url':
      result = isinstance(v, str) and validators.url(v)


def check_revisions(df, schema_df):
  
  revisions = df['summary'].iloc[2]['revisions']

  validate_revisions(revisions)
      # if isinstance(v, str) and check_length(v, 2, 80):
        # result = True

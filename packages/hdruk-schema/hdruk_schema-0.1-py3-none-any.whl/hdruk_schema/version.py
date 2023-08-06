
import re



def regex_match(pattern, string):
  pattern = re.compile(pattern)
  if re.fullmatch(pattern, string):
    return True
  return False


def check_version(version, schema_df):
  version_pattern = schema_df['definitions.semver.pattern'].values[0]
  is_version = regex_match(version_pattern, version)
  return is_version
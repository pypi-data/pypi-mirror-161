
import re
import validators
from validate_email import validate_email




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


def validate_observations_observedNode(observedNode, schema_df):
    # title_min_length = schema_df['definitions.eightyCharacters.minLength'].iloc[0]
    # title_type = schema_df['definitions.eightyCharacters.type'].iloc[0]
    # title_max_length = schema_df['definitions.eightyCharacters.maxLength'].iloc[0]
    if isinstance(observedNode, str) and check_length(observedNode, 2, 80):
        return True
    return False


  
def validate_observations_measuredValue(df, schema_df): #row
  measuredValue = df['observations'].iloc[0]['measuredValue']
  # title = row['title']
  measuredValue_min_length = schema_df['definitions.measuredValueText.minLength'].iloc[0]
  measuredValue_type = schema_df['definitions.measuredValueText.type'].iloc[0]
  measuredValue_max_length = schema_df['definitions.measuredValueText.maxLength'].iloc[0]
  if isinstance(measuredValue, str) and check_length(measuredValue, measuredValue_min_length, measuredValue_max_length):
    return True
  return False


def validate_observations_disambiguatingDescription(disambiguatingDescription, schema_df):

  for k,v in disambiguatingDescription.items():
    if k in ['identifier', 'logo', 'accessRights']:
      result = validators.url(v)
    if k == 'name':
      result = isinstance(v, str) and check_length(v, 2, 80)
    if k == 'description':
      result = isinstance(v, str) and check_length(v, 2, 3000)
    if k == 'observationDate':
      result = validate_email(v) # validate_email('example@example.com',verify=True)

    if k == 'memberOf':
      memberOfList = schema_df['definitions.memberOf.enum']
      result = is_in_list(v, memberOfList)
    if k == 'deliveryLeadTime':
      deliveryLeadTimeList = schema_df['definitions.deliveryLeadTime.enum']
      result = is_in_list(v, deliveryLeadTimeList)
    if k == 'accessService':
      result = isinstance(v, str) and check_length(v, 2, 5000)

    if k == 'accessRequestCost':
      result = isinstance(v, str) and check_length(v, 2, 1000)

    if k in ['dataUseLimitation', 'dataUseRequirements']:
      pattern = r'([^,]+)'
      result = regex_match(pattern, v)

def validate_observations_measuredProperty(measuredProperty, schema_df):

    # measuredProperty = df['observations'].iloc[2]['measuredProperty']

    if isinstance(measuredProperty, list):
      return True

    if isinstance(measuredProperty, str):
      pattern = r'([^,]+)'
      result = regex_match(pattern, measuredProperty)
      if result:
        return True


# def validate_observations_alternateIdentifiers(alternateIdentifiers, schema_df):

#     # alternateIdentifiers = df['observations'].iloc[2]['alternateIdentifiers']

#     if isinstance(alternateIdentifiers, list):
#       return True

#     if isinstance(alternateIdentifiers, str):
#       pattern = r'([^,]+)'
#       result = regex_match(pattern, alternateIdentifiers)
#       if result:
#         return True


# def validate_observations_doiName(doiName, schema_df):

#     # alternateIdentifiers = df['observations'].iloc[2]['alternateIdentifiers']

#     if isinstance(doiName, str):
#       pattern = r'^10.\d{4,9}/[-._;()/:a-zA-Z0-9]+$'
#       result = regex_match(pattern, doiName)
#       if result:
#         return True



def validate_observations(observations, schema_df):

    for k,v in observations.items():

      if k == 'observedNode':
        observedNode = observations['observedNode']
        observedNodeList = schema_df['definitions.statisticalPopulationConstrained.enum'][0]
        return observedNode in observedNodeList
        # validate_observations_observedNode(observedNode, schema_df)

      if k == 'measuredValue':
        measuredValue = observations['measuredValue']
        return isinstance(disambiguatingDescription, str)
        # df['observations'].iloc[2][0]['measuredValue']

        # validate_observations_measuredValue(measuredValue, schema_df)


    if k == 'disambiguatingDescription':
        disambiguatingDescription = observations['disambiguatingDescription']
        result = isinstance(disambiguatingDescription, str)

    #   validate_observations_disambiguatingDescription(disambiguatingDescription, schema_df)


    if k == 'observationDate':
        observationDate = observations['observationDate']
        result = isinstance(observationDate, str)
        # is_valid = validate_email(observationDate)

    #   validate_observations_observationDate(observationDate)


    if k == 'measuredProperty':
        measuredProperty = observations['measuredProperty']
        measuredPropertyList = schema_df['definitions.observation.properties.measuredProperty.allOf'][0][0]['enum']
        return measuredProperty in measuredPropertyList
        # validate_observations_measuredProperty(measuredProperty, schema_df)










    # if k == 'alternateIdentifiers':
    #   alternateIdentifiers = observations['alternateIdentifiers']

    #   validate_observations_alternateIdentifiers(alternateIdentifiers, schema_df)

    # if k == 'doiName':
    #   doiName = observations['doiName']

    #   validate_observations_doiName(doiName)



    
def check_observations(df, schema_df):

  observations = df['observations'].iloc[2][0]

  validate_observations(observations, schema_df)






# def check_observations_disambiguatingDescription(df, schema_df):

#   disambiguatingDescription = df['observations'].iloc[2]['disambiguatingDescription']

#   validate_disambiguatingDescription(disambiguatingDescription)

      # if isinstance(v, str) and check_length(v, 2, 80):
        # result = True

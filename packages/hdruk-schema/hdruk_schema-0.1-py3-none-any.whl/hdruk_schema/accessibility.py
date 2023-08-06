






from operator import not_
import validators
import re


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




# def save_result(result, k):
#       if result:
#         is_valid[k] = True
#       else:
#         is_valid[k] = False
#   else:
#     is_valid[k] = not_available







def vaildated_accessibility_usage(usage):
  


  print('Checking accessibility usage')

  not_available = 'NA'
  is_valid = {}

  check_list = ['dataUseLimitation', 'dataUseRequirements', 'resourceCreator', 'investigations', 'isReferencedBy']
  keys = list(usage.keys())
  na = set(check_list) - set(keys)

  for i in na:
    is_valid[i] = not_available


  for k,v in usage.items():

      if k == 'dataUseLimitation':
        print('Checking dataUseLimitation')
        print('v list: ', v)
        pattern = r'([^,]+)'

        if isinstance(v, str): 
          result = regex_match(pattern, v)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available


        if isinstance(v, list) and len(v) > 0:
          result = regex_match(pattern, v[0])
        # if isinstance(v, str): 
        #   result = regex_match(pattern, v)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available




      if k == ' dataUseRequirements':
        print('dataUseRequirements')
        pattern = r'([^,]+)'
        if isinstance(v, str): 
          result = regex_match(pattern, v)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available


        if isinstance(v, list):
          result = regex_match(pattern, v[0])
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available



      if k == 'resourceCreator':
        print('resourceCreator')
        if isinstance(v, str):
          result =  check_length(v, 2, 1000)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available



        if isinstance(v, list):
          result =  check_length(v, 2, 1000)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available





      if k == 'investigations':
        print('investigations')
        print('v: ', v)
        pattern = r'([^,]+)'
        if isinstance(v, str): 
          result = regex_match(pattern, v)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available

        if isinstance(v, list):
          result = validators.url(v[0])
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available


      if k == 'isReferencedBy':
        print('isReferencedBy')
        pattern = r'^10.\\d{4,9}/[-._;()/:a-zA-Z0-9]+$'
        if isinstance(v, str): 
          result = regex_match(pattern, v)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available

        if isinstance(v, list):
          result = regex_match(pattern, v[0])
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available
  

  return is_valid





def validate_accessibility_access(access, schema_df):

      print('Checking accessibility access')

      not_available = 'NA'
      is_valid = {}

      check_list = ['accessRights', 'accessService', 'accessRequestCost', 'deliveryLeadTime', 'jurisdiction', 'dataController', 'dataProcessor']
      keys = list(access.keys())
      na = set(check_list) - set(keys)

      for i in na:
        is_valid[i] = not_available

      for k,v in access.items():

        if k == 'accessRights':
          print('Access rights')
          if isinstance(v, str): 
            result =  validators.url(v)
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available


          if isinstance(v, list):
            result =  validators.url(v[0])
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available



        if k == 'accessService':
          print('Checking access service')
          result = isinstance(v, str) and check_length(v, 2, 5000)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available

        if k == 'accessRequestCost':
          print('Access request cost')
          if isinstance(v, str):
            result =  check_length(v, 2, 5000)
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available

          if isinstance(v, list):
            result = validators.url(v[0])
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available



        if k == 'deliveryLeadTime':
          print('deliveryLeadTime')
          deliveryLeadTimeList = schema_df['definitions.deliveryLeadTime.enum']
          result = is_in_list(v, deliveryLeadTimeList)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available


        if k == 'jurisdiction':
          print('jurisdiction')
          print('v: ', v)
          pattern1 = r'([^,]+)'
          pattern2 = r'^[A-Z]{2}(-[A-Z]{2,3})?$'
          result = regex_match(pattern1, v[0]) #or regex_match(pattern2, v)
          print('result:', result)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available

        if k in ['dataController', 'dataProcessor']:
          print('dataController')
          result = isinstance(v, str) and check_length(v, 2, 5000)
          if result:
            is_valid[k] = True
          else:
            is_valid[k] = False
        else:
          is_valid[k] = not_available

      return is_valid



def validate_accessibility_formatStandards(formatAndStandards, schema_df):

      print('Checking accessibility formatStandards')
      not_available = 'NA'
      is_valid = {}

      check_list = ['vocabularyEncodingScheme', 'conformsTo', 'language', 'format']
      keys = list(formatAndStandards.keys())
      na = set(check_list) - set(keys)

      for i in na:
        is_valid[i] = not_available


      for k,v in formatAndStandards.items():

        print('k: ', k)
        print('v: ', v)
        if k == 'vocabularyEncodingScheme':
          print('key: vocabularyEncodingScheme')
          if isinstance(v, str): 
            pattern = r'([^,]+)'
            result = regex_match(pattern, v)   
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available

          if isinstance(v, list):
            print('checking list vocabularyEncodingSchemeList')
            vocabularyEncodingSchemeList = schema_df['definitions.controlledVocabulary.enum'].values[0]
            # print('list: ', vocabularyEncodingSchemeList.values)
            result = set(v) <= set(vocabularyEncodingSchemeList)
            # result =  v in vocabularyEncodingSchemeList
            print('here')
            print('result: ', result)

            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available


        if k == 'conformsTo':
          if isinstance(v, str): 
            pattern = r'([^,]+)'
            result = regex_match(pattern, v)  
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available

          # if isinstance(v, list):
          #   standardisedDataModelsList = schema_df['definitions.standardisedDataModels.enum']
          #   result =  v in standardisedDataModelsList
          #   if result:
          #     is_valid[k] = True
          #   else:
          #     is_valid[k] = False
          # else:
          #   is_valid[k] = not_available




        if k == 'language':
          if isinstance(v, str): 
            pattern = r'([^,]+)'
            result = regex_match(pattern, v)  
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available

          # if isinstance(v, list):
          #   languageList = schema_df['definitions.language.enum']
          #   result =  v in languageList
          #   if result:
          #     is_valid[k] = True
          #   else:
          #     is_valid[k] = False
          # else:
          #   is_valid[k] = not_available


        if k == 'format':
          if isinstance(v, str) and len(v) > 1: 
            pattern = r'([^,]+)'
            result = regex_match(pattern, v)  
            if result:
              is_valid[k] = True
            else:
              is_valid[k] = False
          else:
            is_valid[k] = not_available


      return is_valid      




def validate_accessibility(accessibility, schema_df):

    is_valid = {}
    not_available = 'NA'
    check_list = ['access', 'usage', 'formatAndStandards']
    keys = list(accessibility.keys())
    na = set(check_list) - set(keys)

    for i in na:
      is_valid[i] = not_available


    for k,v in accessibility.items():

      if k == 'usage':
        usage = accessibility['usage']
        result = vaildated_accessibility_usage(usage)
        is_valid[k] = result


      if k == 'access':
        access = accessibility['access']
        result = validate_accessibility_access(access, schema_df)
        is_valid[k] = result


      if k == 'formatAndStandards':
        formatAndStandards = accessibility['formatAndStandards']

        result = validate_accessibility_formatStandards(formatAndStandards, schema_df)
        is_valid[k] = result
  
    return is_valid



    
def check_accessibility(accessibility, schema_df):

  is_valid = validate_accessibility(accessibility, schema_df)

  return is_valid



# def check_summary_publisher(df, schema_df):

#   publisher = df['summary'].iloc[2]['publisher']

#   validate_publisher(publisher)

      # if isinstance(v, str) and check_length(v, 2, 80):
        # result = True

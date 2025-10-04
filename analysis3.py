import json
import config
import pandas as pd
import utils

def attribute_dataset(dataset , keylist, nameList) ->  pd.DataFrame:
   """
   return dataframe with fields
   keylist (URL/SourceRepository/Version/YearPublished/) + gender fields.
   Where 
      sum(Female/Male/Ambiguous) = 1 for datasets with persons, 
      OrganizationOnly=1 for datasets with org and no persons.
   That is, the organizations in datasets with persons as PI are ignored.
   """
   nPerson = len(dataset["FirstNames"])
   nOrg = len(dataset["Organizations"])
   
   # get ratios for the persons
   # need to replace None with 0 for names that were missing in Förnammn
      
   if nPerson > 0: 
      FirstNames = [0 if n is None else n for n in dataset['FirstNames']]
      df = nameList.loc[FirstNames]
      nameData = df.sum()
      nameData['OrganizationOnly'] = 0.0
   else:
      nameData = nameList.iloc[0].copy() # copy random row
      nameData.femaleFraction   = 0.0
      nameData.maleFraction     = 0.0
      nameData.ambiguousness    = 0.0
      nameData.attributableFemale = 0.0
      nameData.attributableMale   = 0.0
      nameData.usuallyMale        = 0.0
      nameData.usuallyFemale       = 0.0
      nameData['OrganizationOnly'] = 1.0

   
   # extract keylist from dataset
   d2 = {key: dataset[key] for key in keylist}   
   # put together with nameData in a new DataFrame!
   return( pd.concat([pd.DataFrame.from_records([d2]),  
                      pd.DataFrame.from_records([nameData])  ],axis=1) )

def aggregate_data( ):
  # load SND data
  snd_data = utils.jsonl_load(config.SND_DATA_FILENAME)

  # create a template for output
  dataset = snd_data[0] 
  keylist = list(dataset.keys())
  keylist.remove('Persons')
  keylist.remove('Organizations')
  keylist.remove('FirstNames')

  # load gender ratio data
  nameList = pd.read_csv(config.GENDER_JSON)
  nameList.set_index('name',inplace=True)
  nameList.drop(columns=["popularity"], axis=1, inplace=True)
  # add a row for null
  nullRow = nameList.iloc[0].copy() 
  nullRow.name = None
  nullRow.popularity= None
  nullRow.femaleFraction   = 0.5
  nullRow.maleFraction     = 0.5
  nullRow.ambiguousness    = 1.0
  nullRow.attributableFemale = 0.0
  nullRow.attributableMale   = 0.0
  nullRow.usuallyMale        = 0.5
  nullRow.usuallyFemale       = 0.5
  nameList  = nameList._append([nullRow])

  return([attribute_dataset(d,keylist,nameList) for d in snd_data])

def write_tables(AggregatedData):
  # Export data per dataset
  TableA = pd.concat(AggregatedData, sort=False)
  TableA = TableA.reset_index(drop=True) 
  TableA.to_csv(config.TABLES/'Table3a.csv', index=False, float_format='%.3f') 

  # Yearly per dataset statistics
  TableB = TableA.groupby('YearPublished').sum()
  TableB = TableB[['Female','Male','Ambiguous',"OrganizationOnly"]]
  # ...add Female and Male percentage
  df_ratio = TableB[['Female','Male','Ambiguous']].div(TableB['Female']+ TableB['Male']+ TableB['Ambiguous'], axis=0)
  df_ratio.rename(columns={'Female': 'Percent Female'}, inplace=True)
  df_ratio.rename(columns={'Male': 'Percent Male'}, inplace=True)
  df_ratio.rename(columns={'Ambiguous': 'Percent Ambiguous'}, inplace=True)
  df_ratio = df_ratio*100
  #df_ratio.insert(loc=0,column='YearPublished',value=TableB['YearPublished'])
  #df_ratio.set_index('YearPublished', inplace=True)
  TableB= pd.concat([TableB,df_ratio], axis=1)
  TableB.to_csv(config.TABLES/'Table3b.csv', index=True, float_format='%.3f')

  # Yearly listed PI name statistics for Usual gender
  TableC = TableA.groupby('YearPublished').sum()
  TableC = TableC[['nUsuallyFemale','nUsuallyMale','nAmbiguous']]
  # ...add 'Percent Usually Female'
  df_UFemalePer = TableC[['nUsuallyFemale','nUsuallyMale','nAmbiguous']].div(TableC['nUsuallyFemale'] + TableC['nUsuallyMale'] + TableC['nAmbiguous'], axis=0)
  df_UFemalePer.rename(columns={'nUsuallyFemale': 'Percent Usually Female'}, inplace=True)
  df_UFemalePer.rename(columns={'nUsuallyMale': 'Percent Usually Male'}, inplace=True)
  df_UFemalePer.rename(columns={'nAmbiguous': 'Percent Ambiguous'}, inplace=True)
  df_UFemalePer = df_UFemalePer*100
  #df_ratio.insert(loc=0,column='YearPublished',value=TableC['YearPublished'])
  #df_ratio.set_index('YearPublished', inplace=True)
  TableC = pd.concat([TableC,df_UFemalePer], axis=1)
  TableC.to_csv(config.TABLES/'Table3c.csv', index=True, float_format='%.3f')

  # Yearly listed PI name statistics for Attributed gender
  # convert from dataset fraction to number names
  TableD = TableA[['Female','Male','Ambiguous']].mul(TableA['nUsuallyFemale']+ TableA['nUsuallyMale']+ TableA['nAmbiguous'], axis=0)
  TableD = pd.concat([TableA[['YearPublished']],TableD], axis=1)
  TableD.set_index('YearPublished',inplace=True)
  TableD = TableD.groupby('YearPublished').sum()
  df_ratio = TableD[['Female','Male','Ambiguous']].div(TableD['Female']+ TableD['Male']+ TableD['Ambiguous'], axis=0)
  df_ratio.rename(columns={'Female': 'Percent Female'}, inplace=True)
  df_ratio.rename(columns={'Male': 'Percent Male'}, inplace=True)
  df_ratio.rename(columns={'Ambiguous': 'Percent Ambiguous'}, inplace=True)
  df_ratio = df_ratio*100
  TableD= pd.concat([TableD,df_ratio], axis=1)
  TableD.to_csv(config.TABLES/'Table3d.csv', index=True, float_format='%.3f')

if __name__ == '__main__':
  AggregatedData = aggregate_data( )
  write_tables(AggregatedData)
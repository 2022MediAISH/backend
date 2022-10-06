import datetime
from xml.etree.ElementInclude import include
import requests
import re
import boto3
import json
#pip install sumy
# Importing the parser and tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# Import the LexRank summarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
#pip install nltk
import nltk
#download only once 
#nltk.download('punkt')
import math
import sys
#multithreading part, no need for extra pip install
from threading import Thread
from queue import Queue
import os, json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from pymongo import MongoClient

###############################################
################## IMPORTANT ##################
###############################################
# MOVE ALL THE WAY DOWN TO CHECK HOW TO CALLL #
###############################################

############### Versions 1.7.2 ################
# fixed population ratio to be able to capture from brief descri
############### Versions 1.7.1 ################
# added biolinkbert code
# fixed errors in drug time
# added version in json
############### Versions 1.6.1 ################
# Edit error case that is caused by extra \" in texts
############### Versions 1.6.0 ################
# Edit bern2 ver resource_control
############### Versions 1.5.3 ################
# fixed error case in calc_date
############### Versions 1.5.2 ################
# fixed format matching to frontend team
############### Versions 1.5.1 ################
# created a directory that is used to save
# created database folder using relative url, where NCT~.json is saved
# fixed error in acm_Entities code where error happen when none returns
# modified washout period
############### Versions 1.5.0 ################
# from using acm from amazon server, changed to the server acm from MedAIPlus
# allowed to create database according to NCT ID, if exist bring, not create
# fixed acm id to secret
############### Versions 1.4.3 ################
# modified aws_drugtime code, catching out error cases
############### Versions 1.4.2 ################
# fixed get_title, json changes depending on search by name or by NCT ID
############### Versions 1.4.1 ################
# changed washout to UppaerCamel
############### Versions 1.4.0 ################
# changed short_design -> title
# changed population_box, removed summary
# removed thread for title(short_design)
# updated washout
# added NCT ID
############### Versions 1.3.3 ################
# fixed error case in population box about key name
############### Versions 1.3.2 ################
# fixed error case in drug time_descri code
# fixed error case in washout code
############### Versions 1.3.1 ################
# fixed error case in population ratio code
# fixed error case in population box code
############### Versions 1.3.0 ################
# changed calling process of boto to allow upload without causing error in calling boto client
# erased word2num library
# updated drug_time_descri.py with precision
# change_to_url code is inserted
# updated dictionary key to UpperCamelCase
############### Versions 1.2.1 ################
# fixed wash_out typo and erase time
# optimized intervention_name
# fixed resource_control request response -> url
# fixed intevention name
############### Versions 1.2.0 ################
# previous 1.1.5 -> 1.2.0
# add multithreading to speed up
# optimized short_design
# optimized calc_date
############### Versions 1.1.4 ################
# fixed error caused in get_population_ratio()
############### Versions 1.1.3 ################
# function request - > request_call
# request_call now returns dictionary
# update in washout
############### Versions 1.1.2 ################
# function request(response) to get result
############### Versions 1.1.1 ################
# optimized population_box

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################

BASE_DIR = Path(__file__).resolve().parent

secret_file = os.path.join(BASE_DIR, 'secrets.json') # secrets.json 파일 위치를 명시

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    """비밀 변수를 가져오거나 명시적 예외를 반환한다."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

accessKey = get_secret("aws_access_key_id")
accessSecretKey = get_secret("aws_secret_access_key")
region = get_secret("region_name")
comprehend = boto3.client('comprehend', aws_access_key_id=accessKey, aws_secret_access_key=accessSecretKey, region_name= region)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def acm_Entities(Text):
    try:
        url1 = 'http://61.77.42.239:8100/asp/get_entitiesv2/?query=' + Text
        response = requests.get(url1)
        a = json.loads(response.content)
        return a
    except:
        b = {'Entities' : ''}
        return b

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def removearticles(text):
    articles = {'A': '','a': '', 'An': '','an':'', 'and':'', 'The': '','the':''}
    rest = [word for word in text.split() if word not in articles]
    return ' '.join(rest)

def get_title(response):
    title = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['BriefTitle']

    if("\"" in title):
        title = re.sub('\"', '', title)
        change_dictionary = "{%s : %s%s%s}" % ('"Title"', '"', title, '"')
    else:
        change_dictionary = "{%s : %s%s%s}" % ('"Title"', '"', title, '"')
    #json_acchange_dictionaryceptable_string = .replace("'", "\"")
    #d = json.loads(json_acceptable_string)
    result_dictionary = json.loads(change_dictionary)
    #print(type(result_dictionary))
    return result_dictionary

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_population_box(response):   

    information = {
        "Condition" : "",
        "Participant" : 0,
        "MinAge" : 0,
        "MaxAge" : "",
        "Gender" : "",
        "HealthyCondition" : "",
    }

    information["Participant"] = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount']
    information['Gender'], information['HealthyCondition']  = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["Gender"], response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["HealthyVolunteers"]

    try:
        information['MinAge'] = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["MinimumAge"]
    except:
        information['MinAge'] = ''
    try:
        information['MaxAge'] = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["MaximumAge"]
    except:
        information['MaxAge'] = ''

    convertString = ''.join([str(item) for item in response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ConditionsModule']['ConditionList']['Condition']])
    information['Condition'] = convertString
    
    dic_information = {'PopulationBox' : information}
    return dic_information

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_calc_date(response):

    #get the api resourse
    start_time_api = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['StatusModule']['StartDateStruct']['StartDate']
    end_time_api = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['StatusModule']['CompletionDateStruct']['CompletionDate']
    #since the text is two 'April 2020" split into two difference
    start_date, end_date = start_time_api.split(), end_time_api.split()

    #change the month->the integer num
    datetime_objecta, datetime_objectb = datetime.datetime.strptime(start_date[0], "%B"), datetime.datetime.strptime(end_date[0], "%B")
    start_month, end_month = datetime_objecta.month, datetime_objectb.month
    #print(start_month)
    #print(end_month)

    for value, item in enumerate(start_date):
        if len(item) > 3:
            convert_start_date = item

    for value, item in enumerate(end_date):
        if len(item) > 3:
            convert_end_date = item

    #calc the time
    require_time = (int(convert_end_date) - int(convert_start_date))*12 + (end_month-start_month)
    #print out the total month
    #print(str(require_time) + " months required to complete")
    return_dictionary = {"CompleteTime" : require_time}
    return return_dictionary

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_drug_time(response):
    protocolsection = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']

    detail_description = ""
    brief_description = ""
    try:
        drug_list = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention']
        arm_name = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']
    except:
        pass
    try:
        detail_description = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['BriefSummary']
    except KeyError:
        pass
    try:
        brief_description = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['DetailedDescription']
    except KeyError:
        pass

    drug = []
    time_label = ['day','days','week','weeks','month','months','year','years']
    time_label2 = ['day','week','month','year']
    amount = ['mg','g ', 'mcg', 'milligram','gm','g/m2','micro-gram','ml']
    eat_way = ['oral','po']
    
    
    #dose는 어떻게 넣을지 생각해 봐야할 듯.
    drug_date = []
    
    left = 0
    right = 0
    d_left = 0
    d_right = 0

    drug_dict = {}

    Arm_group = {}
    InterventionDrug = {'ArmGroupList' : []}


    for arms in arm_name:
        try:
            Arm_group[arms['ArmGroupLabel']] = {'ArmGroupLabel' : '','ArmGroupType' : '', 'ArmGroupDescription' : '', 'InterventionList' : '', 'InterventionDescription' : []}
            Arm_group[arms['ArmGroupLabel']]['ArmGroupLabel'] = arms['ArmGroupLabel']
            Arm_group[arms['ArmGroupLabel']]['ArmGroupType'] = arms['ArmGroupType']
            Arm_group[arms['ArmGroupLabel']]['InterventionList'] = {'ArmGroupInterventionName' : []}
            for value in arms['ArmGroupInterventionList']['ArmGroupInterventionName']:
                if ' plus ' in value.lower():
                    temp = value.lower().replace('drug: ',"").split(' plus ')
                    for value2 in temp:
                        Arm_group[arms['ArmGroupLabel']]['InterventionList']['ArmGroupInterventionName'].append('drug: ' + value2)
                elif ' vs ' in value.lower():
                    temp = value.lower().replace('drug: ',"").split(' vs ')
                    for value2 in temp:
                        Arm_group[arms['ArmGroupLabel']]['InterventionList']['ArmGroupInterventionName'].append('drug: ' + value2)
                elif ' and ' in value.lower():
                    temp = value.lower().replace('drug: ',"").split(' and ')
                    for value2 in temp:
                        Arm_group[arms['ArmGroupLabel']]['InterventionList']['ArmGroupInterventionName'].append('drug: ' + value2)

                else:
                    Arm_group[arms['ArmGroupLabel']]['InterventionList']['ArmGroupInterventionName'].append('drug: ' + value.lower().replace('drug: ',""))

        except KeyError:
            pass

    #print(Arm_group)

    for i in range(len(drug_list)):
        if ' plus ' in drug_list[i]['InterventionName'].lower():

            temp = drug_list[i]['InterventionName'].lower().split(' plus ')

            for data in temp:
                drug.append(data.lower().replace('drug: ', ""))
                drug_dict[data.lower().replace('drug: ', "")] = {'DrugName' : '','Duration' : '', 'Dosage' : '', 'HowToTake' : '', 'OtherName' : []} 

        elif ' vs ' in drug_list[i]['InterventionName'].lower():

            temp = drug_list[i]['InterventionName'].lower().split(' vs ')

            for data in temp:
                drug.append(data.lower().replace('drug: ', ""))
                drug_dict[data.lower().replace('drug: ', "")] = {'DrugName' : '','Duration' : '', 'Dosage' : '', 'HowToTake' : '', 'OtherName' : []} 

        elif ' and ' in drug_list[i]['InterventionName'].lower():

            temp = drug_list[i]['InterventionName'].lower().split(' and ')

            for data in temp:
                drug.append(data.lower().replace('drug: ', ""))
                drug_dict[data.lower().replace('drug: ', "")] = {'DrugName' : '','Duration' : '', 'Dosage' : '', 'HowToTake' : '', 'OtherName' : []}     
        
        else:
            if drug_list[i]['InterventionName'].lower().replace('drug: ', "") not in drug:
                drug.append(drug_list[i]['InterventionName'].lower().replace('drug: ', ""))
            drug_dict[drug_list[i]['InterventionName'].lower().replace('drug: ', "")] = {'DrugName' : '','Duration' : '', 'Dosage' : '', 'HowToTake' : '', 'OtherName' : []} 
    #print(drug)
    # print(drug_dict)

    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            if i in value["InterventionName"].lower().replace("drug: ","") or i in value["InterventionName"].lower().replace("drug: ",""):
                try:
                    for other in value["InterventionOtherNameList"]["InterventionOtherName"]:
                        drug_dict[i]['OtherName'].append(other)
                except KeyError:
                    pass




    dummy_entity = ["(",")"]
    temp13 = detail_description + brief_description
    temp13 = temp13.replace(","," ").split(". ")
    slpit = []
    






    for i in temp13:
        for dummy in dummy_entity:
            i = i.replace(dummy,"")
        slpit.append(i.replace("-", " - ").replace("/", " / "))

    # for dummy in dummy_entity:
    #     for i in temp13:
    #         slpit.append(i.replace("-", " - ").replace("/", " / "))
 ########################################################################################
 # 밑에 코드는 description부분에 약물 복용 주기, 약물 복용량을 찾아서 넣는 코드를 작성함# ## 얘는 Druf Dict를 이용해서 하는게 아니라서 상관 없을 것 같음. >> 마지막에 Dictionary의 키값을 Drug의 내용으로하는데,
 #결론적으로는 Key값 바탕으로 Value 값으로 약물명을 추가하기 때문에, 이때 추가할때 동시에 다른 이름까지넣으면 될 것 같음.
 ######################################################################################## 
 ########################################################################################
 # 밑에 코드는 description부분에 약물 복용 주기, 약물 복용량을 찾아서 넣는 코드를 작성함# ## 얘는 Druf Dict를 이용해서 하는게 아니라서 상관 없을 것 같음. >> 마지막에 Dictionary의 키값을 Drug의 내용으로하는데,
 #결론적으로는 Key값 바탕으로 Value 값으로 약물명을 추가하기 때문에, 이때 추가할때 동시에 다른 이름까지넣으면 될 것 같음.
 ######################################################################################## 
    for i1 in range(len(slpit)):     #시간 관련된 내용
        temp = slpit[i1].lower().split()
        # print(temp)
        for i2 in range(len(drug)):
            #print(drug[i2],"----------------------------", slpit[i1])
            if drug[i2] in slpit[i1].lower() or drug[i2] + ' ' in slpit[i1].lower():
                #print(temp)
                
                try:
                    #print(drug[i2], slpit[i1].lower())
                    drug_index = temp.index(drug[i2].split()[0])
                    for i5 in range(len(time_label)):
                        for i3 in range(drug_index-1, -1, -1):
                            if time_label[i5] == temp[i3]:
                                left = i3
                                break
                        for i4 in range(drug_index, len(temp)):
                            if time_label[i5] == temp[i4]:
                                right = i4
                                break

                    for i5 in range(len(amount)):
                        for i3 in range(drug_index-1, -1, -1):
                            if amount[i5] in temp[i3]:
                                d_left = i3
                                break
                        for i4 in range(drug_index, len(temp)):
                            if amount[i5] in temp[i4]:
                                d_right = i4
                                break

                    if left != 0 or right != 0:
                        if left == 0 or abs(drug_index - left) >= abs(drug_index - right):
                            drug_date.append(temp[drug_index : right + 1])
                            drug_dict[drug[i2].lower()]['Duration'] = temp[right - 1] + " " + temp[right]
                        elif right == 0 or abs(drug_index - left) < abs(drug_index - right):
                            drug_date.append(temp[left-1 :drug_index  + 1])
                            drug_dict[drug[i2].lower()]['Duration'] = temp[left - 1] + " " + temp[left]
                    if d_left != 0 or d_right != 0:
                        if d_left == 0 or abs(drug_index - d_left) >= abs(drug_index - d_right):
                            drug_date.append(temp[drug_index : d_right + 1]) # 복용량 관련 내용
                            if temp[d_right - 1].isdigit() == True:
                                drug_dict[drug[i2].lower()]['Dosage'] = temp[d_right - 1] + "  " + temp[d_right]
                        elif d_right == 0 or abs(drug_index - d_left) < abs(drug_index - d_right):
                            drug_date.append(temp[d_left-1 :drug_index  + 1])
                            if temp[d_left - 1].isdigit() == True:
                                drug_dict[drug[i2].lower()]['Dosage'] = temp[d_left - 1] + " " + temp[d_left]

                    d_left = 0 
                    d_right = 0 
                    left = 0 
                    right = 0
                except:
                    pass
                
            elif drug[i2].lower() in slpit[i1].lower() or drug[i2].lower() + ' ' in slpit[i1].lower() :
                
                try:                
                    drug_index = temp.index(drug[i2].split()[0].lower())
                    for i5 in range(len(time_label)):
                        for i3 in range(drug_index-1, -1, -1):
                            if time_label[i5] == temp[i3]:
                                left = i3
                                break
                        for i4 in range(drug_index, len(temp)):
                            if time_label[i5] == temp[i4]:
                                right = i4
                                break

                    for i5 in range(len(amount)):
                        for i3 in range(drug_index-1, -1, -1):
                            if amount[i5] in temp[i3]:
                                d_left = i3
                                break
                        for i4 in range(drug_index, len(temp)):
                            if amount[i5] in temp[i4]:
                                d_right = i4
                                break

                    if left != 0 or right != 0:
                        if left == 0 or abs(drug_index - left) >= abs(drug_index - right):
                            drug_date.append(temp[drug_index : right + 1])
                            drug_dict[drug[i2].lower()]['Duration'] = temp[right - 1] + " " + temp[right]
                        elif right == 0 or abs(drug_index - left) < abs(drug_index - right):
                            drug_date.append(temp[left-1 :drug_index  + 1])
                            drug_dict[drug[i2].lower()]['Duration'] = temp[left - 1] + " " + temp[left]
                    if d_left != 0 or d_right != 0:
                        if d_left == 0 or abs(drug_index - d_left) >= abs(drug_index - d_right):
                            drug_date.append(temp[drug_index : d_right + 1]) # 복용량 관련 내용
                            if temp[d_right - 1].isdigit() == True:
                                drug_dict[drug[i2].lower()]['Dosage'] = temp[d_right - 1] + "  " + temp[d_right]
                        elif d_right == 0 or abs(drug_index - d_left) < abs(drug_index - d_right):
                            drug_date.append(temp[d_left-1 :drug_index  + 1])
                            if temp[d_left - 1].isdigit() == True:
                                drug_dict[drug[i2].lower()]['Dosage'] = temp[d_left - 1] + " " + temp[d_left]

                    d_left = 0
                    d_right = 0
                    left = 0
                    right = 0
                except:
                    pass
    #print(drug_dict)
#################################################################################
#밑에 코드는 queue써서 ArmgroupDescription쪽에서 기간관련 내용 찾는 코드(폐기각)#
#################################################################################

##########################################################################
#밑에 코드는 queue써서 intervention쪽에서 기간관련 내용 찾는 코드(폐기각)#
##########################################################################

    # protocolsection = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']

    # for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
    #     value_line = value['InterventionDescription'].split('. ')
    #     for line in value_line:
    #         temp = line.split()
    #         for i2 in drug_dict:
    #             for i1 in range(len(temp)):
    #                 if (temp[i1] in i2):
    #                     dosage_que.put(temp[i1])
    #                 for i3 in amount:
    #                     if i3 in temp[i1]:
    #                         dosage_que.put( temp[i1-1] + temp[i1])
    # for i in range(dosage_que.qsize()):
    #     print(dosage_que.get())

######################################################################
#밑에 코드는 comprehend써서 intervention쪽에서 복용량, 기간 찾는 코드#
######################################################################
    #comprehend = boto3.client('comprehend')

    
    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            drug_dict[i.lower()]['DrugName'] = i.lower()
            if i == value["InterventionName"].lower():
                try:
                    DetectEntitiestext = value['InterventionDescription']
                    test = (comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'))
                    for i2 in range(len(test['Entities'])):
                        if(test['Entities'][i2]['Type'] == "QUANTITY"):
                            for k in range(len(amount)):
                                if (amount[k] in test['Entities'][i2]['Text'].lower()):
                                    drug_dict[i.lower()]['Dosage'] = test['Entities'][i2]['Text']
                                # drug_dict[i.lower()]['Dosage'] = drug_dict[i.lower()]['Dosage'] + " " + test['Entities'][i2]['Text'] 다시한번 생각해 봐야할 듯
                        for j in range(len(time_label2)):
                            if time_label2[j] in test['Entities'][i2]['Text'].lower():
                                drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Text']
                        for j in range(len(eat_way)):
                            if eat_way[j] in test['Entities'][i2]['Text'].lower():
                                drug_dict[i.lower()]['HowToTake'] = test['Entities'][i2]['Text']
                except KeyError:
                    pass
    #print(drug_dict)

    #print(drug_dict)
    #comprehend_med = boto3.client(service_name='comprehendmedical')

###########################################################################################################################
#밑에 코드는 ACM써서 인터벤션 디스크립션 부분에서 약물 복용법, 복용 주기 관련 내용 추출(같은 약물 다른 내용을 바탕으로 함)#
###########################################################################################################################

    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            drug_dict[i.lower()]['DrugName'] = i.lower() 
            if i == value["InterventionName"].lower().replace("drug: ","") or i in value["InterventionName"].lower().replace("drug: ",""):
                try:
                    DetectEntitiestext = value['InterventionDescription'].lower().replace("drug: ","")
                    test = acm_Entities(DetectEntitiestext) 
                        #print(json.dumps(test,sort_keys=True, indent=4))
                    for other in drug_dict[i.lower()]['OtherName']:
                        for i2 in range(len(test['Entities'])):
                            if test['Entities'][i2]['Text'].lower() in other.lower():
                                try:
                                    for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                        if test['Entities'][i2]['Attributes'][i3]['Type'] == "ROUTE_OR_MODE":
                                            drug_dict[i.lower()]['HowToTake'] = test['Entities'][i2]['Attributes'][i3]['Text'] 
                                        elif test['Entities'][i2]['Attributes'][i3]['Type'] == "DURATION":
                                            drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                        elif test['Entities'][i2]['Attributes'][i3]['Type'] == "DOSAGE" or test['Entities'][i2]['Attributes'][i3]['Type'] == "STRENGTH":
                                            drug_dict[i.lower()]['Dosage'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                except KeyError:
                                    pass                       
                except KeyError:
                    pass
########################################################################################
#밑에 코드는 ACM써서 인터벤션 디스크립션 부분에서 약물 복용법, 복용 주기 관련 내용 추출#
########################################################################################

    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            drug_dict[i.lower()]['DrugName'] = i.lower() 
            if i == value["InterventionName"].lower().replace("drug: ","") or i in value["InterventionName"].lower().replace("drug: ",""):
                try:
                    DetectEntitiestext = value['InterventionDescription'].lower().replace("drug: ","")

                    if 'placebo' in i.lower() :
                        dlist = DetectEntitiestext.split()
                        if 'placebo' in dlist:
                            dlist[dlist.index('placebo')] = "acetaminophen"
                            DetectEntitiestext = " ".join(dlist)
                            #print(DetectEntitiestext)
                            test = acm_Entities(DetectEntitiestext)
                            for i2 in range(len(test['Entities'])):
                                if test['Entities'][i2]['Text'].lower() == "acetaminophen":
                                    test['Entities'][i2]['Text'] = 'placebo'
                            for i2 in range(len(test['Entities'])):    
                                if test['Entities'][i2]['Text'].lower() in i.lower():
                                    try:
                                        for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                            if test['Entities'][i2]['Attributes'][i3]['Type'] == "ROUTE_OR_MODE":
                                                drug_dict[i.lower()]['HowToTake'] = test['Entities'][i2]['Attributes'][i3]['Text'] 
                                            elif test['Entities'][i2]['Attributes'][i3]['Type'] == "DURATION":
                                                drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                            elif test['Entities'][i2]['Attributes'][i3]['Type'] == "DOSAGE" or test['Entities'][i2]['Attributes'][i3]['Type'] == "STRENGTH":
                                                drug_dict[i.lower()]['Dosage'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                    except KeyError:
                                        pass 
                            #print(test)
                    else:
                        test = acm_Entities(DetectEntitiestext) 
                        #print(json.dumps(test,sort_keys=True, indent=4))
                        for i2 in range(len(test['Entities'])):    
                            if test['Entities'][i2]['Text'].lower() in i:
                                try:
                                    for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                        if test['Entities'][i2]['Attributes'][i3]['Type'] == "ROUTE_OR_MODE":
                                            drug_dict[i.lower()]['HowToTake'] = test['Entities'][i2]['Attributes'][i3]['Text'] 
                                        elif test['Entities'][i2]['Attributes'][i3]['Type'] == "DURATION":
                                            drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                        elif test['Entities'][i2]['Attributes'][i3]['Type'] == "DOSAGE" or test['Entities'][i2]['Attributes'][i3]['Type'] == "STRENGTH":
                                            drug_dict[i.lower()]['Dosage'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                except KeyError:
                                    pass                         
                    if value["InterventionName"].lower().replace("drug: ","") in i:
                        for i4 in range(len(test['UnmappedAttributes'])):
                            try:
                                #print(test['UnmappedAttributes'][i4]['Attributes']['Text'])
                                if test['UnmappedAttributes'][i4]['Attributes']['Type'] == "ROUTE_OR_MODE":
                                    drug_dict[i.lower()]['HowToTake'] = test['UnmappedAttributes'][i4]['Attributes']['Text']
                                elif test['UnmappedAttributes'][i4]['Attributes']['Type'] == "DURATION":
                                    drug_dict[i.lower()]['Duration'] = test['UnmappedAttributes'][i4]['Attributes']['Text']
                                elif test['UnmappedAttributes'][i4]['Attributes']['Type'] == "DOSAGE" or test['Entities'][i2]['Attributes'][i3]['Type'] == "STRENGTH":
                                    drug_dict[i.lower()]['Dosage'] = test['UnmappedAttributes'][i4]['Attributes']['Text']    
                            except KeyError:
                                pass
                except KeyError:
                    pass

########################################################################################
#밑에 코드는 ACM써서 ArmGroupdescription 부분에서 약물 복용법, 복용 주기 관련 내용 추출#
########################################################################################
    for value in protocolsection['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']:
        try:
            DetectEntitiestext = value['ArmGroupDescription']
            test = acm_Entities(DetectEntitiestext)
            for i in drug_dict:
                for i2 in range(len(test['Entities'])):
                    if test['Entities'][i2]['Text'].lower() in i:
                        try:
                            for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                if test['Entities'][i2]['Attributes'][i3]['Type'] == "DOSAGE":
                                    drug_dict[i.lower()]['Dosage'] = test['Entities'][i2]['Attributes'][i3]['Text']
                            
                                    break
                            for i3 in range(len(test['Entities'][i2]['Attributes'])): 
                                if test['Entities'][i2]['Attributes'][i3]['Type'] == "DURATION":
                                    drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Attributes'][i3]['Text']
                                    break
                        except KeyError:
                            pass                    

                #print(json.dumps(test,sort_keys=True, indent=4)) 
        except KeyError:
            pass    

#################################################################################################
#밑에 코드는 ACM써서 디스크립션 부분에서 약물 복용 주기 내용 찾는 코드(무조건 마지막에 나와야함)#
#################################################################################################
    #comprehend_med = boto3.client(service_name='comprehendmedical')

    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            if i == value["InterventionName"].lower():
                try:
                    DetectEntitiestext = value['InterventionDescription']
                   
                    if i.lower() == 'placebo':
                        dlist = DetectEntitiestext.split()
                        if 'placebo' in dlist:
                            dlist[dlist.index('placebo')] = "acetaminophen"
                            DetectEntitiestext = " ".join(dlist)
                            #print(DetectEntitiestext)
                            test = acm_Entities(DetectEntitiestext)
                            for i2 in range(len(test['Entities'])):
                                if test['Entities'][i2]['Text'].lower() == "acetaminophen":
                                    test['Entities'][i2]['Text'] = 'placebo'
                            for i2 in range(len(test['Entities'])):    
                                if test['Entities'][i2]['Text'].lower() in i:
                                    try:
                                        for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                            if test['Entities'][i2]['Attributes'][i3]['Type'] == "FREQUENCY" and test['Entities'][i2]['Attributes'][i3]['Text'] not in drug_dict[i.lower()]['Duration']:
                                                drug_dict[i.lower()]['Duration'] = drug_dict[i.lower()]['Duration'] + "(" + test['Entities'][i2]['Attributes'][i3]['Text'] + ")"
                                    except KeyError:
                                        pass 
                    else:
                        test = acm_Entities(DetectEntitiestext) 
                        for i2 in range(len(test['Entities'])):
                            try:
                                for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                    if test['Entities'][i2]['Attributes'][i3]['Type'] == "FREQUENCY" and test['Entities'][i2]['Attributes'][i3]['Text'] not in drug_dict[i.lower()]['Duration']:
                                        drug_dict[i.lower()]['Duration'] = drug_dict[i.lower()]['Duration'] + "(" + test['Entities'][i2]['Attributes'][i3]['Text'] + ")"
                            except KeyError:
                                pass
                except KeyError:
                    pass

    for value in protocolsection['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']:
        try:
            DetectEntitiestext = value['ArmGroupDescription']
            test = acm_Entities(DetectEntitiestext)
            for i in drug_dict:
                for i2 in range(len(test['Entities'])):
                    if test['Entities'][i2]['Text'].lower() in i:
                        try:
                            for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                if test['Entities'][i2]['Attributes'][i3]['Type'] == "FREQUENCY" and test['Entities'][i2]['Attributes'][i3]['Text'] not in drug_dict[i.lower()]['Duration']:
                                    drug_dict[i.lower()]['Duration'] = drug_dict[i.lower()]['Duration'] + "(" + test['Entities'][i2]['Attributes'][i3]['Text'] + ")"

                        except KeyError:
                            pass                    
        except KeyError:
            pass    

# 밑에꺼가 전체 설명에서 뽑는 것인데, 여기서 조금 추가해서 더 할지 아니면 어케 더해야할지 모르겠네.
    DetectEntitiestext = brief_description + ' ' + detail_description
    result = acm_Entities(DetectEntitiestext)
    entities = result['Entities']
    for value in entities:
        try:
            for content in value['Attributes']:
                if content['RelationshipType'] == "FREQUENCY":
                    for content2 in drug_dict:
                        if value["Text"] in content2 and content['Text'] not in drug_dict[content2]['Duration']:
                            drug_dict[content2]['Duration'] = drug_dict[content2]['Duration'] +"("+ content['Text'] + ")"
        except KeyError:
            pass

    for arm in Arm_group:
        try:
            for DrugName in Arm_group[arm]['InterventionList']['ArmGroupInterventionName']:
                for DrugInList in drug_dict:
                    temp = DrugName.split()
                    # print(temp)
                    # print(" ".join(temp[1:]))

                    if DrugInList == " ".join(temp[1:]).lower():
                        Arm_group[arm]['InterventionDescription'].append(drug_dict[DrugInList])
        except TypeError:
            pass
                    #Arm_group[arm]['InteventionDescription'][DrugInList] = ("'" + DrugInList + "'" + ": "+  "{" + drug_dict[DrugInList] + "}")
                    #Arm_group[arm]['InteventionDescription'][DrugInList] = drug_dict[DrugInList]
    for arm in Arm_group:
        try:
            for Drugidx in range(len(Arm_group[arm]['InterventionDescription'])):
                Arm_group[arm]['ArmGroupDescription'] = Arm_group[arm]['ArmGroupDescription'] + Arm_group[arm]['InterventionDescription'][Drugidx]['DrugName']  + ': '  +  Arm_group[arm]['InterventionDescription'][Drugidx]['Dosage'] + ' ' + Arm_group[arm]['InterventionDescription'][Drugidx]['Duration'] + ' ' + Arm_group[arm]['InterventionDescription'][Drugidx]['HowToTake']
                Arm_group[arm]['ArmGroupDescription'] += ', '

        except KeyError:
            pass

    for key in Arm_group:
        InterventionDrug['ArmGroupList'].append(Arm_group[key])

    return_dictionary = {"DrugInformation" : InterventionDrug}
    #print(json.dumps(return_dictionary,sort_keys=True, indent=4))
#################################################################################################
#밑에 코드는 ACM써서 ARm 디스크립션 부분에서 약물 복용 주기 내용 찾는 코드(유사한 내용 바탕으로 실시)#
#################################################################################################

    for value1 in return_dictionary['DrugInformation']['ArmGroupList']:
        medi_loc = 0
        dosa_loc = 0
        abs_s = 100
        dosa = ""
        for value2 in protocolsection['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']:
            try:
                if value1['ArmGroupLabel'] == value2['ArmGroupLabel']:
                    DetectEntitiestext = value2['ArmGroupDescription'].replace("/", " / ").replace("\n","")
                    result = acm_Entities(DetectEntitiestext)
                    #print(json.dumps(result,sort_keys=True, indent=4))
                    entities = result['Entities']
                    for i in range(len(value1["InterventionDescription"])):
                        for other in value1["InterventionDescription"][i]["OtherName"]:
                            for value in entities:
                                if value["Text"].lower().replace(" / ", "/") in other.lower():
                                    try:
                                        for content in value['Attributes']:
                                            if content['RelationshipType'] == "DOSAGE" or content['RelationshipType'] == "STRENGTH":
                                                if content['Text'] != value1["InterventionDescription"][i]['Dosage']:
                                                    value1['InterventionDescription'].append({"Dosage" : content['Text'], "DrugName" : value1["InterventionDescription"][i]['DrugName'], "Duration" : value1["InterventionDescription"][i]["Duration"], "HowToTake" : value1["InterventionDescription"][i]["HowToTake"], "OtherName" : value1["InterventionDescription"][i]["OtherName"]})
                                                    del value1["InterventionDescription"][i]
                                    except KeyError:
                                        pass              
            except KeyError:
                pass        

    for value1 in return_dictionary['DrugInformation']['ArmGroupList']:
        medi_loc = 0
        dosa_loc = 0
        abs_s = 100
        dosa = ""
        for value2 in protocolsection['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']:
            try:
                if value1['ArmGroupLabel'] == value2['ArmGroupLabel']:
                    
                    DetectEntitiestext = value2['ArmGroupDescription'].replace("/", " / ").replace("\n","")
                    result = acm_Entities(DetectEntitiestext)
                    #print(json.dumps(result,sort_keys=True, indent=4))
                    entities = result['Entities']

                    for i in range(len(value1["InterventionDescription"])):
                        for value in entities:
                            #print("entity : " + value["Text"] , "DrugName : " + value1["InterventionDescription"][i]["DrugName"])
                            # print(value["Text"] , value1["InterventionDescription"][i]["DrugName"])
                            if value["Text"].lower().replace(" / ", "/") in value1["InterventionDescription"][i]["DrugName"]:
                                
                                
                                try:
                                    for content in value['Attributes']:
                                        #print(content['RelationshipType'])
                                        if content['RelationshipType'] == "DOSAGE" or content['RelationshipType'] == "STRENGTH":
                                            
                                            #print("22222222222")
                                            if content['Text'] != value1["InterventionDescription"][i]['Dosage']:
                                                value1['InterventionDescription'].append({"Dosage" : content['Text'], "DrugName" : value1["InterventionDescription"][i]['DrugName'], "Duration" : value1["InterventionDescription"][i]["Duration"], "HowToTake" : value1["InterventionDescription"][i]["HowToTake"], "OtherName" : value1["InterventionDescription"][i]["OtherName"]})
                                                del value1["InterventionDescription"][i]
                                except KeyError:
                                    pass

                for i in drug_dict:
                    for i2 in range(len(test['Entities'])):
                        if test['Entities'][i2]['Text'].lower() in i:
                            try:
                                for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                    if test['Entities'][i2]['Attributes'][i3]['Type'] == "FREQUENCY" and test['Entities'][i2]['Attributes'][i3]['Text'] not in drug_dict[i.lower()]['Duration']:
                                        drug_dict[i.lower()]['Duration'] = drug_dict[i.lower()]['Duration'] + "(" + test['Entities'][i2]['Attributes'][i3]['Text'] + ")"

                            except KeyError:
                                pass                    
            except KeyError:
                pass        

        

    for value1 in return_dictionary['DrugInformation']['ArmGroupList']:
        medi_loc = 0
        dosa_loc = 0
        abs_s = 100
        dosa = ""
        DetectEntitiestext = value1['ArmGroupLabel']
        # print(DetectEntitiestext)
        result = acm_Entities(DetectEntitiestext)
        result2 = comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en')
        # print(json.dumps(result,sort_keys=True, indent=4))
        #print(json.dumps(result2,sort_keys=True, indent=4))
        entities = result['Entities']
        entities2 =  result2['Entities']
        for value in entities:
            try:
                for content in value['Attributes']:
                        for i in range(len(value1['InterventionDescription'])):
                            if value["Text"].lower() in value1['InterventionDescription'][i]["DrugName"].lower():
                                if content['RelationshipType'] == "DOSAGE" or content['RelationshipType'] == "STRENGTH":
                                    if content['Text'] != value1['InterventionDescription'][i]['Dosage']:
                                        value1['InterventionDescription'].append({"Dosage" : content['Text'], "DrugName" : value1["InterventionDescription"][i]['DrugName'], "Duration" : value1["InterventionDescription"][i]["Duration"], "HowToTake" : value1["InterventionDescription"][i]["HowToTake"], "OtherName" : value1["InterventionDescription"][i]["OtherName"]})
                                        del value1['InterventionDescription'][i]

            except KeyError:
                for value in entities2:
                    for i in range(len(value1['InterventionDescription'])):
                        if value["Text"].lower() in value1['InterventionDescription'][i]["DrugName"]:
                            medi_loc =  (value["BeginOffset"] + value["EndOffset"])/2
                            # print(medi_loc)
                            for value3 in entities2:
                                for value2 in amount:
                                    if value2 in value3["Text"]:
                                        #print(value3["Text"])
                                        dosa_loc = (value3["BeginOffset"] + value3["EndOffset"])/2
                                        if abs_s > abs(medi_loc - dosa_loc):
                                            abs_s = abs(medi_loc - dosa_loc)
                                            dosa = value3["Text"]
                        if dosa != "" and dosa != value1['InterventionDescription'][i]['Dosage']:                    
                            value1['InterventionDescription'].append({"Dosage" : dosa, "DrugName" : value1['InterventionDescription'][i]["DrugName"], "Duration" : value1['InterventionDescription'][i]["Duration"], "HowToTake" : value1['InterventionDescription'][i]["HowToTake"], "OtherName" : value1["InterventionDescription"][i]["OtherName"]})
                            del value1['InterventionDescription'][i]
        # for value2 in value1['InterventionDescription']:


    return return_dictionary


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_population_ratio(response):

    #test example 1 with n=~ https://www.clinicaltrials.gov/ct2/show/NCT03507790?recrs=ab&type=Intr&cond=Alzheimer+Disease&draw=2
    #test example 2 without n=~ https://www.clinicaltrials.gov/ct2/show/NCT02285140?term=factorial&draw=3

    #save the detail of armDescription
    population_list, save_value, rate, rateString, count = [], [], [], '', 0

    #if there is no "n=~~~"
    #count = 0
    #get the total participates number
    #total = int(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount'])
    #save_total = int(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount'])
    #get the detail of each arm group

    try:
        for i in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']["ArmGroupList"]["ArmGroup"])):
            findPopulation = ''.join([str(item) for item in response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup'][i]['ArmGroupDescription']])
            population_list.append(findPopulation)

        #get the int value of each arm group
        for i in range(len(population_list)):
            #if there is such that matches then meaning there is set ratio
            if "n=" in population_list[i] or "n= " in population_list[i] or "n:" in population_list[i]:
                length_word = len(population_list[i])
                #check if there is word that matches
                start_index=re.search("n=", population_list[i]).start()
                #get the exact value
                extracted_string= population_list[i][start_index:start_index+length_word]
                #print(extracted_string)
                #take out the value of extracted, for example if n=40, get 40 and minus from the total
                save_value.append([int(num) for num in re.findall(r"\d+", extracted_string)][0])

        if count == 0:
            for i in range(len(save_value)):
                rate.append(save_value[i]/math.gcd(*save_value))
            rateString =str(rate[0])
            for i in range(1,len(rate)):
                rateString = rateString +" : " +str(rate[i])

        else:
            #just up up the total
            count += 1
            
    except:
        population_list.append("")

    if rateString == '':
        try:
            DetailedDescription = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['DetailedDescription'].split()
            for i in range(len(DetailedDescription)):
                if "ratio" in DetailedDescription[i]:
                    if ":" in DetailedDescription[i-1]:
                        rateString = DetailedDescription[i-1]
                    elif ":" in DetailedDescription[i+1]:
                        rateString = DetailedDescription[i+1]
        except:
            pass


    return_population_ratio_dictionary = {"PopulationRatio" : rateString}
    return return_population_ratio_dictionary

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_washout(response):
    period = ['washout','wash-out','recovery','run-in','taper','wash']
    times = ['day','days','week','weeks','month','months','year','years']
    line = ""
    index, value = [], []
    min_index, hasWash, hasTime, min = 0, 0, 0, 100

    # washout이 어디에 있는지 확인하고 split하기
    for i in range(len(period)):
            try:
                for j in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'])):
                    content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'][j]['InterventionDescription']
                    content = content.lower()
                    if(period[i] in content):
                        content_list = content.split('.')
                        hasWash += 1
                        break
            except:
                pass
            try:
                for j in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup'])):
                    content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup'][j]['ArmGroupDescription']
                    content = content.lower()
                    if(period[i] in content):
                        content_list = content.split('\n')
                        hasWash += 1
                        break
            except:
                pass

    if (hasWash == 0):
        for i in range(len(period)):
            try:
                content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["BriefSummary"]
                content = content.lower()
                if(period[i] in content):
                   content_list = content.split('.')
                   hasWash += 1
                   break
            except:
                content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['EligibilityModule']['EligibilityCriteria']
                content = content.lower()
                if(period[i] in content):
                   content_list = content.split('\n')
                   hasWash += 1
                   break
            try:
                content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["DetailedDescription"]
                content = content.lower()
                if(period[i] in content):
                   content_list = content.split('.')
                   hasWash += 1
                   break
            except:
                pass

    # washout 없는 경우
    if(hasWash == 0):
        return {"WashoutPeriod" : ""}

    #washout 있는 line만 추출
    for i in range(len(content_list)):
        for j in range(len(period)):
            if(period[j] in content_list[i]):
                line = content_list[i]
                #washout_index = line.index('period') #period관련 단어의(첫 알파벳) index파악--times 뽑기 위해서
                line_list = line.split(" ")
                washout_index = line.index(period[j]) + 5 #-> washout으로 인덱싱
                washout_index_check = line.index(period[j])

                #print(line_list[washout_index-1])

    #without washout period 잡기
    without = "without"
    count = 0
    for i in range(7):
        #print(line[washout_index_check -(i+2)])
        #print("======")
        #print(without[6-i])
        if(line[washout_index_check -(i+2)] == without[6-i]):
            count = count + 1

    if(count==7):
        return {"WashoutPeriod" : "without washout period"}

    # if(line_list[washout_index_check -8]=='without'):
    #     return {"WashoutPeriod" : "without washout period"}
                # if('without' in line):
                #     return {"washout_period" : ""} #without있는 문장 제외(수정 필요)
                # else:
                #     washout_index = line.index(period[j]) #period관련 단어의(첫 알파벳) index파악--times 뽑기 위해서

    #comprehend 돌리기
    #comprehend = boto3.client('comprehend') #주석 하기!!
    DetectEntitiestext = line
    test = (comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'))
    convert = json.dumps(test,sort_keys=True, indent=4)
    data = json.loads(convert)

    # Quantitiy 안에 times 있는지 있으면 뽑기
    for i in range(len(test['Entities'])):
        if(test['Entities'][i]['Type'] == "QUANTITY"):
            for j in range(len(times)):
                if (times[j] in test['Entities'][i]['Text']): #2-week, 4-week
                    index.append(line.index(test['Entities'][i]['Text']))
                    value.append(test['Entities'][i]['Text'])
                    hasTime += 1
    
    if(hasTime == 0):
        return {"WashoutPeriod" : ""}

    # period 표현과 가장 가까운 시간표현 뽑기
    for i in range(len(index)):
        if(min > abs(washout_index - index[i])):
            min = abs(washout_index - index[i])
            min_index = i
    
    #dic형태로 json파일 생성
    string_result = value[min_index]
    change_dictionary = "{%s : %s%s%s}" % ('"WashoutPeriod"', '"', string_result, '"')
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_officialTitle(response):
    title = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['OfficialTitle']
    string_result = title
    #print(title)
    if("\"" in string_result):
        string_result = re.sub('\"', '', string_result)
        change_dictionary = "{%s : %s%s%s}" % ('"OfficialTitle"', '"', string_result, '"')
    else:
        change_dictionary = "{%s : %s%s%s}" % ('"OfficialTitle"', '"', string_result, '"')
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_objective(response):
    summary = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["BriefSummary"]
    purpose = ['objective', 'purpose', 'aim', 'evaluate', 'measure', 'intention', 'target', 'goal', 'object', 'idea', 'desire']
    list = summary.split('.')

    # 보기에는 없어도 api에는 BriefTitle이 있는 경우가 많음
    if("BriefTitle" in response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']):
        objective = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']["BriefTitle"]

    # 혹시 모를 예외 케이스를 위해 BriefSummary에 목적의 표현이 있는 문장 추출
    else:
        for i in range(len(list)):
            for j in range(len(purpose)):
                if(list[i] == purpose[j]):
                    objective = list[i]
                    break

    string_result = objective
    change_dictionary = "{\"Objective\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_maksing(response):
    try:
        masking = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['DesignInfo']['DesignMaskingInfo']['DesignMasking']
        string_result = masking
        change_dictionary = "{\"Masking\" : " + '"' + string_result + '"' + "}"
    except:
        change_dictionary = "{\"Masking\" : " + '"' + " " + '"' + "}"
        
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_allocation(response):
    try:
        allocation = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['DesignInfo']['DesignAllocation']
        string_result = allocation
        change_dictionary = "{\"Allocation\" : " + '"' + string_result + '"' + "}"
        result_dictionary = json.loads(change_dictionary)
        return(result_dictionary)
    except:
        change_dictionary = "{\"Allocation\" : " + '"' + " " + '"' + "}"

    result_dictionary = json.loads(change_dictionary)
    return result_dictionary



#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_enrollment(response):
    enrollment = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount']
    string_result = enrollment
    change_dictionary = "{\"Enrollment\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_designModel(response):
    try:
        model = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['DesignInfo']['DesignInterventionModel']
        string_result = model
        change_dictionary = "{\"DesignModel\" : " + '"' + string_result + '"' + "}"
    except:
        change_dictionary = "{\"DesignModel\" : " + '"' + " " + '"' + "}"

    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_interventionName(response):
    interventionName = []
    type = ""
    
    for i in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'])):
        type = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'][i]['InterventionType']
        name = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'][i]['InterventionName']
        if ('Placebo' in name):
            interventionName.append(name)
        elif ('+' in name):
            interventionName.append(name)
        elif(type=="Drug"):
            DetectEntitiestext = name
            test = acm_Entities(DetectEntitiestext)
            convert = json.dumps(test,sort_keys=True, indent=4)
            data = json.loads(convert)
            for j in range(len(test['Entities'])):
                if(test['Entities'][j]['Type']== 'ID'):
                    interventionName.append(test['Entities'][j]['Text'])
                elif(test['Entities'][j]['Type']=='GENERIC_NAME'):
                    interventionName.append(test['Entities'][j]['Text'])
        else:
            interventionName.append(name)
    # list -> string하면서 ', ' 넣기
    string_result = ', '.join(interventionName)
    change_dictionary = "{%s : %s%s%s}" % ('"InterventionName"', '"', string_result, '"')
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def wrapper(func, arg, queue):
        queue.put(func(arg))

def request_call(url):

    try:
        try:
            expr = re.search("NCT[0-9]+", url)
            expr = expr.group()
            if((expr == None) or ("&fmt=json" in url)):
                newURL = url
            else:
                newURL = "https://clinicaltrials.gov/api/query/full_studies?expr=" + expr + "&fmt=json"
        except:
            newURL = url.replace(" ", "")

        response = requests.get(newURL).json()
        NCTId = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']

        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, f'NCT_ID_database/{NCTId}.json')

        with open(file_path) as json_file:
            data = json.load(json_file)
            return data

    except:
        try:
            expr = re.search("NCT[0-9]+", url)
            expr = expr.group()
            if((expr == None) or ("&fmt=json" in url)):
                newURL = url
            else:
                newURL = "https://clinicaltrials.gov/api/query/full_studies?expr=" + expr + "&fmt=json"
        except:
            newURL = url.replace(" ", "")

        response = requests.get(newURL).json()

        NCTId = {"NCTID" : response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']}
        _id = {"_id" : response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']}
        version = {"version" : "1.7.1"}
        washout, drug_time, population_box = Queue(), Queue(), Queue()
        Thread(target=wrapper, args=(get_washout, response, washout)).start() 
        Thread(target=wrapper, args=(get_drug_time, response, drug_time)).start() 
        Thread(target=wrapper, args=(get_population_box, response, population_box)).start() 

        #dictionary format
        calc_date, population_ratio, official_title, objective, allocation, enrollment, design_model, masking, intervention_name, title = get_calc_date(response), get_population_ratio(response), get_officialTitle(response), get_objective(response), get_allocation(response), get_enrollment(response), get_designModel(response), get_maksing(response), get_interventionName(response), get_title(response)

        request_call = {}
        request_call.update(title)
        request_call.update(version)
        request_call.update(population_box.get())
        request_call.update(washout.get())
        request_call.update(population_ratio)
        request_call.update(calc_date)
        request_call.update(drug_time.get())
        request_call.update(official_title)
        request_call.update(objective)
        request_call.update(allocation)
        request_call.update(enrollment)
        request_call.update(design_model)
        request_call.update(masking)
        request_call.update(intervention_name)
        request_call.update(NCTId)
        #request_call.update(_id)
        request_call = {**_id, **request_call}


        #print(request_call['population_ratio'])
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, f"NCT_ID_database/{response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']}.json")
        with open(file_path, 'w') as json_file:
                json.dump(request_call, json_file,sort_keys=True, indent=4)

        return request_call

# url = "https://clinicaltrials.gov/ct2/show/NCT05356351"
# #위의 오류케이스 발견됨 >> 2가지 수정 
# # 1.만약 약물이 A and B로 묶일때 이를 쪼개는 코드로 수정함
# # 2.ArmGroup Description부분에서도 약물명 관련된 내용을 수정할 수 있도록 코드를 변형함
# url = "https://clinicaltrials.gov/ct2/show/NCT05379179"
# print(request_call(url))

if __name__ == "__main__":
    # sys.argv[1]은 url임
    print(request_call(str(sys.argv[1])))
    
    inputFromUser = str(sys.argv[1])
    response = ""
    # if(inputFromUser.find("http") == -1):
    #     inputFromUser = "https://www.clinicaltrials.gov/api/query/full_studies?expr=" + inputFromUser +"&fmt=json"
    if('NCT' in inputFromUser):
        try:
            expr = re.search("NCT[0-9]+", inputFromUser)
            expr = expr.group()
            if((expr == None) or ("&fmt=json" in inputFromUser)):
                re_url = inputFromUser
            else:
                re_url = "https://clinicaltrials.gov/api/query/full_studies?expr=" + expr + "&fmt=json"
        except:
            re_url = inputFromUser.replace(" ", "")
            
    
    response = requests.get(re_url).json()
    
    nct_id = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']

    mongoKey = os.path.join(BASE_DIR, './config/prod.js')
    
    # Making Connection
    myclient = MongoClient(secrets['mongoURI'])

    # database
    db = myclient["testdb"]

    # Created or Switched to collection
    # names: GeeksForGeeks
    Collection = db["test01"]

    file_name = nct_id +".json"

    try:
        ##Loading or Opening the json file
        with open("./NCT_ID_database/"+file_name) as file:
            file_data = json.load(file)

        if isinstance(file_data, list):
            Collection.insert_many(file_data)
        else:
            Collection.insert_one(file_data)  
    except:
        pass
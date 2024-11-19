import pandas as pd
import openai
import json
import ast
openai.api_base = "..."
openai.api_key = "..."
openai.api_version = "2023-05-15"
openai.api_type = "azure"
from langchain.chains.openai_functions import create_openai_fn_chian
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field

# Sometiems GPT's outputs are not json type, this function is to check this situation. 
def is_json_valid(var):
  try:
    json.loads(var)
    return True
  except json.JSONDecodeError:
    return False


def grading_function(analysis_prompt, resume_content): 
  """
    analysis_prompt is written for GPT, resume_content is each candidate's resume. 
    This funciton combines the prompt and the resume for grading. 
  """
  # First Step: Using GPT to gain 5 info: whether the academy meets the requirement, three scores, reason. 
  analysis_system_message_prompt = SystemMessagePromptTemplate.from_template(
    template = analysis_prompt
  )
  candidate_prompt = """CV: {text}"""
  analysis_human_message_prompt = HumanMessagePromptTemplate.from_template(
    candidate_prompt
  )
  analysis_chat_prompt = ChatPromptTemplate.from_messages(
    [analysis_system_message_prompt, analysis_human_message_prompt]
  )
  first_messages=analysis_chat_prompt.format_prompt(text=resume_content).to_messages()
  model = AzureChatOpenAI(
    Openai_api_version="2023-05-15", 
    Temperature=0,
    Request_timeout=60,
    Max_tokens=1024,
  )
  token_len = model.get_num_tokens_from_messages(fisrt_messages)
  model.deployment_name = "gpt-35-turbo" if token_len < 2000 else "gpt-35-turbo-16k"
  prompt = str(model(first_messages))

  #Second Step: Select 5 info from GPT's output,. Using GPT to add three scores as the candidate's final grade. 
  second_messages = [{"role": "user", "content": prompt}]
  function = [
    {
      "name": "get_info", 
      "description": "Get info: whether the candidate pass the test, three scores, and reason for candidate", 
      "parameters": {
        "type": "object", 
        "properties": {
          "Pass": {"type": "string", "description": "whether the candidate pass the test, according to their academic degree. "}, 
                   "score_exp": {
                   "type": "integer", 
                   "description": "The experience score of the candidate", 
                  }, 
                  "score_academy": {
                    "type": "integer",
                    "description": "The academy score of the candidate", 
                  }, 
                   "score_award": {
                     "type": "integer", 
                     "description": "The award score of the candidate", 
                   },
                   "analysis": {"type": "string", "description": "The analysis from three scores mentioned above. "},
                                "summary": {"type": "string", "description": "A short summary of the analysis. "}, 
                                },
                   "required": ["Pass, score_exp, score_academy, score_award, analysis, summary"], 
      },
    }
  ]

  openai.api_base = "https:    "
  openai.api_key = "      "
  openai.api_version = "2023-07-01-preview"
  openai.api_type = "azure"
  second_response = openai.ChatCompletion.create(
    engine = "gpt-35-turbo",
    messages = second_messages, 
    functions = functions,
    function_call = "auto",
    )
  response_message = second_response["choices"][0]["message"]

  # Third Step: check whether the second step's output is json type.
  arguments = response_message["function_call"]["arguments"]
  if is_json_valid(arguments):
    arguments = json.loads(arguments)
    whether_pass = arguments["Pass"]
    score_exp = arguments["score_exp"]
    score_academy = arguments["score_academy"]
    score_award = arguments["score_award"]
    analysis = arguments["analysis"]
    summary = arguments["summary"]
  else:
    whether_pass = str("Value loss")
    score_exp = -1
    score_academy = -1
    score_award = -1
    analysis = str("Value loss")
    summary = str("Value loss")
  return whether_pass, score_exp, score_academy, score_award, analysis, summary

  # write prompt, for each resume, determine whether the academic qualifications meet the requirements, 
  #  score based on academic qualifications, work and internship experience, and awards, and give reasons for the score
  analysis_prompt = f"""
    You are a professional human resource who work for Luckin Coffee. You need to grade each candidate according to their resume. \ 
    You also need to judge whether their experiences is related to catering industry, coffee, tea, milk tea, yogurt, or waiter. \ 
    df varaiable contains all the resume. \ 
    In the resume, some information is written in English, the rest of the information is written in Chinese. \ 
    You need to focus in both English and Chinese information. \ 
  
    Judge Experience Method: 
      1 - The number of project or experience is 0, score_exp = 0, \
      2 - The candidate has project or experience, neither of them is directly related to food or beverage area or waiter. \  
      3 - The candidate has project or experience, among them, one of them is directly related to food or beverage area or waiter. \
      4 - The candidate has project or experience, among them, two of them is directly related to food or beverage area or waiter. \  
      5 - The candidate has project or experience, among them, more than two of them is directly related to food or beverage area or waiter. \

    Judge Academy Method: 
      1 - academicDegree is "High school" or "Technical secondary school", score_academy = 10. \ 
      2 - academicDegree is "College",  score_academy = 15. \ 
      3 - academicDegree is "Undergraduate" or "Master" or "Phd", score_academy = 20. \ 

    Judge Award Method: 
      1 - The number of award is 0, score_award = 0. \
      2 - The number of award is equal or larger than 0, score_award = 15. \

    Think step by step: 
      1 - Judging whether the candidate pass the test: \ 
          if the academicDegree is "Specialized" or "Undergraduate", then the candidate pass the test. \
          if the academicDegree is "High school" or "Specialized", then the candidate doesn't pass the test. \
      2 - Print whether the candidate pass the test or not. \ 
      3 - The initial value of score_exp is 0. \ 
          Using <experienceInfo> in the resume, obtain score_exp and remember this number, \ 
          detailed scoring criteria seen in <Judge Experience Method>. \ 
      4 - The initial value of score_academy is 0. \ 
          Using <academicDegree> in the resume, obtain score_academy and remember this number, \ 
          detailed scoring criteria seen in <Judge Academy Method>. \ 
      5 - The initial value of score_award is 0. \ 
          Using <awardInfo> in the resume, obtain score_award and remember this number, \ 
          detailed scoring criteria seen in <Judge Award Method>. \ 
      6 - The score_exp, score_academy, and score_award do not affect each other. \ 
      7 - Print the score_exp, score_academy, and score_award. \ 
      8 - Give a detailed analysis from experience, academy, and award perspectives, \
          List the experience that related to the food or beverage area(if the candidate has), \ 
          double check whether it is related to the food or beverage area. \ 
      9 - Give a summary of the analysis mentioned below. \ 
  
    Format: 
      Pass: Yes/No. 
      score_exp, score_academy, score_award. 
      Analysis. 
      Summary. 
  """

  #write prompt, for each resume, translate the English scoring reasons into Chinese
  def translation(prompt_reason, reason):
    analysis_system_message_prompt = SystemMessagePromptTemplate.from_template(
      template = prompt_reason
    )
    reason_prompt = """Input: {reason}"""
    Analysis_human_message_prompt = HumanMessagePromptTemplate.from_template(
      Reason_prompt
    )
    analysis_chat_prompt  = ChatPromptTemplate.from_messages(
      [analysis_system_message_prompt, analysis_human]
    )
    trans_messages = analysis_chat_prompt.format_prompt(reason=reason).to_messages()
    model = AzureChatOpenAI(
      openai_api_version = "2023-05-15",
      temperature = 0, 
      request_timeout = 60, 
      max_token = 1024,
    )
    token_len = model.get_nun_tokens_from_messages(trans_messages)
    model.deployment_name = "gpt-35-turbo" if token_len <2000 else "gpt-35-turbo-16k"
    return str(model(trans_messages).content)


    Prompt_chinese = f"""
      You are a professional translator. 
      Your job is to translate the reason from English to elegant Chinese. 
      Reason: ```<reason>```
    """
  
  #main function
  def full_time(df): 
    df_new = df['dt', 'applicationId', 'candidateId', 'company', 'position_title', 'resume_content'].copy()
    is_recommended = []
    total_score = []
    recommend_analysis = []
    recommend_reason = []
    summary = []
    for i in range(0, len(df)):
      text = df.iloc[i, -3].replace("nan", "0")
      text = ast.literal_eval(text)
      text.pop(0)
      text.pop(0)
      text.pop(1)
      is_recommended_temp, score_exp_temp, score_academy_temp, score_award_temp, analysis_temp, summary_temp = grading_function(analysis_prompt, text)
      total_score_temp = score_exp_temp + score_academy_temp + score_award_temp
      #Check if the grade overflows. 
      if total_score_temp > 100: 
        Total_score_temp = 100
        analysis_chinese_temp = translation(prompt_chinese, analysis_temp)
        summary_chinese_temp = translation(prompt_chinese, summary_temp)
        print(i, "success", is_recommended_temp, analysis_chinese_temp)
        is_recommended.append(is_recommended_temp)
        total_score.append(total_score_temp)
        recommend_analysis.append(analysis_chinese_temp)
        recommend_reason.append(analysis_chinese_temp)
        summary.append(summary_chinese_temp)

    df_new["recommend_analysis"] = recommend_analysis
    df_new["recommend_reason"] = recommend_reason
    df_new["is_recommended"] = is_recommended
    df_new["total_score"] = total_score
    df_new["summary"] = summary

  return df_new


  #****
  from fulltime import full_time
  import pandas as pd

  df = pd.read_csv('barista_1103.csv')
  new_df = full_time(df)
  new_df.to_csv('final_1103.csv')
import pandas as pd
import ast
from grading import grading_function
from translation import translation
  
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


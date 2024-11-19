from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chat_models import AzureChatOpenAI

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
  
import re
from datetime import datetime, timezone
import requests
from odoo import models, _
from odoo.tools import html2plaintext

class CommunicationChannel(models.Model):
    _inherit = 'discuss.channel'
        
    def _notify_thread(self, message, msg_vals=False, **kwargs):
        rdata = super(CommunicationChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        partner_chatgpt = self.env.ref("vg_azure_openai_integration.partner_chatgpt")
        user_chatgpt = self.env.ref("vg_azure_openai_integration.user_chatgpt")
        author_id = msg_vals.get('author_id')
        chatgpt_name = str(partner_chatgpt.name or '') + ', '
        prompt = msg_vals.get('body')
        if not prompt:            
            return rdata
        
        if author_id != partner_chatgpt.id and (chatgpt_name in msg_vals.get('record_name', '') or 'ChatGPT,' in msg_vals.get('record_name', '')) and self.channel_type == 'chat':            
            ICP = self.env['ir.config_parameter'].sudo()
            past_message_included = self.env.user.past_message_included
            msg_history = self.get_channel_messages(self.id, past_message_included)
            formatted_msgs = self.format_for_openai(msg_history, partner_chatgpt.id)             
            res = self._get_chatgpt_response(prompt=prompt, msg_history=formatted_msgs)                              
            self.with_user(user_chatgpt).message_post(body=res, message_type='comment', subtype_xmlid='mail.mt_comment')

        return rdata

    def _get_chatgpt_response(self, prompt, msg_history):
        ICP = self.env['ir.config_parameter'].sudo()               
        remain_token = self.env.user.remain_token
        token_timestamp = self.env.user.token_timestamp
        current_timestamp = datetime.now(timezone.utc)
        default_token_limit = int(ICP.get_param('vg_azure_openai_integration.token_limit', default=0))
        token_limit = default_token_limit if self.env.user.token_limit == -1 else self.env.user.token_limit

        #reset the remain token if needed
        if(token_timestamp.month != current_timestamp.month or token_limit < remain_token):            
            remain_token = token_limit
            self.env.user.write({'remain_token': remain_token, 'token_timestamp': current_timestamp})            

        if(remain_token <= 0):
            return "You've reached the token limit for this month. Your token limit will reset on the 1st of next month. Contact your administrator if you need additional tokens."
        
        system_message = self.env.user.prompt_message

        msg_history.insert(0,{
            "role": "user",
            "content": system_message
        })

        msg_history.append({
                "role": "system",
                "content": prompt
            })
        
        estimate_token = self.estimate_tokens(msg_history)
        if(remain_token < estimate_token):
            return "You've reached the token limit for this month. Your token limit will reset on the 1st of next month. Contact your administrator if you need additional tokens."
                
        api_key = ICP.get_param('vg_azure_openai_integration.openapi_api_key', default='')
        endpoint = ICP.get_param('vg_azure_openai_integration.endpoint', default='')
        gpt_model = ICP.get_param('vg_azure_openai_integration.chatgpt_model', default='')
        tempreture = self.env.user.tempreture
        top_P = self.env.user.top_p                    
        
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        payload = {
            "messages": msg_history,
            "temperature": float(tempreture),
            "top_p": float(top_P),
            "max_tokens": 4000
        }

        GPT_ENDPOINT = f"{endpoint.strip("/")}/openai/deployments/{gpt_model}/chat/completions?api-version=2024-02-15-preview"            
        try:            
            response = requests.post(GPT_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            chatgpt_response = data["choices"][0]["message"]["content"]
            usage = data['usage']
            remain_token = remain_token - usage['total_tokens']
            self.env.user.write({'remain_token': remain_token, 'token_timestamp': datetime.now(timezone.utc)})
            return chatgpt_response
        except requests.exceptions.RequestException as e:            
            return "There is something wrong with ChatGPT setup. Please contact your administrator"
        except Exception as e:
            return e
        
    def get_channel_messages(self, channel_id, limit):
        if not channel_id:
            return []
        # Retrieve messages related to the specified channel
        messages = self.env['mail.message'].search([            
            ('res_id', '=', channel_id)
        ], order='date desc', limit=limit)

        return messages
    
    def format_for_openai(self, messages, partner_chatgpt_id):        
        formatted_messages = []
        for message in messages[::-1]:               
            role = "user" if message.author_id.id != partner_chatgpt_id else "assistant"
            formatted_messages.append({
                "role": role,
                "content": html2plaintext(str(message.body))
            })        
        return formatted_messages
    
    def estimate_tokens(self, messages):                
        pattern = re.compile(r"\w+|\s+|[^\w\s]")
        total_tokens = 0        
        # Iterate over each message in the list
        for message in messages:
            # Calculate tokens for "role" and "content" separately
            role_tokens = pattern.findall(message['role'])
            content_tokens = pattern.findall(message['content'])            
            # Add the number of tokens for each part
            total_tokens += len(role_tokens) + len(content_tokens)        
        return total_tokens
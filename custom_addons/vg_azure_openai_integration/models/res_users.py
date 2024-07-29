from odoo import models, fields, api
from datetime import datetime, timezone

class ResUsers(models.Model):
    _inherit = 'res.users'

    # New fields
    tempreture = fields.Float(string="Temperature", digits=(1,2), default=0.7)
    past_message_included = fields.Integer(string="Past messages included", default=10)
    top_p = fields.Float(string="Top P", digits=(1,2), default=0.95)
    prompt_message = fields.Text(string="Prompt message", default="You are an AI assistant that helps people find information.")
    token_limit = fields.Integer(string="Token limit (monthly)",required=False, default=-1)
    remain_token = fields.Integer(string="Remaining token", required=False, default=lambda self:self.env['ir.config_parameter'].get_param('vg_azure_openai_integration.token_limit', default=50000))
    token_timestamp = fields.Date(required=False, default=datetime.now(timezone.utc))

    @api.onchange('past_message_included')
    def _onchange_past_message_included(self):
        if self.past_message_included and (self.past_message_included < 0 or self.past_message_included > 10):
            self.past_message_included = 10
            return {
                'warning': {
                    'title': 'Invalid Value',
                    'message': '"Past messages included" value must be between 0 and 10. It has been reset to 10.',
                }
            }
        
    @api.onchange('tempreture')
    def _onchange_tempreture(self):
        if self.tempreture and (self.tempreture < 0 or self.tempreture > 1):
            self.tempreture = 0.7
            return {
                'warning': {
                    'title': 'Invalid Value',
                    'message': '"Temperature" value must be between 0 and 1. It has been reset to 0.7.',
                }
            }
        
    @api.onchange('top_p')
    def _onchange_top_p(self):
        if self.top_p and (self.top_p < 0 or self.top_p > 1):
            self.top_p = 0.95
            return {
                'warning': {
                    'title': 'Invalid Value',
                    'message': '"Top p" value must be between 0 and 1. It has been reset to 0.95.',
                }
            }

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    endpoint = fields.Char(string="Endpoint", config_parameter="vg_azure_openai_integration.endpoint", required=True)
    openapi_api_key = fields.Char(string="API Key", config_parameter="vg_azure_openai_integration.openapi_api_key", required=True)
    chatgpt_model = fields.Char(string="Deployment name", config_parameter="vg_azure_openai_integration.chatgpt_model", required=True)
    token_limit = fields.Integer(string="Default token linit", config_parameter="vg_azure_openai_integration.token_limit", required=True, default=50000)    
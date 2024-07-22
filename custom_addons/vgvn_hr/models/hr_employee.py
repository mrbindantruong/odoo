from odoo import fields, models, api

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    tax_number = fields.Char(string="Tax Number", store=True, readonly=False)

    # @api.onchange('country_id')
    # def _onchange_country_id(self):        
    #     if not (self.country_of_birth):
    #         self.country_of_birth = self.country_id

    @api.model
    def _get_default_country(self):
        # country = self.env['res.country'].search([('code', '=', 'VN')], limit=1)
        return self.env.company.country_id
    country_id = fields.Many2one('res.country', 'Nationality (Country)', groups="hr.group_hr_user", tracking=True, default=_get_default_country)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="hr.group_hr_user", tracking=True, default=_get_default_country)
    
from odoo import models, fields, api,_
from odoo.exceptions import Warning, ValidationError


class ClientRequest(models.Model):
    _name = 'client.request'
    _rec_name = 'name'
    _order = "id desc"

    name = fields.Many2one('res.partner', string='Customer', required=True)
    phone = fields.Char(string='Contact Number', required=True)
    address = fields.Char(string='Address')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    description_of_matter = fields.Text(string='Description Of Matter')
    lawyer = fields.Many2one("hr.employee", string="Lawyer", required=True)
    acess_name = fields.Char()
    payment_type = fields.Char(string='Payment Type')
    payment_amount = fields.Float(string='Payment Amount')
    state = fields.Selection([('new', 'New'), ('request', 'Request'), ('approved', 'Approved'),
                              ('rejected', 'Rejected')], default='new')
    matter_name = fields.Char(string="Matter Name", required=True)
    matter_type_value = fields.Many2one("matter.type", string="Matter Type", required=True)
    description_of_matter = fields.Text("Description")
    payment_type = fields.Boolean("Payment Type:Trials")

    @api.multi
    def action_request(self):
        for rec in self:
            rec.state = "request"

    @api.multi
    def action_approve(self):
        self.env['res.partner'].create({
            'name': self.name.name,
            'street': self.address,
            'phone': self.phone,
            'email': self.email,
        })
        self.env['matters.details'].create({
            'client': self.name.name,
            'category_of_matter': self.matter_name,
            'lawyer': self.lawyer.name,
            'type_of_matter': self.matter_type_value.matter_name,
        })
        self.state = 'approved'

    @api.multi
    def action_reject(self):
        for rec in self:
            rec.state = "rejected"





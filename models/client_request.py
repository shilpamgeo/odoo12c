from odoo import models, fields, api,_
from odoo.exceptions import Warning, ValidationError


class ClientConfirm(models.Model):
    _name = 'client.confirm'

    name = fields.Char(string='Customer', required=True)


class ClientRequest(models.Model):
    _name = 'client.request'
    _rec_name = 'name'
    _order = "id desc"

    name = fields.Many2one('client.confirm', string='Customer', required=True)
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

    # @api.multi
    # @api.constrains('phone')
    # def check_phone_number(self):
    #     for rec in self:
    #         if rec.phone and len(rec.phone) != 10:
    #             raise ValidationError(_('Contact number is Invalid'))
    #         return True

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
        })
        self.state = 'approved'

    @api.multi
    def action_reject(self):
        for rec in self:
            rec.state = "rejected"

    # @api.multi
    # def action_payment(self):
    #
    #     invoice = self.env['account.invoice'].create({
    #         'partner_id': self.name.id,
    #         'payment_term_id': self.matter_type_value.id,
    #         'invoice_line_ids': [(0, 0, {
    #             'name': self.matter_type_value.id,
    #             'product_id': 1,
    #             'quantity': 1,
    #             'price_unit': self.matter_type_value.matter_amount,
    #             'account_id': 12,
    #         })]
    #     })
    #     self.state = 'paid'
    #     return invoice





from odoo import models,fields, api, _


class MatterDetails(models.Model):
    _name = 'matter.details'
    _rec_name = 'type_of_matter'

    open_date = fields.Date(string='Open Date')
    client = fields.Many2one('client.request')
    lawyer = fields.Many2one(string="Lawyer", related="client.lawyer")
    type_of_matter = fields.Many2one('matter.type', string='Type Of Matter', required=True)
    category_of_matter = fields.Char(string='Category Of Matter')
    payment_type = fields.Char(string='Payment Type')
    close_date = fields.Date(string='Close Date')
    matter = fields.Char(string='Matter')
    judge = fields.Char(string="Judge")
    firm = fields.Char(string="Firm")
    number = fields.Char(string="Number")
    client_name = fields.Many2one(string="Name", readonly=True)
    client_no = fields.Char(string="Contact Number", readonly=True)
    client_address = fields.Char(string="Address", readonly=True)
    client_email = fields.Char(string="Email", readonly=True)
    owner = fields.Char(string="Owner Name")
    upload = fields.Binary(string="Upload")
    description = fields.Text()
    activity = fields.Text()
    time_spent = fields.Datetime()
    time_invoiced = fields.Datetime()
    rate = fields.Float(string='Rate (%)', default=0.00)
    Amount = fields.Float(string='Amount', default=0.00)
    unit_measure = fields.Float(string="Unit Of Measure", default=0.00)
    name_seq = fields.Char(string="Number", readonly=True, copy=False, default=_('New'))

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('matter.details')
        return super(MatterDetails, self).create(vals)

    @api.multi
    def action_payment(self):

        invoice = self.env['account.invoice'].create({
            'partner_id': self.client.id,
            'payment_term_id': self.type_of_matter.id,
            'invoice_line_ids': [(0, 0, {
                'name': self.type_of_matter.id,
                'product_id': 1,
                'quantity': 1,
                'price_unit': self.type_of_matter.matter_amount,
                'account_id': 12,
            })]
        })
        return invoice

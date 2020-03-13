from odoo import models,fields, api, _


class MatterDetails(models.Model):
    _name = 'matters.details'

    open_date = fields.Date(string='Open Date')
    client = fields.Many2one('client.request', string='Customer', required=True,  domain=[('state', '=', 'approved')])
    lawyer = fields.Char(string="Lawyer", readonly=True)
    type_of_matter = fields.Many2one('matter.type', string='Type Of Matter')
    category_of_matter = fields.Char(string='Category Of Matter', required=True)
    payment_type = fields.Char(string='Payment Type')
    close_date = fields.Date(string='Close Date')
    matter = fields.Char(string='Matter')
    judge = fields.Char(string="Judge")
    firm = fields.Char(string="Firm")
    number = fields.Char(string="Number")
    matter_id = fields.One2many('matters.data', 'matter_id_inverse', string="Matter")
    matter_doc = fields.One2many('matter.documents', 'matter_documents_inverse')
    matter_time = fields.One2many('matter.time', 'matter_time_inverse')
    matter_date = fields.One2many('matter.date', 'matter_date_inverse')

    @api.multi
    def action_payment(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.client,
            'payment_term_id': self.type_of_matter.id,
            'invoice_line_ids': [(0, 0, {
                'name': self.type_of_matter.id,
                'product_id': 1,
                'quantity': 1,
                'price_unit': 1000,
                'account_id': 12,
            })]
        })
        return invoice


class MatterData(models.Model):
    _name = 'matters.data'

    client_name = fields.Char(string="Name")
    client_no = fields.Char(string="Contact Number")
    client_address = fields.Char(string="Address")
    client_email = fields.Char(string="Email")
    matter_id_inverse = fields.Many2one('matters.details')


class Matterdocuments(models.Model):
    _name = 'matter.documents'

    owner = fields.Char(string="Owner Name")
    upload = fields.Binary(string="Upload")
    description = fields.Text()
    activity = fields.Text()
    matter_documents_inverse = fields.Many2one('matters.details')


class MatterTime(models.Model):
    _name = 'matter.time'

    time_spent = fields.Datetime()
    time_invoiced = fields.Datetime()
    rate = fields.Float(string='Rate (%)', default=0.00)
    Amount = fields.Float(string='Amount', default=0.00)
    unit_measure = fields.Float(string="Unit Of Measure", default=0.00)
    matter_time_inverse = fields.Many2one('matters.details')


class MatterDate(models.Model):
    _name = 'matter.date'

    open_date = fields.Date(string='Open Date')
    close_date = fields.Date(string='Close Date')
    matter_date_inverse = fields.Many2one('matters.details')
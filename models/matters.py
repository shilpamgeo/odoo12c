from odoo import models,fields, api, _


class MatterDetails(models.Model):
    _name = 'matters.details'
    _rec_name = 'client'

    open_date = fields.Date(string='Open Date')
    client = fields.Char(string='Customer', domain=[('state', '=', 'in_progress')])
    lawyer = fields.Char(string="Lawyer", domain=[('state', '=', 'in_progress')])
    type_of_matter = fields.Char(string='Type Of Matter', domain=[('state', '=', 'in_progress')])
    category_of_matter = fields.Char(string='Category Of Matter', required=True, domain=[('state', '=', 'in_progress')])
    close_date = fields.Date(string='Close Date')
    matter = fields.Char(string='Matter')
    judge = fields.Char(string="Judge")
    number = fields.Char(string="Number")
    # matter_id = fields.One2many('matters.data', 'matter_id_inverse', string="Matter")
    # matter_doc = fields.One2many('matter.documents', 'matter_documents_inverse')
    matter_time = fields.One2many('matter.time', 'matter_time_inverse')
    matter_date = fields.One2many('matter.date', 'matter_date_inverse')
    upload = fields.Binary(string="Upload")
    description = fields.Text()
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('payment', 'Payment'),
                                     ('in_progress', 'In Progress'), ('won', 'Won'), ('loss', 'Loss')], default='draft')
    act_data = fields.One2many('act.data', 'act_data_inverse')
    matter_trial = fields.One2many('matter.trial', 'matter_trial_inverse')

    @api.multi
    def action_approved(self):
        for rec in self:
            rec.state = "approved"

    @api.multi
    def action_progress(self):
        for rec in self:
            rec.state = "in_progress"

    @api.multi
    def action_won(self):
        for rec in self:
            rec.state = "won"

    @api.multi
    def action_loss(self):
        for rec in self:
            rec.state = "Loss"


class MatterTrail(models.Model):
    _name = 'matter.trial'

    matter_trial_inverse = fields.Many2one('matters.details')
    trial_name = fields.Char('Trial Name')
    trial_matter = fields.Char(related='matter_trial_inverse.type_of_matter')
    trial_date = fields.Date(required=True)
    matter_state = fields.Selection(related="matter_trial_inverse.state")

    @api.multi
    def action_payment(self):
        for rec in self:
            rec.matter_trial_inverse.state = "payment"
        invoice = self.env['account.invoice'].create({
            'partner_id': self.matter_trial_inverse.id,
            # 'payment_term_id': self.trial_matter,
            'invoice_line_ids': [(0, 0, {
                'name': self.trial_matter,
                'product_id': 1,
                'quantity': 1,
                'price_unit': 1000,
                'account_id': 12,
            })]
        })
        return invoice


class ActData(models.Model):
    _name = 'act.data'

    act_data_inverse = fields.Many2one('matters.details')
    act_no = fields.Char(string="Section Number")
    act_name = fields.Char(string="Act Name")
    case_category = fields.Char(string="Case Category", related="act_data_inverse.type_of_matter")


# class MatterData(models.Model):
#     _name = 'matters.data'
#
#     client_name = fields.Char(string="Name", related="matter_id_inverse.client")
#     client_no = fields.Char(string="Contact Number")
#     client_address = fields.Char(string="Address")
#     client_email = fields.Char(string="Email")
#     matter_id_inverse = fields.Many2one('matters.details')


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
# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api,_
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,Warning


class LawyerRecords(models.Model):
    _name = 'case.case'
    _description = 'Case Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    case_category = fields.Selection([('f', 'Family Cases'), ('c', 'Criminal Cases'), ('b', 'Traffic Cases'),
                                      ('j', 'Civil Cases')], string='Category of Case', required=True)
    case_details = fields.Text(string='Details Of Case (SECTION)', required=True)
    case_lawyer = fields.Many2one('hr.employee', string=" Lawyer", required=True, track_visibility='onchange')
    case_client = fields.Many2one('res.partner', string='Client', required=True, track_visibility='onchange',
                                  domain=[['customer', '=', 1]])
    case_court = fields.Many2one('court.court', string='Court', required=True)
    case_next = fields.Date(string='Sitting Date', required=True)
    case_menu = fields.One2many('case.case.line', 'connect_id', string="Sitting")
    case_note = fields.One2many('notes.notes', 'connect_id1', string="Internal Notes")
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    obj_attachment = fields.Integer(string='attachment', compute='attachments1')

    state = fields.Selection([('draft', 'Draft'),
                              ('invoiced', 'Invoiced'),
                              ('completed', 'Completed')], default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('case.case')
        return super(LawyerRecords, self).create(vals)

    @api.one
    def attachments1(self):
        obj_attachment = self.env['ir.attachment']
        for record in self:
            record.attachment_count = 0
        attachment_ids = obj_attachment.search([('res_model', '=', 'case.case'), ('res_id', '=', record.id)])
        if attachment_ids:
            record.obj_attachment = len(attachment_ids)

    @api.multi
    def count_attachments(self):
        self.ensure_one()
        domain = [('res_model', '=', 'case.case'), ('res_id', 'in', self.ids)]
        return {

            'name': 'ir.attachment tree',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context':  "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.multi
    def make_payment(self):
        self.ensure_one()
        self.sudo().write({
            'state': 'invoiced'
        })

        ctx = {

            'default_corres_customer': self.case_client.id, 'default_employee_id': self.case_lawyer.id
        }
        return {
            'name': 'my.form',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': ctx,
        }

    @api.multi
    def add_sittings(self):
        self.ensure_one()
        self.sudo().write({
            'state': 'draft'
        })

    @api.multi
    def mark_done(self):
        self.ensure_one()
        self.sudo().write({
            'state': 'completed'
        })


class LawyerRecordsline(models.Model):
    _name = 'case.case.line'
    case_description = fields.Text(string='Description', required=True)
    connect_id = fields.Many2one('case.case', string='Description', required=True)
    case_date = fields.Date(string='Date', required=True)


class InternalNotes(models.Model):
    _name = 'notes.notes'
    case_internal = fields.Text(string='Internal Notes', required=True)
    connect_id1 = fields.Many2one('case.case', string='Internal Notes', required=True)


class Court(models.Model):
    _name = 'court.court'
    _rec_name = 'case_court'
    _order = "id desc"

    case_court = fields.Text(string='Court', required=True)


class PartnerForm(models.Model):

    _inherit = 'res.partner'
    _order = "id desc"

    # customer_val = fields.Many2one('client.request', domain="[('state','=','approved')]")
    customer = fields.Boolean(string='Is a Client', default=True)
    client_request_count = fields.Integer(compute='set_client_request_count', string='Client Request')
    case_count = fields.Integer(compute="get_case_count")

    @api.multi
    def set_client_request_count(self):
        for line in self:
            line.client_request_count = +1

    @api.multi
    def client_request_matter(self):
        return {
            'name': _('Matter'),
            'domain': [('name', '=', self.id), ('state', '=', 'approved')],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'client.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    def get_case_count(self):
        count = self.env['client.request'].search_count([('name', '=', self.id), ('state', '=', 'approved')])
        self.case_count = count


class Payslip(models.Model):

    _inherit = 'hr.payslip'

    corres_customer = fields.Many2one('res.partner', string='Customer')


class ContractWage(models.Model):
    _name = 'contract.wage'

    case_name = fields.Many2one('matter.type', 'Case Name')
    per_hour = fields.Integer('Wage per hour')
    working_hours = fields.Integer()
    day_sal = fields.Integer()
    month_sal = fields.Integer()
    date = fields.Date()
    contract_inverse = fields.Many2one('hr.contract')

    @api.onchange('per_hour', 'working_hours')
    def perday_salary(self):
        for record in self:
            if record.per_hour and record.working_hours:
                record.day_sal = record.per_hour * record.working_hours


class Contract(models.Model):

    _inherit = 'hr.contract'

    contract_id = fields.One2many('contract.wage', 'contract_inverse')
    amount_total = fields.Char(compute="total_salary")
    date_field = fields.Date("Date")

    @api.multi
    @api.constrains('date_field', 'contract_id.date')
    def calc_date(self):
        month_value = self.date_field.month
        print(month_value)
        for record in self:
            for line in record.contract_id:
                month_value2 = line.date.month
                if month_value != month_value2:
                    raise ValidationError(_('create payment on same month'))

    @api.multi
    @api.depends('contract_id', 'contract_id.day_sal')
    def total_salary(self):
        for rec in self:
            sum = 0
            for line in rec.contract_id:
                sum += line.day_sal
            rec.amount_total = sum


class Lawyers(models.Model):
    _inherit = 'hr.employee'

    emp_id = fields.Many2one('hr.contract')

    @api.multi
    def action_report(self):
        # datas = {'emp_id': self.emp_id}
        return self.env.ref('legal_case_management.action_report_lawyer_data').report_action(self)


# class LawyerReport(models.Model):
#     _name = 'report.legal_case_management.lawyer_report_template'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         x = data['emp_id']
#         return {
#             'doc_ids': docids,
#             'x':x
#         }















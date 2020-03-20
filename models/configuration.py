from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,Warning


class UniversityType(models.Model):
    _name = 'university.type'
    _rec_name = 'university_name'

    university_name = fields.Char(string="University Name")
    year = fields.Date(string="Year of Graduation")


class ServiceTypes(models.Model):
    _name = 'lawyer.master'

    lawyer_name = fields.Many2one('hr.employee', string="Lawyer Name")
    date_id = fields.Date("Date", required=True)
    emp_id = fields.Char("Employee Id", required=True)
    month_salary = fields.Char(compute="total_sal", string="Total Salary")
    state = fields.Selection([('request', 'Request'), ('paid', 'Paid')], default='request')
    lawyer_master_data = fields.One2many('lawyer.service', 'lawyer_master_inverse')

    @api.multi
    @api.constrains('date_id', 'lawyer_master_data.date_val')
    def calc_date(self):
        month_value = self.date_id.month
        print(month_value)
        for record in self:
            for line in record.lawyer_master_data:
                month_value2 = line.date_val.month
                if month_value != month_value2:
                    raise ValidationError(_('create payment on same month'))

    @api.multi
    @api.depends('lawyer_master_data', 'lawyer_master_data.day_sal_data')
    def total_sal(self):
        for rec in self:
            sum = 0
            for line in rec.lawyer_master_data:
                sum += line.day_sal_data
            rec.month_salary = sum

    # @api.multi
    # @api.depends('date_id')
    # def total_sal(self):
    #     if self.date_id:
    #         month_value = self.date_id.month
    #         get_data = self.env['hr.contract'].search([])
    #         for record in get_data:
    #             if record.employee_id:
    #                 if record.employee_id.id == self.lawyer_name.id:
    #                     if record.date_field:
    #                         month_value1 = record.date_field.month
    #                         if month_value != month_value1:
    #                             raise ValidationError(_('Contract is not generated for this month'))
    #                         else:
    #                             self.month_salary = record.amount_total

    @api.multi
    def action_paid(self):
        print("entered")
        contract = self.env['hr.contract'].create({
            'name': self.emp_id,
            'employee_id': self.lawyer_name.id,
            'wage': self.month_salary,
            'amount_total': self.month_salary,
            'date_field': self.date_id,
            'type_id': 1,
            'date_start': self.date_id,
            'resource_calender_id': 40,
        })
        print("entered2")
        payslip = self.env['hr.payslip'].create({
            'employee_id': self.lawyer_name.id,
            'date_from': self.date_id,
            'date_to': datetime.now(),
            'contract_id': contract.id,
            'struct_id': 1,
            'line_ids': [(0, 0, {
                'name': self.lawyer_name.name,
                'code': self.emp_id,
                'category_id': 1,
                'quantity': 1,
                'rate': 1,
                'salary_rule_id': self.env['hr.salary.rule'].search([('name', '=', 'Basic Salary')]).id,
                'amount': self.month_salary,
            })]
        })
        self.state = 'paid'
        return contract, payslip


class LawyerService(models.Model):
    _name = 'lawyer.service'

    case_name_data = fields.Many2one('matter.type', string='Case Name')
    per_hour_data = fields.Integer(string="Wage per hour")
    working_hours_data = fields.Integer(string="Working Hours")
    day_sal_data = fields.Integer(string="Per day Salary")
    date_val = fields.Date(string="Date")
    lawyer_master_inverse = fields.Many2one('lawyer.master')

    @api.onchange('per_hour_data', 'working_hours_data')
    def perday_salary(self):
        for record in self:
            if record.per_hour_data and record.working_hours_data:
                record.day_sal_data = record.per_hour_data * record.working_hours_data


class MatterTypes(models.Model):
    _name = 'matter.type'
    _rec_name = 'matter_name'

    matter_section = fields.Char(string="Section no")
    matter_name = fields.Char(string="Matter Name")




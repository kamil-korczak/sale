import datetime
from odoo import api, fields, models


class SaleOrderArchive(models.Model):
    _name = "sale.order.archive"
    _description = "Sales Order Archive"


    name = fields.Char(string="Order name/symbol", required=True, index=True)
    order_create_date = fields.Datetime(string='Order create date', readonly=True, index=True, 
        help="Date on which sales order is created.")
    customer_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True, required=True, index=True)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', index=True )
    amount_total = fields.Monetary(string='Total')
    currency_id = fields.Many2one('res.currency', string="Order Currency")
    order_line = fields.Integer(string="Count of Order Lines")

    def move_orders_to_archive(self):
        '''
        Move orders older than 30 days with status *sale* or *cancel* to Archive.
        '''
        orders = self._search_30_days_old_orders()
        prepared_data_to_copy = self._prepare_data_to_copy(orders)
        created = self._create_orders_archive(prepared_data_to_copy)

        if created:
            self._delete_orders(orders)

    def _search_30_days_old_orders(self):
        date_30_days_ago = datetime.datetime.now() + datetime.timedelta(days=-30)
        search_args = [
            '|', 
            ('state', '=', 'draft'), 
            ('state', '=', 'cancel'), 
            ('date_order', '<', date_30_days_ago)
        ]
        return self.env['sale.order'].search(args=search_args, order='id')
            
    def _prepare_data_to_copy(self, orders):
        data = []
        for order in orders:
            data.append({
                    'name': order.name,
                    'order_create_date': order.create_date,
                    'customer_id': order.partner_id.id,
                    'salesperson_id': order.user_id.id,
                    'amount_total': order.amount_total,
                    'currency_id': order.currency_id.id,
                    'order_line': len(order.order_line),
            })
        return data

    @api.model_create_multi
    def _create_orders_archive(self, data):
        return self.env['sale.order.archive'].create(data)

    def _delete_orders(self, orders):
        return orders.unlink()

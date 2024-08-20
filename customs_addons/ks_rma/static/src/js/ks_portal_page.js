odoo.define('ks_rma.ks_portal_page', function (require){
   var ajax = require('web.ajax');
   var core = require('web.core');
   var Dialog = require('web.Dialog');

   var _t = core._t;

   $(document).ready(function(){

      $('.ks_open_rma_form').on("click",function(e){
            $("#ks_open_sale_rma_form").modal('show');
      });

      $('#ks_open_sale_rma_form #ks_is_return').on("change",function(e){
        if($(e.currentTarget).prop('checked')){
              $('.ks_return_qty_tr').removeClass('d-none');
              $('.ks_return_qty_td').removeClass('d-none');
              $('.return').removeClass('d-none');
        }
        else{
              $('.ks_return_qty_td').addClass('d-none');
               $('.ks_return_qty_tr').addClass('d-none');
               $('.return').addClass('d-none');
        }
      })

      $('#ks_open_sale_rma_form #ks_is_refund').on("change",function(e){
        if($(e.currentTarget).prop('checked')){
              $('.ks_refund_qty_tr').removeClass('d-none');
              $('.ks_refund_qty_td').removeClass('d-none');
               $('.refund').removeClass('d-none');
        }
        else{
              $('.ks_refund_qty_td').addClass('d-none');
               $('.ks_refund_qty_tr').addClass('d-none');
               $('.refund').addClass('d-none');
        }
      })

      $('#ks_open_sale_rma_form #ks_is_replace').on("change",function(e){
        if($(e.currentTarget).prop('checked')){
              $('.ks_replace_qty_tr').removeClass('d-none');
              $('.ks_replace_qty_td').removeClass('d-none');
               $('.replace').removeClass('d-none');
               $('#ks_is_return').prop('checked',false);
              $('#ks_is_refund').prop('checked',false);
                $('.ks_return_div').addClass('d-none');
                $('.ks_refund_div').addClass('d-none');
                 $('.ks_refund_qty_td').addClass('d-none');
               $('.ks_refund_qty_tr').addClass('d-none');
                 $('.ks_return_qty_td').addClass('d-none');
               $('.ks_return_qty_tr').addClass('d-none');
                $('.refund').addClass('d-none');
                 $('.return').addClass('d-none');
        }
        else{
              $('.ks_refund_qty_td').addClass('d-none');
               $('.ks_refund_qty_tr').addClass('d-none');
               $('.replace').addClass('d-none');
                $('.ks_return_div').removeClass('d-none');
                $('.ks_refund_div').removeClass('d-none');
                $('.ks_replace_qty_tr').addClass('d-none');
              $('.ks_replace_qty_td').addClass('d-none');
        }
      })

      $('.ks_create_rma_button').on("click",function(e){
            if($('#ks_is_return').prop('checked') || $('#ks_is_refund').prop('checked') || $('#ks_is_replace').prop('checked')){
                  var self = this
                  $(e.currentTarget).attr('disabled', 'disabled');
                  self.is_return = $('#ks_is_return').prop('checked');
                  self.is_refund = $('#ks_is_refund').prop('checked');
                  self.is_replace = $('#ks_is_replace').prop('checked');
                  self.ks_notes = $('.ks_rma_notes').val();
                  self.return_reason = parseInt($('.ks_rma_return_reason :selected').attr('id'))
                  self.refund_reason = parseInt($('.ks_rma_refund_reason :selected').attr('id'))
                  self.replace_reason = parseInt($('.ks_rma_replace_reason :selected').attr('id'))
                  self.partner_id = parseInt($('.ks_partner_id').attr('id'));
                  self.picking_id = parseInt($('.ks_picking_id').attr('id'));
                  self.picking_type_id = parseInt($('.ks_picking_type_id').attr('id'));
                  self.return_picking_type_id = parseInt($('.ks_return_picking_type_id').attr('id'));
                  self.order_id = parseInt($('.ks_sale_order_id').attr('id'));
                  self.return_qty = 0
                  self.refund_qty = 0
                  self.replace_qty = 0
                  self.product_detail_dict = {}
                  _.each($('.ks_product_line_row'), function (el) {
                     if ($(el).find('#rma_line_checkbox').prop('checked')){
                         if (self.is_return){
                            self.return_qty = parseInt($(el).find('input.ks_return_qty_value').val());
                          }
                          if (self.is_refund){
                            self.refund_qty = parseInt($(el).find('input.ks_refund_qty_value').val());
                          }
                          if (self.is_replace){
                            self.replace_qty = parseInt($(el).find('input.ks_replace_qty_value').val());
                          }
                          var demand_qty = parseInt($(el).find('#ks_demand_qty').text().trim());
                          var product_id = parseInt($(el).find('.ks_product_id').attr('id'));
                          self.product_detail_dict[product_id] = [demand_qty, self.refund_qty, self.return_qty, self.replace_qty]
                    }
                  })
                  ajax.jsonRpc('/create/rma/request', 'call', {
                        'partner_id': self.partner_id,
                        'is_return': self.is_return,
                        'is_refund': self.is_refund,
                        'is_replace': self.is_replace,
                        'rma_lines': self.product_detail_dict,
                        'sale_order_id': self.order_id,
                        'picking_id': self.picking_id,
                        'picking_type_id': self.picking_type_id,
                        'return_picking_type_id': self.return_picking_type_id,
                        'ks_notes': self.ks_notes,
                        'return_reason': self.return_reason,
                        'refund_reason': self.refund_reason,
                        'replace_reason': self.replace_reason
                  }).then(function(result){
                        if(result.Success){
                            location.reload()
                        }
                        if(result.Error){
                            alert(_t("Error While Creating RMA", result.Error));
                        }
                  });
            }
            else{
                  alert(_t('Select at least one RMA request operation'));
            }
      })
   })
})
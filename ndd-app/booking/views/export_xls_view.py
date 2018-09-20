# -*- coding: utf-8 -*-

import xlwt
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from ..models import Booking
from .utils import StyleXls
from agent_transport.models import AgentTransport
from customer.models import Principal, Shipper


class ExportDataView(TemplateView):

    @login_required(login_url=reverse_lazy('login'))
    def render_export_page(request):
        template_name = 'export.html'
        context = {}
        context['nbar'] = 'export'
        return render(request, template_name, context)

    def export_xls(request):
        if request.method == 'POST':
            month_export = request.POST['month-work-export']
            month_export = datetime.strptime(month_export, '%Y-%m')
            file_month_name = month_export.strftime('%b-%Y')

            style_xls = StyleXls()

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Booking-' + file_month_name + '.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws_booking = wb.add_sheet('Booking')

            # Sheet header
            style = style_xls.header_style()

            columns = ['Time', 'Date', 'Principal', 'Shipper', 'Agent', 'Size', 'Booking', 'TR', 'FM', 'TR', 'Factory', 'TR', 'TR', 'To', 'Container', 'Seal no', \
            'Vessel', 'Port', 'Closing date', 'Closing time', 'Ref.', 'Remark', 'Work ID', 'Pick up', 'Factory', 'Return', 'In', 'Out', 'In', 'Start', 'Finish', 'Out', 'In', 'Out']

            ws_booking.write_merge(0, 0, 26, 27, 'Pick up', style)
            ws_booking.write_merge(0, 0, 28, 31, 'Factory', style)
            ws_booking.write_merge(0, 0, 32, 33, 'Return', style)

            for col_num in range(len(columns)):
                if col_num <= 25 :
                    ws_booking.write_merge(0, 1, col_num, col_num, columns[col_num], style)
                else:
                    ws_booking.write(1, col_num, columns[col_num], style)

            # Sheet body, remaining rows

            rows = Booking.objects.filter((Q(date__month=month_export.month) & Q(date__year=month_export.year))).values_list('time', 'date', 'principal', 'shipper', 'agent', 'size', 'booking_no', 'pickup_tr', 'pickup_from', 'forward_tr', \
            'factory', 'backward_tr', 'return_tr', 'return_to', 'container_no', 'seal_no', 'vessel', 'port', 'closing_date', 'closing_time', 'ref', 'remark', 'work_id', \
            'pickup_date', 'factory_date', 'return_date', 'pickup_in_time', 'pickup_out_time', 'factory_in_time', 'factory_load_start_time', 'factory_load_finish_time', \
            'factory_out_time', 'return_in_time', 'return_out_time', 'nextday', 'cancel').order_by('date', 'work_id')

            row_num = 1
            row_prev = None
            booking_prev = None
            booking_status = True
            for row in rows:
                row = list(row)
                bg_black = False 
                row_num += 1
                if row_prev != None and row_prev != row[1]:
                    style = style_xls.bg_black()
                    ws_booking.write_merge(row_num, row_num, 0, len(row)-3, '', style)
                    row_num += 1
                row_prev = row[1]

                for col_num in range(len(row)-2):
                    style = xlwt.XFStyle()
                    style.borders = style_xls.border_cell()
                    style.alignment = style_xls.align_left()

                    if col_num == 2:
                        try:
                            row[col_num] = Principal.objects.get(pk=row[col_num]).name
                        except Principal.DoesNotExist:
                            row[col_num] = ''

                    if col_num == 3:
                        try:
                            row[col_num] = Shipper.objects.get(pk=row[col_num]).name
                        except Shipper.DoesNotExist:
                            row[col_num] = ''

                    if str(type(row[col_num])) == "<class 'datetime.date'>" :
                        style.num_format_str = 'dd/mm/yy'

                    if row[len(row)-2] == '1' and col_num > 22 and col_num < 26:
                        style.pattern = style_xls.bg_aqua()
                    
                    if booking_prev != row[6]:
                        booking_status = not(booking_status)
                    booking_prev = row[6]

                    if col_num == 6: 
                        if booking_status == True:
                            style.pattern = style_xls.bg_light_orange()
                        else:
                            style.pattern = style_xls.bright_green()

                    if row[len(row)-1] == '1':
                        style.pattern = style_xls.cancel_row()

                    if col_num >= 26 :
                        if row[col_num] != '':
                            date_time = row[col_num].split('//')
                            if date_time[0] == '':
                                date = None
                            else:
                                date = datetime.strptime(date_time[0], "%Y-%m-%d").strftime("%d/%m/%y")
                            time = date_time[1]
                            row[col_num] = date + ' - ' + time

                    ws_booking.write(row_num, col_num, row[col_num], style)


            ws_agent_transport = wb.add_sheet('สายเรือ')

            # Sheet header
            style = style_xls.header_style()

            columns = ['Date', 'Principal', 'Shipper', 'Agent', 'Size', 'Booking', 'TR', 'FM', 'TR', 'TO', 'Container 1', 'Container 2', \
            'Ref.', 'Remark', 'Work ID', 'Pick up', 'Return']

            for col_num in range(len(columns)):
                ws_agent_transport.write(0, col_num, columns[col_num], style)

            # Sheet body, remaining rows
            rows = AgentTransport.objects.filter((Q(date__month=month_export.month) & Q(date__year=month_export.year))).values_list('date', 'principal', 'shipper', 'agent', 'size', 'booking_no', 'pickup_tr', 'pickup_from','return_tr', 'return_to', \
            'container_1', 'container_2', 'ref', 'remark', 'work_id', 'pickup_date', 'return_date', 'cancel').order_by('date', 'work_id')

            row_num = 0
            row_prev = None
            booking_prev = None
            booking_status = True
            for row in rows:
                row = list(row)
                bg_black = False 
                row_num += 1
                if row_prev != None and row_prev != row[0]:
                    style = style_xls.bg_black()
                    ws_agent_transport.write_merge(row_num, row_num, 0, len(row)-2, '', style)
                    row_num += 1
                row_prev = row[0]

                for col_num in range(len(row)-1):
                    style = xlwt.XFStyle()
                    style.borders = style_xls.border_cell()
                    style.alignment = style_xls.align_left()

                    if col_num == 1:
                        try:
                            row[col_num] = Principal.objects.get(pk=row[col_num]).name
                        except Principal.DoesNotExist:
                            row[col_num] = ''

                    if col_num == 2:
                        try:
                            row[col_num] = Shipper.objects.get(pk=row[col_num]).name
                        except Shipper.DoesNotExist:
                            row[col_num] = ''

                    if str(type(row[col_num])) == "<class 'datetime.date'>" :
                        style.num_format_str = 'dd/mm/yy'

                    if booking_prev != row[5]:
                        booking_status = not(booking_status)
                    booking_prev = row[5]

                    if col_num == 5: 
                        if booking_status == True:
                            style.pattern = style_xls.bg_light_orange()
                        else:
                            style.pattern = style_xls.bright_green()

                    if row[len(row)-1] == '1':
                        style.pattern = style_xls.cancel_row()

                    ws_agent_transport.write(row_num, col_num, row[col_num], style)

            wb.save(response)
            return response
        return False


# -*- coding: utf-8 -*-

import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from ..forms import BookingAddForm
from ..models import Booking
from customer.models import Principal, Shipper


class BookingAddView(TemplateView):

    @login_required(login_url=reverse_lazy('login'))
    def render_add_booking_page(request):
        add_booking = BookingAddView()
        template_name = 'booking/booking_add.html'
        context = {}
        context['form'] = BookingAddForm()
        context['principals'] = Principal.objects.filter(Q(work_type='normal') & Q(cancel=0)).order_by('name')
        context['nbar'] = 'booking-table'

        if request.method == 'POST':
            context = add_booking.create_context(request.POST)
            
        return render(request, template_name, context)

    def create_context(self, req):
        context = {}
        context['principals'] = Principal.objects.filter(Q(work_type='normal') & Q(cancel=0)).order_by('name')
        context['nbar'] = 'booking-table'
        if 'principal' in req:
            context['principal'] = req.get('principal')
            if context['principal']:
                context['shippers'] = Shipper.objects.filter(Q(principal=context['principal']) & Q(cancel=0)).order_by('name')
                context['principal_name'] = Principal.objects.get(pk=context['principal']).name
            else:
                context['shippers'] = []

            req._mutable = True
            context['time_list'] = req.getlist('time')
            context['size_list'] = req.getlist('size')
            context['quantity_list'] = req.getlist('quantity')
            context['date_list'] = req.getlist('date')
            context['zip'] = zip(context['time_list'], context['size_list'], context['quantity_list'], context['date_list'])

            req.update({'time':'', 'size':'', 'quantity':'', 'date':''})
            context['form'] = BookingAddForm(req)
        return context

    @login_required(login_url=reverse_lazy('login'))
    def save_data_booking(request):
        add_booking = BookingAddView()
        if request.method == 'POST':
            form = BookingAddForm(request.POST)
            if form.is_valid():
                principal = request.POST['principal']
                shipper = request.POST['shipper']
                agent = request.POST['agent']
                booking_no = request.POST['booking_no']
                time_list = request.POST.getlist('time')
                size_list = request.POST.getlist('size')
                quantity_list = request.POST.getlist('quantity')
                date_list = request.POST.getlist('date')
                pickup_from = request.POST['pickup_from']
                factory = request.POST['factory']
                return_to = request.POST['return_to']
                vessel = request.POST['vessel']
                port = request.POST['port']
                closing_date = request.POST['closing_date']
                closing_time = request.POST['closing_time']
                ref = request.POST['ref']
                remark = request.POST['remark']
                address = request.POST['address']

                nextday = request.POST['nextday']

                if not closing_date:
                    closing_date = None
                if address == 'other':
                    address_other = request.POST['address_other']

                container = zip(time_list, size_list, quantity_list, date_list)
                for time, size, quantity, date in container:
                    add_booking.work_id_after_add(date, shipper, int(quantity))
                    
                    if nextday == '1':
                        return_date = request.POST['return_date']
                    else:
                        return_date = date

                    for i in range(int(quantity)):
                        work_id, work_number = add_booking.run_work_id(date, shipper)
                        data = {
                            'principal': Principal.objects.get(pk=principal),
                            'shipper': Shipper.objects.get(pk=shipper),
                            'agent': re.sub(' +', ' ', agent.strip()),
                            'booking_no': re.sub(' +', ' ', booking_no.strip()),
                            'time': re.sub(' +', ' ', time.strip()),
                            'size': re.sub(' +', ' ', size.strip()),
                            'date': date,
                            'pickup_from': re.sub(' +', ' ', pickup_from.strip()),
                            'factory': re.sub(' +', ' ', factory.strip()),
                            'return_to': re.sub(' +', ' ', return_to.strip()),
                            'vessel': re.sub(' +', ' ', vessel.strip()),
                            'port': re.sub(' +', ' ', port.strip()),
                            'closing_date': closing_date,
                            'closing_time': closing_time,
                            'ref': re.sub(' +', ' ', ref.strip()),
                            'remark': re.sub(' +', ' ', remark.strip()),
                            'work_id': work_id,
                            'work_number': work_number,
                            'nextday': nextday,
                            'pickup_date': date,
                            'factory_date': date,
                            'return_date': return_date,
                            'address': address
                        }
                        if address == 'other':
                            data['address_other'] = address_other

                        booking = Booking(**data)
                        booking.save()
                 
                messages.success(request, "Added Booking.")
                return redirect('booking-table')
            messages.error(request, "Form not validate.")
        return redirect('booking-add')

    def run_work_id(self, date, shipper):
        work = Booking.objects.filter(date=date).aggregate(Max('work_number'))
        if work['work_number__max'] == None:
            work_number = 0
        else:
            work_shipper = Booking.objects.filter(date=date, shipper=shipper).aggregate(Max('work_number'))
            if work_shipper['work_number__max'] == None:
                work_number = work['work_number__max'] + 1
            else:
                work_number = work_shipper['work_number__max'] + 1

        work = str("{:03d}".format(work_number))
        date = datetime.strptime(date, "%Y-%m-%d")
        work_id = date.strftime('%d%m%y') + work
        return work_id, work_number

    def work_id_after_add(self, date, shipper, quantity):
        max_work = Booking.objects.filter(date=date, shipper=shipper).aggregate(Max('work_number'))
        if max_work['work_number__max']:
            work_gt = Booking.objects.filter(date=date, work_number__gt=max_work['work_number__max'])
            for work in work_gt:               
                new_work_number = work.work_number + quantity
                work_str = str("{:03d}".format(new_work_number))
                date = datetime.strptime(date, "%Y-%m-%d")
                work_id = date.strftime('%d%m%y') + work_str

                booking = Booking.objects.get(pk=work.pk)
                booking.work_id = work_id
                booking.work_number = new_work_number
                booking.save()
        return

            


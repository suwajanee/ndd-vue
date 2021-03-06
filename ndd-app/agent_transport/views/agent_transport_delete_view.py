from django.views.generic import TemplateView
from ..models import AgentTransport
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class AgentTransportDeleteView(TemplateView):

    @login_required(login_url=reverse_lazy('login'))
    def delete_data_agent_transport(request, pk):
        agent_transport = AgentTransport.objects.get(pk=pk)
        agent_transport.delete()

        if request.method == "GET":
            filter_by = request.GET.get("filter_by")
            date_filter = request.GET.get("date_filter")
            if not date_filter:
                return redirect(reverse('agent-transport-table'))
            else:
                return redirect(reverse('agent-transport-table') + '?filter_by=' + filter_by + '&date_filter=' + date_filter)


    @login_required(login_url=reverse_lazy('login'))
    def delete_multiple_data_agent_transport(request):
        
        if request.method == "POST":
            pk_list = request.POST.getlist('pk')
            filter_by = request.POST['filter_by']
            date_filter = request.POST['date_filter']

            for pk in pk_list:
                agent_transport = AgentTransport.objects.get(pk=pk)
                agent_transport.delete()

            if not date_filter:
                return redirect(reverse('agent-transport-table'))
            else:
                return redirect(reverse('agent-transport-table') + '?filter_by=' + filter_by + '&date_filter=' + date_filter)
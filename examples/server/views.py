# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.conf import settings
from server.forms import SubscriptionForm, SubscriptionFormWithNgModel


class NgFormValidationView(TemplateView):
    template_name = 'subscribe-form.html'

    def get_context_data(self, **kwargs):
        context = super(NgFormValidationView, self).get_context_data(**kwargs)
        context.update(with_ws4redis=hasattr(settings, 'WEBSOCKET_URL'))
        return context

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = SubscriptionForm()
        form.fields['height'].widget.attrs['step'] = 0.05  # Ugly hack to set step size
        context.update(form=form)
        return self.render_to_response(context)

    def post(self, request, **kwargs):
        post_data = request.POST.copy()
        # post_data.update({'email': 'invalidXmail'})  # intentionally invalidate form data
        form = SubscriptionForm(post_data)
        if form.is_valid():
            return redirect('form_data_valid')
        form.fields['height'].widget.attrs['step'] = 0.05  # Ugly hack to set step size
        context = self.get_context_data(**kwargs)
        context.update(form=form)
        return self.render_to_response(context)


class NgFormValidationViewWithNgModel(NgFormValidationView):
    template_name = 'subscribe-form-with-model.html'
    form = SubscriptionFormWithNgModel(scope_prefix='subscribe_data')


class Ng3WayDataBindingView(NgFormValidationViewWithNgModel):
    template_name = 'three-way-data-binding.html'


class NgFormDataValidView(TemplateView):
    template_name = 'form-data-valid.html'

    def get_context_data(self, **kwargs):
        context = super(NgFormDataValidView, self).get_context_data(**kwargs)
        context.update(with_ws4redis=hasattr(settings, 'WEBSOCKET_URL'))
        return context

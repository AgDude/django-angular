# -*- coding: utf-8 -*-
from django.forms.util import ErrorDict
from django.utils.html import format_html
from djangular.forms.angular_base import NgFormBaseMixin, SafeTuple


class NgModelFormMixin(NgFormBaseMixin):
    """
    Add this NgModelFormMixin to every class derived from forms.Form, if
    you want to manage that form through an Angular controller.
    It adds attributes ng-model, and optionally ng-change, ng-class and ng-style
    to each of your input fields.
    If form validation fails, the ErrorDict is rewritten in a way, so that the
    Angular controller can access the error strings using the same key values as
    for its models.
    """

    def __init__(self, data=None, *args, **kwargs):
        self.scope_prefix = kwargs.pop('scope_prefix', getattr(self, 'scope_prefix', None))
        self.ng_directives = {}
        for key in list(kwargs.keys()):
            if key.startswith('ng_'):
                fmtstr = kwargs.pop(key)
                self.ng_directives[key.replace('_', '-')] = fmtstr
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'ng_models'):
            if not isinstance(getattr(self.Meta, 'ng_models'), list):
                raise TypeError('Meta.ng_model is not of type list')
        elif 'ng-model' not in self.ng_directives:
            self.ng_directives['ng-model'] = '%(model)s'
        self.prefix = kwargs.get('prefix')
        if self.prefix and data:
            data = dict((self.add_prefix(name), value) for name, value in data.get(self.prefix).items())
        super(NgModelFormMixin, self).__init__(data, *args, **kwargs)
        if self.scope_prefix == self.form_name:
            raise ValueError("The form's name may not be identical with its scope_prefix")

    def _post_clean(self):
        """
        Rewrite the error dictionary, so that its keys correspond to the model fields.
        """
        super(NgModelFormMixin, self)._post_clean()
        if self._errors and self.prefix:
            self._errors = ErrorDict((self.add_prefix(name), value) for name, value in self._errors.items())

    def get_initial_data(self):
        """
        Return a dictionary specifying the defaults for this form. This dictionary can be used to
        inject the initial values for an Angular controller using the directive:
        ``ng-init={{ thisform.get_initial_data|js|safe }}``.
        """
        data = {}
        ng_models = hasattr(self, 'Meta') and getattr(self.Meta, 'ng_models', []) or []
        for name, field in self.fields.items():
            if 'ng-model' in self.ng_directives or name in ng_models:
                data[name] = self.initial and self.initial.get(name) or field.initial
        return data

    def get_field_errors(self, field):
        errors = super(NgModelFormMixin, self).get_field_errors(field)
        identifier = format_html('{0}.{1}', self.form_name, field.name)
        errors.append(SafeTuple((identifier, self.field_error_css_classes, '$pristine', '$message', 'invalid', '$message')))
        return errors

    def non_field_errors(self):
        errors = super(NgModelFormMixin, self).non_field_errors()
        errors.append(SafeTuple((self.form_name, self.form_error_css_classes, '$pristine', '$message', 'invalid', '$message')))
        return errors

    def get_widget_attrs(self, bound_field):
        identifier = self.add_prefix(bound_field.name)
        ng = {
            'name': bound_field.name,
            'identifier': identifier,
            'model': self.scope_prefix and ('%s.%s' % (self.scope_prefix, identifier)) or identifier
        }
        attrs = {}
        if hasattr(self, 'Meta') and bound_field.name in getattr(self.Meta, 'ng_models', []):
            attrs['ng-model'] = ng['model']
        for key, fmtstr in self.ng_directives.items():
            attrs[key] = fmtstr % ng
        return attrs

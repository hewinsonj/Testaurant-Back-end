from api.models import editLog
from django.forms.models import model_to_dict

class AuditMixin:
    audit_fields = None  # optional whitelist

    def _snapshot(self, obj):
        data = model_to_dict(obj)
        if self.audit_fields:
            data = {k: v for k, v in data.items() if k in self.audit_fields}
        return data

    def _log(self, action, instance, before=None, after=None):
        editLog.objects.create(
            restaurant=getattr(instance, 'restaurant', None),
            actor=self.request.user if self.request.user.is_authenticated else None,
            action=action,
            target_model=instance.__class__.__name__,
            target_id=instance.pk,
            before=before,
            after=after,
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._log('create', instance, before=None, after=self._snapshot(instance))
        return instance

    def perform_update(self, serializer):
        instance = self.get_object()
        before = self._snapshot(instance)
        instance = serializer.save()
        after = self._snapshot(instance)
        self._log('update', instance, before=before, after=after)
        return instance

    def perform_destroy(self, instance):
        before = self._snapshot(instance)
        self._log('delete', instance, before=before, after=None)
        return super().perform_destroy(instance)
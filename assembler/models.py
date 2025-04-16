from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from customers.models import AssemblyRequest
from notifications.signals import notify

class AssemblyTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing Components'),
        ('assembling', 'Assembling'),
        ('testing', 'Testing'),
        ('quality_check', 'Quality Check'),
        ('completed', 'Completed'),
        ('issues', 'Issues Found')
    ]

    request = models.OneToOneField(
        AssemblyRequest,
        on_delete=models.CASCADE,
        related_name='assembly_task'
    )
    assembler = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assembly_tasks'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_date = models.DateTimeField(null=True, blank=True)
    expected_completion = models.DateTimeField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Assembly Task for Request #{self.request.id}"

    def save(self, *args, **kwargs):
        # If status is being changed
        if self.pk:
            old_task = AssemblyTask.objects.get(pk=self.pk)
            if old_task.status != self.status:
                # Update timestamps based on status
                if self.status == 'preparing' and not self.start_date:
                    self.start_date = timezone.now()
                elif self.status == 'completed' and not self.actual_completion:
                    self.actual_completion = timezone.now()
                
                # Notify customer about status change
                notify.send(
                    sender=self.assembler,
                    recipient=self.request.customer,
                    verb='updated',
                    action_object=self,
                    description=f'Assembly task status updated to {self.get_status_display()}'
                )

                # Notify supervisor if issues are found
                if self.status == 'issues':
                    supervisors = User.objects.filter(is_staff=True)
                    for supervisor in supervisors:
                        notify.send(
                            sender=self.assembler,
                            recipient=supervisor,
                            verb='reported',
                            action_object=self,
                            description=f'Issues reported in assembly task #{self.pk}'
                        )

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class TaskCheckpoint(models.Model):
    task = models.ForeignKey(
        AssemblyTask,
        on_delete=models.CASCADE,
        related_name='checkpoints'
    )
    description = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='completed_checkpoints'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checkpoint: {self.description} for Task #{self.task.pk}"

    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']

class IssueReport(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]

    task = models.ForeignKey(
        AssemblyTask,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_issues'
    )
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resolved_issues'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Issue: {self.title} for Task #{self.task.pk}"

    def save(self, *args, **kwargs):
        if self.resolved and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        # If this is a new issue
        if not self.pk:
            # Update task status to 'issues'
            self.task.status = 'issues'
            self.task.save(update_fields=['status'])
            
            # Notify supervisors
            supervisors = User.objects.filter(is_staff=True)
            for supervisor in supervisors:
                notify.send(
                    sender=self.reported_by,
                    recipient=supervisor,
                    verb='reported',
                    action_object=self,
                    description=f'New {self.get_priority_display()} priority issue reported: {self.title}'
                )

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

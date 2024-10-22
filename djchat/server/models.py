from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from .validators import validate_icon_image_size, validate_image_file_extension

# File upload path functions
# These functions determine where uploaded files will be stored in the media directory


def server_icon_upload_path(instance, filename):
    """Generate upload path for server icons.
    Creates a unique path based on server ID to prevent filename conflicts."""
    return f"server/{instance.id}/server_icon/{filename}"


def server_banner_upload_path(instance, filename):
    """Generate upload path for server banners.
    Creates a unique path based on server ID to prevent filename conflicts."""
    return f"server/{instance.id}/server_banner/{filename}"


def category_icon_upload_path(instance, filename):
    """Generate upload path for category icons.
    Creates a unique path based on category ID to prevent filename conflicts."""
    return f"category/{instance.id}/category_icon/{filename}"


class Category(models.Model):
    """
    Represents a category that servers can belong to.
    Acts as a classification system for organizing servers by type/theme.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Optional description field
    icon = models.FileField(
        upload_to=category_icon_upload_path,
        null=True,
        blank=True,  # Makes the field optional in forms and the database
    )

    def save(self, *args, **kwargs):
        """
        Override the default save method to handle icon file management.
        When updating an existing category with a new icon:
        1. Retrieve the existing category
        2. If the icon has changed, delete the old icon file
        3. Save the new data
        This prevents orphaned files in the media directory.
        """
        if self.id:
            existing = get_object_or_404(Category, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)
        super(Category, self).save(*args, **kwargs)

    @receiver(models.signals.pre_delete, sender="server.Category")
    def category_delete_files(sender, instance, **kwargs):
        """
        Signal receiver that executes before a Category is deleted.
        Ensures that when a category is deleted, its associated icon file
        is also deleted from the file system to prevent orphaned files.
        """
        for field in instance._meta.fields:
            if field.name == "icon":
                file = getattr(instance, field.name)
                if file:
                    file.delete(save=False)

    def __str__(self):
        return self.name


class Server(models.Model):
    """
    Represents a server instance in the application.
    Servers are the main containers for channels and user interactions.
    Similar to how Discord or Slack organizes its workspace structure.
    """

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # When user is deleted, delete their servers
        related_name="server_owner",  # Access via user.server_owner.all()
    )
    # Every server will have a category (one-to-one), one category can have many servers (one-to-many) many side has foreign key hence specified here only.
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,  # When category is deleted, delete associated servers
        related_name="server_category",  # Access via category.server_category.all()
    )
    description = models.CharField(max_length=250, blank=True, null=True)
    # A server can have many members, members can be part of many servers. Hence, many to many relationship. Seperate table mapping servers and users
    member = models.ManyToManyField(
        settings.AUTH_USER_MODEL,  # Creates intermediary table for server-user relationships
        # No related_name specified, so default would be server_set
    )
    banner = models.ImageField(
        upload_to=server_banner_upload_path,
        null=True,
        blank=True,
        validators=[validate_image_file_extension],  # Ensures proper file types
    )
    icon = models.ImageField(
        upload_to=server_icon_upload_path,
        null=True,
        blank=True,
        validators=[
            validate_icon_image_size,  # Ensures icon isn't too large
            validate_image_file_extension,  # Ensures proper file types
        ],
    )

    def save(self, *args, **kwargs):
        if self.id:
            existing = get_object_or_404(Server, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)
            if existing.banner != self.banner:
                existing.banner.delete(save=False)
        super(Category, self).save(*args, **kwargs)

    @receiver(models.signals.pre_delete, sender="server.Server")
    def category_delete_files(sender, instance, **kwargs):
        for field in instance._meta.fields:
            if field.name == "icon" or field.name == "banner":
                file = getattr(instance, field.name)
                if file:
                    file.delete(save=False)

    def __str__(self):
        return f"{self.name}-{self.id}"


class Channel(models.Model):
    """
    Represents a channel within a server.
    Channels are specific discussion areas within a server, similar to
    Discord channels or Slack channels within a workspace.
    """

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # When user is deleted, delete their channels
        related_name="channel_owner",  # Access via user.channel_owner.all()
    )
    topic = models.CharField(max_length=100)
    # A server can have many channels (one-to-many), one channel can have one server (one-to-one). Specified on many side.
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,  # When server is deleted, delete its channels
        related_name="channel_server",  # Access via server.channel_server.all()
    )

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

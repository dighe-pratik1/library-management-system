from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.db.models import Q

from .models import Notification

from members.models import Member


# =========================================================
# NOTIFICATION LIST
# =========================================================

def notification_list(request):

    notifications = Notification.objects.select_related(
        "member"
    ).all()


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()


    if search:

        notifications = notifications.filter(

            Q(
                title__icontains=search
            )

            |

            Q(
                message__icontains=search
            )

            |

            Q(
                member__first_name__icontains=search
            )

            |

            Q(
                member__last_name__icontains=search
            )

            |

            Q(
                member__member_code__icontains=search
            )
        )


    # -----------------------------------------------------
    # TYPE FILTER
    # -----------------------------------------------------

    notification_type = request.GET.get(
        "type",
        ""
    ).strip()


    if notification_type:

        notifications = notifications.filter(
            notification_type=notification_type
        )


    # -----------------------------------------------------
    # READ STATUS FILTER
    # -----------------------------------------------------

    read_status = request.GET.get(
        "read",
        ""
    ).strip()


    if read_status == "read":

        notifications = notifications.filter(
            is_read=True
        )


    elif read_status == "unread":

        notifications = notifications.filter(
            is_read=False
        )


    # -----------------------------------------------------
    # COUNTS
    # -----------------------------------------------------

    total_notifications = Notification.objects.count()

    unread_notifications = Notification.objects.filter(
        is_read=False
    ).count()

    read_notifications = Notification.objects.filter(
        is_read=True
    ).count()


    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "notifications": notifications,

        "total_notifications": total_notifications,

        "unread_notifications": unread_notifications,

        "read_notifications": read_notifications,

        "search": search,

        "notification_type": notification_type,

        "read_status": read_status,

        "notification_types":
            Notification.NotificationType.choices,
    }


    return render(
        request,
        "notifications/notification_list.html",
        context
    )


# =========================================================
# ADD NOTIFICATION
# =========================================================

def notification_add(request):

    if request.method == "POST":

        member_id = request.POST.get(
            "member"
        )

        title = request.POST.get(
            "title",
            ""
        ).strip()

        message_text = request.POST.get(
            "message",
            ""
        ).strip()

        notification_type = request.POST.get(
            "notification_type",
            Notification.NotificationType.GENERAL
        )

        priority = request.POST.get(
            "priority",
            Notification.Priority.NORMAL
        )


        # -------------------------------------------------
        # MEMBER VALIDATION
        # -------------------------------------------------

        if not member_id:

            messages.error(
                request,
                "Please select a member."
            )

            return redirect(
                "notification_add"
            )


        member = get_object_or_404(
            Member,
            pk=member_id
        )


        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        if not title:

            messages.error(
                request,
                "Please enter notification title."
            )

            return redirect(
                "notification_add"
            )


        # -------------------------------------------------
        # MESSAGE
        # -------------------------------------------------

        if not message_text:

            messages.error(
                request,
                "Please enter notification message."
            )

            return redirect(
                "notification_add"
            )


        # -------------------------------------------------
        # CREATE
        # -------------------------------------------------

        Notification.objects.create(

            member=member,

            title=title,

            message=message_text,

            notification_type=notification_type,

            priority=priority,

            is_read=False,
        )


        messages.success(
            request,
            "Notification created successfully."
        )


        return redirect(
            "notification_list"
        )


    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    members = Member.objects.filter(
        status=True
    ).order_by(
        "first_name",
        "last_name"
    )


    context = {

        "members": members,

        "notification_types":
            Notification.NotificationType.choices,

        "priorities":
            Notification.Priority.choices,
    }


    return render(
        request,
        "notifications/notification_form.html",
        context
    )


# =========================================================
# NOTIFICATION DETAIL
# =========================================================

def notification_detail(request, pk):

    notification = get_object_or_404(

        Notification.objects.select_related(
            "member"
        ),

        pk=pk
    )


    # -----------------------------------------------------
    # Automatically mark as read
    # -----------------------------------------------------

    if not notification.is_read:

        notification.is_read = True

        notification.save(
            update_fields=[
                "is_read",
                "updated_at"
            ]
        )


    return render(

        request,

        "notifications/notification_detail.html",

        {
            "notification": notification
        }
    )


# =========================================================
# MARK AS READ
# =========================================================

def notification_read(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk
    )


    notification.is_read = True

    notification.save(
        update_fields=[
            "is_read",
            "updated_at"
        ]
    )


    messages.success(
        request,
        "Notification marked as read."
    )


    return redirect(
        "notification_list"
    )


# =========================================================
# MARK AS UNREAD
# =========================================================

def notification_unread(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk
    )


    notification.is_read = False

    notification.save(
        update_fields=[
            "is_read",
            "updated_at"
        ]
    )


    messages.success(
        request,
        "Notification marked as unread."
    )


    return redirect(
        "notification_list"
    )


# =========================================================
# MARK ALL AS READ
# =========================================================

def notification_read_all(request):

    if request.method == "POST":

        Notification.objects.filter(
            is_read=False
        ).update(
            is_read=True
        )


        messages.success(
            request,
            "All notifications marked as read."
        )


    return redirect(
        "notification_list"
    )


# =========================================================
# DELETE NOTIFICATION
# =========================================================

def notification_delete(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk
    )


    if request.method == "POST":

        notification.delete()


        messages.success(
            request,
            "Notification deleted successfully."
        )


        return redirect(
            "notification_list"
        )


    return render(

        request,

        "notifications/notification_detail.html",

        {
            "notification": notification,

            "delete_confirm": True
        }
    )
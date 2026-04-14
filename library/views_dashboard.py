@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    if is_admin(request.user):
        if request.method == 'POST':
            txn_id = request.POST.get('txn_id')
            action = request.POST.get('action')
            txn = get_object_or_404(Transaction, id=txn_id)
            if action == 'approve_issue':
                txn.mark_issued()
                messages.success(request, f"Request for '{txn.book.title}' by {txn.user.username} APPROVED.")
            elif action == 'approve_return':
                txn.mark_returned()
                messages.success(request, f"Return for '{txn.book.title}' by {txn.user.username} CONFIRMED.")
            elif action == 'reject_request':
                txn.mark_cancelled()
                messages.error(request, f"Request for '{txn.book.title}' by {txn.user.username} REJECTED/CANCELLED.")
            return redirect('dashboard')

        pending_requests = Transaction.objects.filter(status__in=[Transaction.Status.REQUESTED, Transaction.Status.RETURN_REQUESTED]).order_by('-created_at')
        latest_contacts = ContactMessage.objects.all().order_by('-created_at')[:5]
        latest_feedback = FeedbackMessage.objects.all().order_by('-created_at')[:5]
        context = {
            'pending_requests': pending_requests,
            'latest_contacts': latest_contacts,
            'latest_feedback': latest_feedback
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        if request.method == 'POST':
            txn_id = request.POST.get('txn_id')
            action = request.POST.get('action')
            txn = get_object_or_404(Transaction, id=txn_id, user=request.user)
            if action == 'cancel_request' and txn.status == Transaction.Status.REQUESTED:
                txn.mark_cancelled()
                messages.warning(request, "Request cancelled.")
            elif action == 'request_return' and txn.status == Transaction.Status.ISSUED:
                txn.status = Transaction.Status.RETURN_REQUESTED
                txn.save()
                messages.success(request, "Return requested. Please wait for admin approval.")
            return redirect('dashboard')

        txns = Transaction.objects.filter(user=request.user).exclude(status=Transaction.Status.CANCELLED).order_by('-created_at')
        return render(request, 'dashboard/student_dashboard.html', {'transactions': txns})

@login_required
@user_passes_test(is_admin)
def admin_user_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.filter(role=User.Roles.STUDENT).order_by('username')
    return render(request, 'admin/user_list.html', {'students': users})

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    student = get_object_or_404(User, id=user_id)
    history = Transaction.objects.filter(user=student).order_by('-created_at')
    currently_issued = history.filter(status=Transaction.Status.ISSUED)
    return render(request, 'admin/user_detail.html', {
        'student': student,
        'history': history,
        'currently_issued': currently_issued
    })

@login_required
@user_passes_test(is_admin)
def admin_transactions(request: HttpRequest) -> HttpResponse:
    all_txns = Transaction.objects.all().order_by('-created_at')
    return render(request, 'admin/all_transactions.html', {'transactions': all_txns})

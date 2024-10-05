from django.urls import path
from . import views


urlpatterns = [
    path('', views.leaveRequestIndex, name='leave_request_index'),
    path('<int:id>/', views.leaveRequestDetail, name='leave_request_detail'),
    path('create/', views.leaveRequestCreate, name='leave_request_create'),
    path('cancel/', views.leave_request_cancel, name='leave_request_cancel'),
    path('update/<int:id>/', views.leaveRequestUpdate, name='leave_request_update'),
    path('approval/', views.LeaveApprovalIndex, name='leave_approval_index'),
    path('approval/create/', views.leave_approval_create, name='leave_approval_create'),
    path('active/', views.leaveActiveIndex, name='leave_active_index'),
    path('balance/create/', views.leaveBalanceCreate, name='leave_balance_create'),

]
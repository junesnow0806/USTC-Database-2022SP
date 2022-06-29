from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('home/', views.home),
    
    # branch-related
    path('show_all_branches/', views.show_all_branches),
    path('create_branch/', views.create_branch),
    path('delete_branch', views.delete_branch),
    path('update_branch', views.update_branch),
    
    # customer-related
    path('show_all_customers/', views.show_all_customers),
    path('create_customer/', views.create_customer),
    path('delete_customer', views.delete_customer),
    path('update_customer', views.update_customer),
    path('show_contact', views.show_contact),
    path('show_customer_principal', views.show_customer_principal),
    path('show_customer_accounts', views.show_customer_accounts),
    path('show_customer_loans', views.show_customer_loans),
    
    
    # account-related
    path('create_account/', views.create_account),
    path('delete_account', views.delete_account),
    path('update_account', views.update_account),
    path('show_all_accounts/', views.show_all_accounts),
    path('add_account_customer', views.add_account_customer),
    path('show_deposit_customers', views.show_deposit_customers),
    path('show_cheque_customers', views.show_cheque_customers),
    
    
    # loan-related
    path('create_loan/', views.create_loan),
    path('delete_loan', views.delete_loan),
    path('update_loan', views.update_loan),
    path('show_all_loans/', views.show_all_loans),
    path('show_loan_customers', views.show_loan_customers),
    path('add_loan_customer', views.add_loan_customer),
    path('create_payout', views.create_payout),
    path('show_all_payouts', views.show_all_payouts),
    
    
    
    # statistics-related
    path('stats_home/', views.stats_home),
    path('stats_loan', views.stats_loan),
    path('stats_loan_year', views.stats_loan_year),
    path('stats_deposit', views.stats_deposit),
    path('stats_deposit_year', views.stats_deposit_year),
    
    
    
    
    
    
    
]
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from httplib2 import Http
from .models import *
import random
import string
from django.db.models import Sum, Max, Min
from decimal import Decimal

# Create your views here.
def home(request):
    return render(request, 'BankSystem/home.html')



'''
Branch Management Module
'''
def show_all_branches(request):
    all_branches = Branch.objects.all()
    return render(request, 'BankSystem/branch/show_all_branches.html', locals())

def update_branch(request):
    branch_name = request.GET.get('branch_name')
    if not branch_name:
        return HttpResponse('---请求异常')
    try:
        branch = Branch.objects.get(name=branch_name)
    except Exception as e:
        print('--update branch error is %s'%(e))
        return HttpResponse('--not found')
    
    if request.method == 'GET':
        return render(request, 'BankSystem/branch/update_branch.html', locals())
    elif request.method == 'POST':
        assets = request.POST['assets']
        branch.assets = assets
        branch.save()
        return HttpResponseRedirect('/BankSystem/show_all_branches')
    
def delete_branch(request):
    branch_name = request.GET.get('branch_name')
    if not branch_name:
        return HttpResponse('---请求异常')
    
    try:
        branch = Branch.objects.get(name=branch_name)
    except Exception as e:
        print('--delete branch error is %s'%(e))
        return HttpResponse('--not found')
    
    branch.delete()
    return HttpResponseRedirect('/BankSystem/show_all_branches')

def create_branch(request):
    if request.method == 'GET':
        return render(request, 'BankSystem/branch/create_branch.html')
    elif request.method == 'POST':
        name = request.POST.get('name')
        existed = True
        try:
            branch = Branch.objects.get(name=name)
        except:
            existed = False
        if existed:
            return HttpResponse('the branch has existed')
        city = request.POST.get('city')
        assets = request.POST.get('assets')
        Branch.objects.create(name=name, city=city, assets=assets)
        return HttpResponseRedirect('/BankSystem/show_all_branches')
    
    
    


'''
Customer Management Module
'''
def show_all_customers(request):
    all_customers = Customer.objects.all()
    return render(request, 'BankSystem/customer/show_all_customers.html', locals())

def create_customer(request):
    if request.method == 'GET':
        return render(request, 'BankSystem/customer/create_customer.html', locals())
    elif request.method == 'POST':
        id = request.POST.get('id')
        existed = True
        try:
            customer = Customer.objects.get(id=id)
        except:
            existed = False
        if existed:
            return HttpResponse('The customer has existed')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        principal_id = request.POST.get('principal_id')
        try:
            principal = Staff.objects.get(id=principal_id)
        except:
            return HttpResponse('--指定的负责人身份证号有误！')
        principal_type = request.POST.get('principal_type')
        if principal_type == 'ACCOUNT':
            principal_type = Customer.PrincipalType.ACCOUNT
        elif principal_type == 'LOAN':
            principal_type = Customer.PrincipalType.LOAN
        elif principal_type == 'BOTH':
            principal_type = Customer.PrincipalType.BOTH
        else:
            return HttpResponse("Invalid Principal Type!")
        
        # 创建客户
        customer = Customer(id=id)
        customer.name = name
        customer.phone = phone
        customer.address = address
        customer.principal = principal
        customer.principal_type = principal_type
        customer.save()
        
        # 创建客户的联系人
        contact_name = request.POST.get('contact_name')
        contact_phone = request.POST.get('contact_phone')
        contact_email = request.POST.get('contact_email')
        contact_relationship = request.POST.get('contact_relationship')
        Contact.objects.create(customer=customer, name=contact_name, phone=contact_phone, email=contact_email, relationship=contact_relationship)
        
        return HttpResponseRedirect('/BankSystem/show_all_customers')
    
def delete_customer(request):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return HttpResponse('---请求异常')
    try:
        customer = Customer.objects.get(id=customer_id)
    except Exception as e:
        print('--update bank error is %s'%(e))
        return HttpResponse('--not found')
    loans = customer.loan_set.all()
    deposits = customer.deposit_set.all()
    cheques = customer.cheque_set.all()
    if len(loans) > 0:
        return HttpResponse('该客户存在关联贷款, 不允许删除')
    if len(deposits) > 0:
        return HttpResponse('该客户存在关联储蓄账户, 不允许删除')
    if len(cheques) > 0:
        return HttpResponse('该客户存在关联支票账户, 不允许删除')
    customer.delete()
    return HttpResponseRedirect('/BankSystem/show_all_customers')

def update_customer(request):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return HttpResponse('---请求异常')
    try:
        customer = Customer.objects.get(id=customer_id)
    except Exception as e:
        print('--update customer error is %s'%(e))
        return HttpResponse('--not found')
    
    if request.method == 'GET':
        return render(request, 'BankSystem/customer/update_customer.html', locals())
    elif request.method == 'POST':
        customer.name = request.POST['name']
        customer.phone = request.POST['phone']
        customer.address = request.POST['address']
        customer.save()
        return HttpResponseRedirect('/BankSystem/show_all_customers')

def show_contact(request):
    customer_id = request.GET['customer_id']
    customer = Customer.objects.get(id=customer_id)
    try:
        contact = customer.contact
    except:
        return HttpResponse('联系人不存在!')
    return render(request, 'BankSystem/customer/show_contact.html', locals())

def show_customer_accounts(request):
    customer_id = request.GET.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    deposits = customer.deposit_set.all()
    cheques = customer.cheque_set.all()
    return render(request, 'BankSystem/customer/show_customer_accounts.html', locals())

def show_customer_loans(request):
    customer_id = request.GET.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    loans = customer.loan_set.all()
    return render(request, 'BankSystem/customer/show_customer_loans.html', locals())

def show_customer_principal(request):
    customer_id = request.GET.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    principal = customer.principal
    return render(request, 'BankSystem/customer/show_customer_principal.html', locals())



'''
Account Management
'''
def create_account(request):
    if request.method == 'GET':
        all_branches = Branch.objects.all()
        return render(request, 'BankSystem/account/create_account.html', locals())
    elif request.method == 'POST':
        balance = request.POST['balance']
        branch_name = request.POST['branch_name']
        open_date = request.POST['open_date']
        try:
            branch = Branch.objects.get(name=branch_name)
        except Exception as e:
            print('--update bank error is %s'%(e))
            return HttpResponse('--not found')
        if request.POST['account_type'] == '储蓄账户':
            # 生成一个不重复的储蓄账户号, 约定储蓄账户号以0开头
            account_no = "".join(random.sample([x for x in string.digits], 10))
            account_no = '0' + account_no[1:]
            account_type = Account.AccountType.DEPOSIT
            interest_rate = request.POST['interest_rate']
            currency_type = request.POST['currency_type']
            Deposit.objects.create(no=account_no, account_type=account_type, balance=balance, branch=branch, interest_rate=interest_rate, currency_type=currency_type)
            deposit = Deposit.objects.get(no=account_no)
            deposit.open_date = open_date
            deposit.save()
        elif request.POST['account_type'] == '支票账户':
            # 生成一个不重复的支票账户号, 约定支票账户号以1开头
            account_no = "".join(random.sample([x for x in string.digits], 10))
            account_no = '1' + account_no[1:]
            account_type = Account.AccountType.CHEQUE
            overdraft = request.POST['overdraft']
            Cheque.objects.create(no=account_no, account_type=account_type, balance=balance, branch=branch, overdraft=overdraft)
            cheque = Cheque.objects.get(no=account_no)
            cheque.open_date = open_date
            cheque.save()
        return render(request, 'BankSystem/account/create_success.html')

def delete_account(request):
    account_no = request.GET.get('account_no')
    account_type = request.GET.get('account_type')
    if account_type == 'DEPOSIT':
        deposit = Deposit.objects.get(no=account_no)
        deposit.delete()
    elif account_type == 'CHEQUE':
        cheque = Cheque.objects.get(no=account_no)
        cheque.delete()
    return HttpResponseRedirect("/BankSystem/show_all_accounts")

def update_account(request):
    if request.method == 'GET':
        account_no = request.GET.get('account_no')
        account_type = request.GET.get('account_type')
        if account_type == 'DEPOSIT':
            deposit = Deposit.objects.get(no=account_no)
            balance = deposit.balance
            interest_rate = deposit.interest_rate
            currency_type = deposit.currency_type
            branch_name = deposit.branch.name
            return render(request, 'BankSystem/account/update_deposit.html', locals())
        elif account_type == 'CHEQUE':
            cheque = Cheque.objects.get(no=account_no)
            balance = cheque.balance
            overdraft = cheque.overdraft
            branch_name = cheque.branch.name
            return render(request, 'BankSystem/account/update_cheque.html', locals())
        else:
            return HttpResponse('---Wrong account type!')
    elif request.method == 'POST':
        account_type = request.POST.get('account_type')
        if account_type == 'DEPOSIT':
            deposit_no = request.POST.get('account_no')
            deposit = Deposit.objects.get(no=deposit_no)
            deposit.balance = request.POST.get('balance')
            deposit.interest_rate = request.POST.get('interest_rate')
            deposit.currency_type = request.POST.get('currency_type')
            deposit.save()
            return HttpResponseRedirect('/BankSystem/show_all_accounts')
        elif account_type == 'CHEQUE':
            cheque_no = request.POST.get('account_no')
            cheque =Cheque.objects.get(no=cheque_no)
            cheque.balance = request.POST.get('balance')
            cheque.overdraft = request.POST.get('overdraft')
            cheque.save()
            return HttpResponseRedirect('/BankSystem/show_all_accounts')
        else:
            return HttpResponse('Invalid account type!')
    return HttpResponse("Invalid request type!")

def show_all_accounts(request):
    all_deposits = Deposit.objects.all()
    all_cheques = Cheque.objects.all()
    return render(request, 'BankSystem/account/show_all_accounts.html', locals())

def add_account_customer(request):
    if request.method == 'GET':
        account_no = request.GET.get('account_no')
        account_type = request.GET.get('account_type')
        branch_name = request.GET.get('branch_name')
        return render(request, 'BankSystem/account/add_account_customer.html',locals())
    elif request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        account_no = request.POST.get('account_no')
        account_type = request.POST.get('account_type')
        branch_name = request.POST.get('branch_name')
        branch = Branch.objects.get(name=branch_name)
        if not customer_id:
            return HttpResponse('---请求异常')
        else:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Exception as e:
                print('--update bank error is %s'%(e))
                return HttpResponse('--not found')
            # 查询该客户的账户信息
            # 如果该客户已经在同一支行开设了同一类型的账户, 则不允许开设
            if account_type == 'DEPOSIT':
                existed = True
                try:
                    account = customer.deposit_set.get(branch=branch)
                except:
                    existed = False
                if existed:
                    return HttpResponse("该客户已在该支行开设过储蓄账号, 不允许再次开设!")
                else:
                    deposit = Deposit.objects.get(no=account_no)
                    deposit.customers.add(customer)
                    return HttpResponseRedirect('/BankSystem/show_all_accounts')
            elif account_type == 'CHEQUE':
                existed = True
                try:
                    account = customer.cheque_set.get(branch=branch)
                except:
                    existed = False
                if existed:
                    return HttpResponse("该客户已在该支行开设过支票账号, 不允许再次开设!")
                else:
                    cheque = Cheque.objects.get(no=account_no)
                    cheque.customers.add(customer)
                    return HttpResponseRedirect('/BankSystem/show_all_accounts')

def show_deposit_customers(request):
    deposit_no = request.GET.get('account_no')
    deposit = Deposit.objects.get(no=deposit_no)
    customers = deposit.customers.all()
    return render(request, 'BankSystem/account/show_deposit_customers.html', locals())

def show_cheque_customers(request):
    cheque_no = request.GET.get('account_no')
    cheque = Cheque.objects.get(no=cheque_no)
    customers = cheque.customers.all()
    return render(request, 'BankSystem/account/show_cheque_customers.html', locals())
    



'''
Loan Management Module
'''
def create_loan(request):
    if request.method == 'GET':
        all_branches = Branch.objects.all()
        return render(request, 'BankSystem/loan/create_loan.html', locals())
    elif request.method == 'POST':
        brach_name = request.POST.get('branch_name')
        branch = Branch.objects.get(name=brach_name)
        amount = request.POST.get('amount')
        # 生成一个不重复的贷款号, 约定贷款号以2开头
        loan_no = "".join(random.sample([x for x in string.digits], 10))
        loan_no = '2' + loan_no[1:]
        Loan.objects.create(no=loan_no, amount=amount, branch=branch)
        return HttpResponseRedirect('/BankSystem/show_all_loans')
    else:
        return HttpResponse('Invalid request!')

def delete_loan(request):
    loan_no = request.GET.get('loan_no')
    loan = Loan.objects.get(no=loan_no)
    if loan.status == '发放中':
        return HttpResponse('处于发放中的贷款不允许删除')
    loan.delete()
    return HttpResponseRedirect('/BankSystem/show_all_loans')

def update_loan(request):
    return HttpResponse('贷款信息不允许修改')

def show_all_loans(request):
    all_loans = Loan.objects.all()
    for loan in all_loans:
        payouts = loan.payout_set.all()
        if len(payouts) == 0:
            payed = Decimal(0)
        else:
            payed = payouts.aggregate(Sum('amount'))['amount__sum']
        if payed == Decimal(0):
            loan.status = '未开始发放'
        elif payed < loan.amount:
            loan.status = '发放中'
        elif payed == loan.amount:
            loan.status = '已全部发放'
        loan.save()
    return render(request, 'BankSystem/loan/show_all_loans.html', locals())

def add_loan_customer(request):
    if request.method == 'GET':
        loan_no = request.GET.get('loan_no')
        branch_name = request.GET.get('branch_name')
        return render(request, 'BankSystem/loan/add_loan_customer.html', locals())
    elif request.method == 'POST':
        loan_no = request.POST.get('loan_no')
        branch_name = request.POST.get('branch_name')
        customer_id = request.POST.get('customer_id')
        try:
            customer = Customer.objects.get(id=customer_id)
        except Exception as e:
            print('--add loan customer error is %s'%(e))
            return HttpResponse('--not found')
        loan = Loan.objects.get(no=loan_no)
        loan.customers.add(customer)
        return HttpResponseRedirect('/BankSystem/show_all_loans')
    else:
        return HttpResponse('Invalid request!')

def show_loan_customers(request):
    loan_no = request.GET.get('loan_no')
    loan = Loan.objects.get(no=loan_no)
    customers = loan.customers.all()
    return render(request, 'BankSystem/loan/show_loan_customers.html', locals())

def create_payout(request):
    if request.method == 'GET':
        loan_no = request.GET.get('loan_no')
        loan = Loan.objects.get(no=loan_no)
        return render(request, 'BankSystem/loan/create_payout.html', locals())
    elif request.method == 'POST':
        loan_no = request.POST.get('loan_no')
        loan = Loan.objects.get(no=loan_no)
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        payout_no = loan.payout_set.all().count() + 1 # 生成payout编号
        payouts = loan.payout_set.all()
        if len(payouts) == 0:
            payed = Decimal(0)
        else:
            payed = payouts.aggregate(Sum('amount'))['amount__sum']
        new_payed = payed + Decimal(amount)
        if new_payed < loan.amount:
            loan.status = '发放中'
        elif new_payed == loan.amount:
            loan.status = '已全部发放'
        else:
            return HttpResponse('Invalid payout--amount overflow!')
        loan.save()
        Payout.objects.create(no=payout_no, date=date, amount=amount, loan=loan)
        return HttpResponseRedirect('/BankSystem/show_all_payouts?loan_no=%s'%loan.no)
    else:
        return HttpResponse('Invalid request!')    
    
def show_all_payouts(request):
    loan_no = request.GET.get('loan_no')
    loan = Loan.objects.get(no=loan_no)
    all_payouts = loan.payout_set.all()
    if loan.payout_set.all():
        remainder = loan.amount - loan.payout_set.all().aggregate(Sum('amount'))['amount__sum']
    else:
        remainder = loan.amount
    return render(request, 'BankSystem/loan/show_all_payouts.html', locals())




'''
Statistics Module
'''
def stats_home(request):
    return render(request, 'BankSystem/stats/stats_home.html')

def stats_loan(request):
    created_year_min = Loan.objects.all().aggregate(Min('created_time'))['created_time__min'].year
    created_year_max = Loan.objects.all().aggregate(Max('created_time'))['created_time__max'].year
    # 根据年份从小到大生成一个列表数据
    stats_years = []
    branches = Branch.objects.all()
    for year in range(created_year_min, created_year_max+1):
        stats_year = {}
        stats_year['year'] = year
        stats_year['branch_dicts'] = []
        for branch in branches:
            branch_dict = {}
            loans = Loan.objects.filter(created_time__year=year, branch=branch) # year年创建的属于该支行贷款记录
            total_amount = loans.aggregate(Sum('amount'))['amount__sum']
            customer_count = 0
            for loan in loans:
                customer_count += loan.customers.all().count()
            branch_dict['branch_name'] = branch.name
            branch_dict['total_amount'] = total_amount
            branch_dict['customer_count'] = customer_count
            stats_year['branch_dicts'].append(branch_dict)
        stats_years.append(stats_year)
    return render(request, 'BankSystem/stats/stats_loan.html', locals())

def stats_loan_year(request):
    year = request.GET.get('year')
    created_month_min = Loan.objects.filter(created_time__year=year).aggregate(Min('created_time'))['created_time__min'].month
    created_month_max = Loan.objects.filter(created_time__year=year).aggregate(Max('created_time'))['created_time__max'].month
    
    # 根据月份从小到大生成一个列表
    stats_months = []
    branches = Branch.objects.all()
    for month in range(created_month_min, created_month_max+1):
        stats_month = {}
        stats_month['month'] = month
        stats_month['branch_dicts'] = []
        for branch in branches:
            branch_dict = {}
            loans = Loan.objects.filter(created_time__year=year, created_time__month=month, branch__exact=branch)
            total_amount = loans.aggregate(Sum('amount'))['amount__sum']
            customer_count = 0
            for loan in loans:
                customer_count += loan.customers.all().count()
            branch_dict['branch_name'] = branch.name
            branch_dict['total_amount'] = total_amount
            branch_dict['customer_count'] = customer_count
            stats_month['branch_dicts'].append(branch_dict)
        stats_months.append(stats_month)
    
    # 按季度统计
    stats_seasons = []
    for season in range(1, 5):
        month_min = (season-1) * 3 + 1
        month_max = season * 3
        stats_season = {}
        stats_season['season'] = season
        stats_season['branch_dicts'] = []
        for branch in branches:
            branch_dict = {}
            loans = Loan.objects.filter(created_time__year=year, created_time__month__gte=month_min, created_time__month__lte=month_max, branch__exact=branch)
            total_amount = loans.aggregate(Sum('amount'))['amount__sum']
            customer_count = 0
            for loan in loans:
                customer_count += loan.customers.all().count()
            branch_dict['branch_name'] = branch.name
            branch_dict['total_amount'] = total_amount
            branch_dict['customer_count'] = customer_count
            stats_season['branch_dicts'].append(branch_dict)
        stats_seasons.append(stats_season)
    return render(request, 'BankSystem/stats/stats_loan_year.html', locals())

def stats_deposit(request):
    open_year_min = Deposit.objects.all().aggregate(Min('open_date'))['open_date__min'].year
    open_year_max = Deposit.objects.all().aggregate(Max('open_date'))['open_date__max'].year
    print(open_year_min)
    print(open_year_max)
    # 根据年份从小到大生成一个列表数据
    stats_years = []
    branches = Branch.objects.all()
    for year in range(open_year_min, open_year_max+1):
        stats_year = {}
        stats_year['year'] = year
        stats_year['branch_dicts'] = []
        for branch in branches:
            branch_dict = {}
            deposits = Deposit.objects.filter(open_date__year=year, branch=branch) # year年创建的属于该支行贷款记录
            total_amount = deposits.aggregate(Sum('balance'))['balance__sum']
            customer_count = 0
            for deposit in deposits:
                customer_count += deposit.customers.all().count()
            branch_dict['branch_name'] = branch.name
            branch_dict['total_amount'] = total_amount
            branch_dict['customer_count'] = customer_count
            stats_year['branch_dicts'].append(branch_dict)
        stats_years.append(stats_year)
    return render(request, 'BankSystem/stats/stats_deposit.html', locals())

def stats_deposit_year(request):
    year = request.GET.get('year')
    open_month_min = Deposit.objects.filter(open_date__year=year).aggregate(Min('open_date'))['open_date__min'].month
    open_month_max = Deposit.objects.filter(open_date__year=year).aggregate(Max('open_date'))['open_date__max'].month
    
    # 根据月份从小到大生成一个列表
    stats_months = []
    branches = Branch.objects.all()
    for month in range(open_month_min, open_month_max+1):
        stats_month = {}
        stats_month['month'] = month
        stats_month['branch_dicts'] = []
        for branch in branches:
            branch_dict = {}
            deposits = Deposit.objects.filter(open_date__year=year, open_date__month=month, branch__exact=branch)
            total_amount = deposits.aggregate(Sum('balance'))['balance__sum']
            customer_count = 0
            for deposit in deposits:
                customer_count += deposit.customers.all().count()
            branch_dict['branch_name'] = branch.name
            branch_dict['total_amount'] = total_amount
            branch_dict['customer_count'] = customer_count
            stats_month['branch_dicts'].append(branch_dict)
        stats_months.append(stats_month)
    
    # 按季度统计
    stats_seasons = []
    for season in range(1, 5):
        month_min = (season-1) * 3 + 1
        month_max = season * 3
        stats_season = {}
        stats_season['season'] = season
        stats_season['branch_dicts'] = []
        for branch in branches:
            branch_dict = {}
            deposits = Deposit.objects.filter(open_date__year=year, open_date__month__gte=month_min, open_date__month__lte=month_max, branch__exact=branch)
            total_amount = deposits.aggregate(Sum('balance'))['balance__sum']
            customer_count = 0
            for deposit in deposits:
                customer_count += deposit.customers.all().count()
            branch_dict['branch_name'] = branch.name
            branch_dict['total_amount'] = total_amount
            branch_dict['customer_count'] = customer_count
            stats_season['branch_dicts'].append(branch_dict)
        stats_seasons.append(stats_season)
    return render(request, 'BankSystem/stats/stats_deposit_year.html', locals())
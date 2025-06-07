from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import F,Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import *
#Import for to make the code.
#Landing Page when user just visit the site
def landPage(request):
    #Getting all seminar that is currently available
    landSems = Paginator(seminar.objects.all().exclude(semiUser = request.user.id), 5)
    lPage = request.GET.get('page')
    lSeminar = landSems.get_page(lPage)
    context = {
        "land_sem": lSeminar
    }
    #Call landing page from template
    return render(request, "dashboard/landingPage.html", context)

# Create your views here.
@login_required(login_url="/landPage") #If not login, return to land page
def dash(request): 
    #Getting list of seminar that is not made by the logged user
    dashSeminar = seminar.objects.all().exclude(semiUser = request.user.id)
    #seminars = seminar.objects.all().exclude(semiUser = request.user.id) 
    if request.GET.get('searchs', None):
        searchs = request.GET['searchs']
        dashSeminar = dashSeminar.filter(seminar_name__icontains=searchs)
    pager = Paginator(dashSeminar, 8)
    cPage = request.GET.get('page')
    seminars = pager.get_page(cPage)
    #Used to display the list of seminar later in the dashboard
    context = {
        "object_list": seminars,
    }
    #calling dashboard from template    
    return render(request, "dashboard/dashboard.html", context)

@login_required(login_url="/landPage")
# Part of Manage Seminar Participation and Manage Payment function
def pSemInfo(request, semID):
    #Getting logged in user id
    semiuser = seminar.objects.get(id=semID)
    userJoin = User.objects.get(id=request.user.id)
    #If the seminar clicked is pay to enter
    if semiuser.seminar_req == "Pay-to-enter":
        semiPayed = semPay.objects.get(semiRelation = semiuser)
        context = {'seminars':semiuser, 'Payed': semiPayed,}
        #Creating queue for Joining the seminar
        if request.method == "POST":
            reason = request.POST['why']
            imgProof = request.FILES.get('image')
            qReq = "PENDING"
            #Creating seminarQ (queue for the seminar) object
            semiQ = seminarQ.objects.create(semName=semiuser, joinUser = userJoin,
                                            reasontoJoin=reason, status_req = qReq,
                                            proofPic = imgProof)
            semiQ.save()
            return redirect('/')
    else:
        context = {'seminars':semiuser,}
    #Otherwise creating seminar ticket    
    #Creating Seminar Ticket
        if request.method == "POST":
            #Updating seminar joined user
            semiuser.joined_user =+ 1
            #Creating receipt object
            recp = "Receipt "+semiuser.seminar_name
            joinReceipt = receipt.objects.create(receiptInfo=recp, semUs=userJoin,
                                                 semInfo=semiuser)
            joinReceipt.save() #Saving receipt object
            semiuser.save() #updating seminar object
            
            return redirect('/reviewDash')
        
    #getting the seminar ID to semiuser variable
    #Used to display the seminar information based on the seminar ID 
    #given from "semiuser" variable
    
    return render(request, "ManageSeminarParticipant/pInfoSeminar.html", context)

@login_required(login_url="/landPage")
#Part of Manage Payment
def viewUQueue(request, passID):
    #Calling queue info of user that clicked
    queUser = seminarQ.objects.get(id = passID)
    ussr = User.objects.get(id=request.user.id)
    #Passing request
    if request.method == "POST":
        answ = request.POST['ans']
        #If being approved, create a receipt project
        if answ == "APPROVE":
            semir = seminar.objects.get(id=queUser.semName.id)
            semir.joined_user =+ 1
            recp = "Receipt "+queUser.semName.seminar_name
            approvReceipt = receipt.objects.create(receiptInfo=recp,
                                                   semUs=queUser.joinUser,
                                                   semInfo=queUser.semName)
            approvReceipt.save() #Saving receipt object
            semir.save() #updating seminar object
            queUser.delete() #Deleting queue object
                 
            return redirect('/reviewDash')
        else:
            #If not change status to DENIED and delete queue
            queUser.status_req = answ
            queUser.save()
            queUser.delete()
            return redirect('/reviewDash')
    context = {'queUser':queUser, 'logged_user':ussr,}
    return render(request, "ManageReview/userQueue.html", context)
    

@login_required(login_url="/landPage")
#Part of Manage Seminar Participation Function
def viewTix(request, userTix):
    tix = receipt.objects.get(id = userTix)
    context = {'receipts':tix}
    return render(request, "ManageReview/ticketView.html", context)


#Manage User used to register the user to SemiDu.
def manageUser(request):
    #Getting request from html form.
    if request.method == "POST":
        #Variable ID from the form will be requested to be written in the-
        #python variable.
        uName = request.POST['uName']
        uPass = request.POST['uPass']
        uEmail = request.POST['uEmail']
        uPhoneNumb = request.POST['uPhoneNumb']
        
        #Creating variable using User class from Django.
        #Since it is the default User class, Phone Number will placed in the first name variable
        SemidUser = User.objects.create_user(username=uName, email=uEmail, 
                                             password=uPass, first_name=uPhoneNumb)
        
        #Saving the data to the database.
        SemidUser.save()
        
        #Message to show confirmation.
        messages.success(request, "SemiDu Account Has Been Created")
        
        #Redirecting user to Sign In page.
        return redirect('authuser')
    #Diplaying the Register Page.
    return render(request, "ManageUser/register.html")
        
        
#Authenticate User used to let user sign in to SemiDu.
def authenticateUser(request):
    #Getting request from sign in page html form.
    if request.method == 'POST':
        uName = request.POST['uName']
        uPass = request.POST['uPass']
        #Checking User database if the inputted name exist.
        user = authenticate(username=uName, password=uPass)
        #If the data exist, user will be redirected to dashboard page.
        if user is not None:
            #Signing in the user
            login(request, user)
            
            return redirect('/')
        #If the data did not exist, user will be given error.
        else:
            messages.error(request, "404")
            return redirect('')
    #Diplaying the Sign In Page.
    return render(request, "AuthenticateUser/signin.html")
#Signing Out Method used to sign out user from SemiDu.
def signOut(request):
    logout(request)
    return redirect('/')

#Manage Profile used to change user account information in SemiDu
@login_required(login_url="/landPage")
def manageProf(request):
    #Request if the user is signed in or not
    if request.user.is_authenticated:
        #if signed in, user id will be the identification for it
        logged_user = User.objects.get(id=request.user.id)
        #Getting request from profile page html form
        if request.method == 'POST':
            cName = request.POST['cName']
            cEmail = request.POST['cEmail']
            cPhoneNumb = request.POST['cPhoneNumb']
            #Replacing user data with the data that has been inputed in form
            #Note: Phone Number will placed in the first name variable
            logged_user.username = cName
            logged_user.email = cEmail
            logged_user.first_name = cPhoneNumb
            #Saving the current data
            logged_user.save()
            #As a sign that the changes happen succesfuly
            messages.success(request, ("Your Data has been Changed, please Sign In again."))
            #Signing out user to maximizing the changes
            logout(request)
            return redirect('/')
    else:
        #if user not signed in, user will be directed to dashboard
        messages.success(request, ("You need to Sign In to use this service."))
    #Calling Manage Profile page
    return render(request, "ManageProfile/profile.html")

#Manage Seminar used by user to create their seminar within SemiDu
@login_required(login_url="/landPage")
def manageSeminar(request):
    #Authentification if user are signed in or not
    if request.user.is_authenticated:
        #If user signed in, user id will be analyzed as identification
        logged_user = User.objects.get(id=request.user.id)
        #Requesting form from Seminar Page
        if request.method == "POST":
            sName = request.POST['sName']
            sPoint = request.POST['sPoint']
            sPeeps = request.POST['sPeeps']
            sContact = request.POST['sContact']
            stat = request.POST['stats']
            pMethod = request.POST['payMet']
            ac = request.POST['payNum']
            
            #Variable using custom models "seminar" that has been migrated by Django
            SeminarD = seminar.objects.create(seminar_name = sName, seminar_purpose = sPoint, 
                                              amount_peoples = sPeeps, seminar_contact = sContact,
                                              semiUser = logged_user, seminar_req = stat)
            #if user select pay to enter semPay object will be created
            if SeminarD.seminar_req == "Pay-to-enter":
                paySeminar = semPay.objects.create(semiRelation = SeminarD,
                                                   semiMethod = pMethod, 
                                                   serialNum = ac)
                
                paySeminar.save() #Saving semPay object
                SeminarD.save() #Saving seminar object
            #Otherwise just create the seminar object
            else:
                SeminarD.save()#Saving seminar object
            #Returning user to dashboard
            return redirect('/')
    else:
        #if user not signed in, user will be directed to dashboard
        messages.success(request, ("You need to Sign In to use this service."))
    #Calling Manage Seminar page
    return render(request, "ManageSeminar/seminar.html")

@login_required(login_url="/landPage")
#Part of Manage Review Function
def reviewDash(request):
    #Calling logged user
    semUsser = User.objects.get(id=request.user.id)
    #Calling all seminar that has been created by user
    uSeminar = semUsser.seminar_set.all()
    qSeminar = semUsser.seminarq_set.all()
    #Creating Pagination
    #Calling seminar that user had joined 
    revPage = Paginator(semUsser.receipt_set.all(), 6)
    rPage = request.GET.get('page')
    revSem = revPage.get_page(rPage)
    #Displaying all joined seminar and user's seminar
    context = {
        "seminar_list": revSem, "my_seminar":uSeminar,
        "pending_seminar": qSeminar,
    }       
    return render(request, "ManageReview/reviewDashboard.html", context)

@login_required(login_url="/landPage")
#Manage Review Function
def revForms(request, semJoID):
    #Calling receipt models connected to the user clicked
    semiID = receipt.objects.get(id = semJoID)
    #POST method to create review object
    if request.method == "POST":
        #calling variable from the html
        rev_rates = request.POST['rates']
        feeds = request.POST['reviewSem']
        #Creating review object
        userJoin = User.objects.get(id=request.user.id)
        rev_create = review.objects.create(revUser = userJoin,
                                           semiRevInfo=semiID.semInfo,
                                           ratings = rev_rates,
                                           feedback = feeds)
        #Save review model and redirecting to review dashboard
        rev_create.save()
        return redirect('/reviewDash')
    #Returing receipt component that is relevant to the review
    context = {'seminar_info':semiID}  
    return render(request, "ManageReview/reviewForm.html", context)

@login_required(login_url="/landPage")
#Part of Manage Review for Organizer
def organizerDash(request, orgaID):
    #Calling seminar that will be displayed
    semiOID = seminar.objects.get(id=orgaID)
    loReview = semiOID.review_set.all()
    pendList = semiOID.seminarq_set.all()
    #Pagination setter
    orgaPage = Paginator(semiOID.receipt_set.all(), 8)
    oPage = request.GET.get('page')
    loUser = orgaPage.get_page(oPage)
    
    #Displaying seminar while returning seminar, receipt and review object
    context = {
        'pageload': semiOID, 'user_list': loUser,
        'review_list': loReview, 'queue_list': pendList,
    }
    return render(request, "ManageReview/seminarManage.html", context)

@login_required(login_url="/landPage")
#Part of Manage Review for Organizer
def orgaUserView(request, uID):
    #calling review that has been clicked by Organizer
    revID = review.objects.get(id=uID)
    #Displaying and returning review object
    context = {'user_review': revID}
    return render(request, "ManageReview/feedbackU.html", context)
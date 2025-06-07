from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dash, name = 'dashboard'),
    path('landPage', views.landPage, name='landingPage'),
    path('manageuser', views.manageUser, name = 'manageuser'),
    path('authuser', views.authenticateUser, name = 'authuser'),
    path('signOut', views.signOut, name = 'signOut'),
    path('manageprof', views.manageProf, name ='manageProf'),
    path('manageseminar', views.manageSeminar, name ='manageSem'),
    path('pInfoSeminar/<str:semID>/', views.pSemInfo, name ='pInfoSeminar'),
    path('sempdf', views.pSemInfo, name ='sempdf'),
    path('reviewDash', views.reviewDash, name='revDash'),
    path('viewtix/<str:userTix>/', views.viewTix, name ='viewtix'),
    path('semiReview/<str:semJoID>/', views.revForms, name = 'semiReviewForm'),
    path('orgaSeminar/<str:orgaID>/', views.organizerDash, name = 'orgaSeminar'),
    path('orgaUserRev/<str:uID>/', views.orgaUserView, name = 'orgaUserRev'),
    path('uQueue/<str:passID>/', views.viewUQueue, name = 'uQueue'),    
]


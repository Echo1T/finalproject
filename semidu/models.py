from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw


# Create your models here.
class seminar(models.Model):
    seminar_name = models.CharField(max_length=225, null=True)
    seminar_purpose = models.CharField(max_length=225, null=True)
    amount_peoples = models.IntegerField(null=True)
    joined_user = models.IntegerField(default=0, blank=True)
    seminar_contact = models.CharField(max_length=225, null=True)
    seminar_req = models.CharField(max_length=225, null=True)
    semiUser = models.ForeignKey(User, null=True, on_delete= models.SET_NULL)
    
class semPay(models.Model):
    semiRelation = models.ForeignKey(seminar, null=True, on_delete= models.SET_NULL)
    semiMethod = models.CharField(max_length=225, null=True)
    payAmount = models.IntegerField(default=0, blank=True)
    serialNum = models.CharField(max_length=225, null=True)
    
    
class seminarQ(models.Model):
    semName = models.ForeignKey(seminar, null=True, on_delete= models.SET_NULL)
    joinUser = models.ForeignKey(User, null=True, on_delete= models.SET_NULL)
    reasontoJoin = models.TextField(null=True)
    status_req = models.CharField(max_length=225, null=True)
    proofPic = models.ImageField(upload_to='imgProof', blank=True)

class receipt(models.Model):
    receiptInfo = models.CharField(max_length=225, null=True)
    semUs = models.ForeignKey(User, null=True, on_delete= models.SET_NULL)
    semInfo = models.ForeignKey(seminar, null=True, on_delete= models.SET_NULL)
    
    qrCD = models.ImageField(upload_to='qrCD', blank=True)
    
    
    def __str__(self):
        return str(self.receiptInfo)
    
    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make("Username: "+self.semUs.username+"\nSeminar Name: "+self.semInfo.seminar_name+
                                 "\nSeminar Description: "+self.semInfo.seminar_purpose+"\nSeminar Contact: "+ self.semInfo.seminar_contact)
        fname = f'QRCode-{self.semUs.username}-{self.semInfo.seminar_name}.png'
        buffer = BytesIO()
        qrcode_img.save(buffer,'PNG')
        self.qrCD.save(fname, File(buffer), save=False)
        super().save(*args, **kwargs)
        
class review(models.Model):
    revUser = models.ForeignKey(User, null=True, on_delete= models.SET_NULL)
    semiRevInfo = models.ForeignKey(seminar, null=True, on_delete= models.SET_NULL)
    ratings = models.IntegerField(null=True)
    feedback = models.TextField(null=True)
    
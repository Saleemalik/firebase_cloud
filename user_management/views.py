import pyrebase
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
import requests
import json


config = {
    "apiKey": "AIzaSyDVEg7K_RKDtsHecSwugnXm4HtKo6Nr2V8",
    "authDomain": "user-management-5d31b.firebaseapp.com",
    "projectId": "user-management-5d31b",
    "storageBucket": "user-management-5d31b.appspot.com",
    "messagingSenderId": "813981171752",
    "appId": "1:813981171752:web:83885b6ace05daadb2751d",
    "measurementId": "G-T8G2Q10Z4J",
    "databaseURL": "https://user-management-5d31b-default-rtdb.firebaseio.com/",
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()

def login(request):
    if "uid" in request.session:
        return redirect('user')
    else:
        if request.method == 'POST':
            email = request.POST['email']

            password = request.POST['password']

            try:
                user = auth.sign_in_with_email_and_password(email, password)
                uid = user['localId']
                user_token = user['idToken']
                request.session['u_token'] = str(user_token)
                request.session['uid']=str(uid)
                return JsonResponse('true', safe=False)
            except:
                return JsonResponse('false', safe=False)
            
        return render(request, 'login.html')

def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user=auth.create_user_with_email_and_password(email,password1)
                user = auth.sign_in_with_email_and_password(email, password1)
                
                
                uid = user['localId']
                request.session['uid']=str(uid)

                data = {"name": name} 
               
                db.child("users").child(uid).child('details').set(data)
                
                # print(user) 
                # uid = user['localId']
                # idtoken = request.session[uid]
                return JsonResponse('true', safe=False)
            except requests.HTTPError as e:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                if error == "EMAIL_EXISTS":
                    return JsonResponse('false2', safe=False)
            except json.decoder.JSONDecodeError as e:
                
                
                return JsonResponse('false1', safe=False)

        else:
            return JsonResponse('false3', safe=False)
    return render(request, 'register.html')

def userh(request):
    if "uid" in request.session:
        uid= request.session['uid'] 
        
        token = request.session['u_token']
    
        if request.method == "POST":
            name = request.POST["name"]
            DOB = request.POST['dob']
            address = request.POST.get('address')
            photo = request.FILES.get('photo')

            print("ok", name, DOB, address, photo)
            if name != '':
                db.child("users").child(uid).child('details').update({"name" : name})
            if DOB != '':
                db.child("users").child(uid).child('details').update({"DOB" : DOB})
            if address != '':
                db.child("users").child(uid).child('details').update({"address" : address})
            if photo is not None:
                storage.child("users").child(uid).child('user_photo').put(photo)

                url = storage.child("users").child(uid).child('user_photo').get_url(token)
                db.child("users").child(uid).child('details').update({"photo" : url})

        
                
        
        details = db.child("users").child(uid).child('details').get().val()

        context = {
            "details" : details
        }

        return render(request, 'userh.html', context)
    else:
        return redirect('login')

def reset_password(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            auth.send_password_reset_email(email)
            return JsonResponse("true", safe=False)
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            if error == "EMAIL_NOT_FOUND":
                    return JsonResponse('false', safe=False)


    return render(request, 'reset.html')



def logout(request):
    try:
        del request.session['uid']
        del request.session['u_token']
    except:
        pass
    return redirect("login")
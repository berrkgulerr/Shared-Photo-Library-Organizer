import decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .models import *
from .forms import CreateUserForm
from photos.consumers import SockConsumer


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        context = {'form': form}
        return render(request, 'photos/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'photos/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    user = request.user
    collections = Collection.objects.filter(collection_owner_id=user.id)
    views = View.objects.filter(view_owner_id=user.id)
    shared_collections = user.collection_set.all()
    shared_views = user.view_set.all()
    context = {'collections': collections, 'views': views,
               'shared_collections': shared_collections, 'shared_views': shared_views}

    return render(request, 'photos/dashboard.html', context)


@login_required(login_url='login')
def addCollection(request):
    user = request.user
    if request.method == 'POST':
        name1 = request.POST['name']
        mycollection = Collection.objects.create(
            name=name1,
            collection_owner_id=user.id
        )
        data = {'mycol_id': mycollection.id, 'mycol_name': mycollection.name}
        return JsonResponse(data)


def addPhotoToView(myviews, photo):
    photo_tags = []
    for tag in photo.tags.all():
        photo_tags.append(tag.name)

    for view in myviews:
        view_tagList = []
        for tag in view.tags.all():
            view_tagList.append(tag.name)
        if view.conjunctive:
            if all(elem in photo_tags for elem in view_tagList):
                if (view.startTime <= photo.datetime <= view.endTime) and (
                        view.startLatitude <= photo.latitude <= view.endLatitude) and (
                        view.startLongitude <= photo.longitude <= view.endLongitude):
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
                    view.save()
        else:
            if any(x in photo_tags for x in view_tagList):
                if view.startTime <= photo.datetime <= view.endTime and \
                        view.startLatitude <= photo.latitude <= view.endLatitude and \
                        view.startLongitude <= photo.longitude <= view.endLongitude:
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
                    view.save()


@login_required(login_url='login')
def addPhoto(request):
    myuser = request.user
    pk = request.POST.get("collection_id")
    mycollection = Collection.objects.get(pk=pk)
    users = []
    for user in mycollection.shared_users.all():
        users.append(user.id)
    if myuser.id != mycollection.collection_owner_id:
        if myuser.id in users:
            users.remove(myuser.id)
        users.append(mycollection.collection_owner_id)

    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    data = request.POST
    image = request.FILES.get('photo_image')
    photo = Photo.objects.create(
        name=data['photo_name'],
        image=image,
        latitude=decimal.Decimal(data['photo_latitude']),
        longitude=decimal.Decimal(data['photo_longitude']),
        datetime=parse_date(data['photo_datetime']),
        photo_owner_id=myuser.id,
        collection_id=mycollection.id
    )
    tags = data['photo_tags']
    tagslist = [str(r) for r in tags.split(',')]
    for tag in tagslist:
        if not Tag.objects.filter(name=tag).exists():
            newTag = Tag.objects.create(name=tag)
            photo.tags.add(newTag)
        else:
            photo.tags.add(Tag.objects.get(name=tag))
    photo.save()
    mycollection.photos.add(photo)
    mycollection.save()

    myviews = View.objects.filter(collection_id=pk).all()
    addPhotoToView(myviews, photo)
    data1 = {'photo_id': photo.id, 'photo_name': photo.name, 'success': True, 'url': photo.image.url,
             'tags': tags, 'lat': data['photo_latitude'], 'long': data['photo_longitude'],
             'date': data['photo_datetime']}

    item = {'photo_id': photo.id, 'photo_name': photo.name, 'photo_url': photo.image.url,
            'photo_tags': tags, 'photo_lat': str(photo.latitude), 'photo_long': str(photo.longitude),
            'photo_date': photo.datetime.isoformat()}
    SockConsumer.broadcast(users, {
        "op": "add_photo",
        "message": "Photo with name \"" + photo.name + "\" is added by " + request.user.username,
        "item": item,
    })

    return JsonResponse(data1)


@login_required(login_url='login')
def addView(request):
    myuser = request.user
    pk = request.POST.get("collection_id")
    mycollection = Collection.objects.get(pk=pk)
    users = []
    owner = "true"
    for user in mycollection.shared_users.all():
        users.append(user.id)
    if myuser.id != mycollection.collection_owner_id:
        owner = "false"
        if myuser.id in users:
            users.remove(myuser.id)
        users.append(mycollection.collection_owner_id)
    data1 = {'message': None}
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    data = request.POST
    view = View.objects.create(
        name=data['view_name'],
        startLatitude=data['view_startLatitude'],
        startLongitude=data['view_startLongitude'],
        endLatitude=data['view_endLatitude'],
        endLongitude=data['view_endLongitude'],
        startTime=parse_date(data['view_startTime']),
        endTime=parse_date(data['view_endTime']),
        view_owner_id=myuser.id,
        collection_id=mycollection.id,
        collection_name=mycollection.name
    )
    if data['view_conjunctive'] == 'Conjunctive':
        view.conjunctive = True
    else:
        view.conjunctive = False

    tags = data['view_tags']
    tagslist = [str(r) for r in tags.split(',')]
    for tag in tagslist:
        if not Tag.objects.filter(name=tag).exists():
            newTag = Tag.objects.create(name=tag)
            view.tags.add(newTag)
        else:
            view.tags.add(Tag.objects.get(name=tag))

    filtered_photos = Photo.objects.filter(collection_id=pk, datetime__range=(view.startTime, view.endTime),
                                           latitude__range=(view.startLatitude, view.endLatitude),
                                           longitude__range=(view.startLongitude, view.endLongitude))
    if view.conjunctive:
        for photo in filtered_photos:
            photo_tags = []
            for tag in photo.tags.all():
                photo_tags.append(tag.name)
            if all(elem in photo_tags for elem in tagslist):
                view.photos.add(photo)
                newViewId = View_ids_of_photo.objects.create(iid=view.id)
                photo.view_id.add(newViewId)
                photo.save()
    else:
        for photo in filtered_photos:
            photo_tags = []
            for tag in photo.tags.all():
                photo_tags.append(tag.name)
            if any(x in photo_tags for x in tagslist):
                view.photos.add(photo)
                newViewId = View_ids_of_photo.objects.create(iid=view.id)
                photo.view_id.add(newViewId)
                photo.save()
    for user in mycollection.shared_users.all():
        view.shared_users.add(user)
    if myuser.id != mycollection.collection_owner_id:
        owner = "false"
        if myuser in view.shared_users.all():
            view.shared_users.remove(myuser)
        view.shared_users.add(User.objects.get(id=mycollection.collection_owner_id))
    view.save()
    mycollection.views.add(view)
    mycollection.save()
    data1['message'] = 'View created'
    item = {'view_id': view.id, 'view_name': view.name, 'view_tags': tags, 'view_collection_name': mycollection.name,
            'view_conjunctive': view.conjunctive,
            'view_startLatitude': str(view.startLatitude), 'view_endLatitude': str(view.endLatitude),
            'view_startLongitude': str(view.startLongitude), 'view_endLongitude': str(view.endLongitude),
            'view_startTime': view.startTime.isoformat(), 'view_endTime': view.endTime.isoformat(),
            'view_collectionName': view.collection_name, 'view_photoCount': view.photos.count()}

    SockConsumer.broadcast(users, {
        "op": "add_view",
        "message": "View with name \"" + view.name + "\" is created by " + request.user.username,
        "item": item,
    })
    return JsonResponse(data1)


@login_required(login_url='login')
def updatePhoto(request):
    pk = request.POST.get("pphoto-id")
    myuser = request.user
    photo = Photo.objects.get(id=pk)
    mycollection = Collection.objects.get(id=photo.collection_id)
    users = []
    for user in mycollection.shared_users.all():
        users.append(user.id)
    if myuser.id != mycollection.collection_owner_id:
        if myuser.id in users:
            users.remove(myuser.id)
        users.append(mycollection.collection_owner_id)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    myviews = []
    for viewID in photo.view_id.all():
        if View.objects.filter(id=viewID.iid).exists():
            myviews.append(View.objects.get(id=viewID.iid))
    for view in myviews:
        view.photos.remove(photo)

    data = request.POST
    photo.name = data['pphoto_name']
    photo.latitude = decimal.Decimal(data['pphoto_latitude'])
    photo.longitude = decimal.Decimal(data['pphoto_longitude'])
    photo.datetime = parse_date(data['pphoto_datetime'])
    photo.tags.clear()
    photo.view_id.clear()
    tags = data['pphoto_tags']
    tagslist = [str(r) for r in tags.split(',')]
    for tag in tagslist:
        if not Tag.objects.filter(name=tag).exists():
            newTag = Tag.objects.create(name=tag)
            photo.tags.add(newTag)
        else:
            photo.tags.add(Tag.objects.get(name=tag))
    photo.save()
    myviews = View.objects.filter(collection_id=mycollection.id).all()
    addPhotoToView(myviews, photo)

    data1 = {'photo_id': photo.id, 'photo_name': photo.name, 'success': True, 'url': photo.image.url,
             'tags': tags, 'lat': photo.latitude, 'long': photo.longitude,
             'date': photo.datetime}
    item = {'photo_id': photo.id, 'photo_name': photo.name, 'photo_url': photo.image.url,
            'photo_tags': tags, 'photo_lat': str(photo.latitude), 'photo_long': str(photo.longitude),
            'photo_date': photo.datetime.isoformat()}
    SockConsumer.broadcast(users, {
        "op": "update_photo",
        "message": "Photo with name \"" + photo.name + "\" is updated by " + request.user.username,
        "item": item,
    })
    return JsonResponse(data1)


@login_required(login_url='login')
def updateView(request):
    pk = request.POST.get("vview-id")
    view = View.objects.get(id=pk)
    if request.user.id != view.view_owner_id:
        return redirect('home')
    mycollection = Collection.objects.get(id=view.collection_id)
    myphotos = view.photos.all()
    for photo in myphotos:
        photo.view_id.clear()
        photo.save()
    users = []
    for user in view.shared_users.all():
        users.append(user.id)
    data = request.POST
    view.name = data['vview_name']
    view.startLatitude = decimal.Decimal(data['vview_startLatitude'])
    view.startLongitude = decimal.Decimal(data['vview_startLongitude'])
    view.endLatitude = decimal.Decimal(data['vview_endLatitude'])
    view.endLongitude = decimal.Decimal(data['vview_endLongitude'])
    view.startTime = parse_date(data['vview_startTime'])
    view.endTime = parse_date(data['vview_endTime'])
    view.tags.clear()
    view.photos.clear()
    if data['vview_conjunctive'] == 'Conjunctive':
        view.conjunctive = True
    else:
        view.conjunctive = False
    tags = data['vview_tags']
    tagslist = [str(r) for r in tags.split(',')]
    for tag in tagslist:
        if not Tag.objects.filter(name=tag).exists():
            newTag = Tag.objects.create(name=tag)
            view.tags.add(newTag)
        else:
            view.tags.add(Tag.objects.get(name=tag))

    filtered_photos = Photo.objects.filter(collection_id=mycollection.id,
                                           datetime__range=(view.startTime, view.endTime),
                                           latitude__range=(view.startLatitude, view.endLatitude),
                                           longitude__range=(view.startLongitude, view.endLongitude))
    if view.conjunctive:
        for photo in filtered_photos:
            photo_tags = []
            for tag in photo.tags.all():
                photo_tags.append(tag.name)
            if all(elem in photo_tags for elem in tagslist):
                view.photos.add(photo)
                newViewId = View_ids_of_photo.objects.create(iid=view.id)
                photo.view_id.add(newViewId)
                photo.save()
    else:
        for photo in filtered_photos:
            photo_tags = []
            for tag in photo.tags.all():
                photo_tags.append(tag.name)
            if any(x in photo_tags for x in tagslist):
                view.photos.add(photo)
                newViewId = View_ids_of_photo.objects.create(iid=view.id)
                photo.view_id.add(newViewId)
                photo.save()
    view.save()

    data1 = {'view_id': view.id, 'view_name': view.name, 'view_tags': tags, 'view_conjunctive': view.conjunctive,
             'view_startLatitude': view.startLatitude, 'view_endLatitude': view.endLatitude,
             'view_startLongitude': view.startLongitude,
             'view_endLongitude': view.endLongitude, 'view_startTime': view.startTime, 'view_endTime': view.endTime,
             'view_collectionName': view.collection_name, 'view_photoCount': view.photos.count()}

    item = {'view_id': view.id, 'view_name': view.name, 'view_tags': tags, 'view_collection_name': mycollection.name,
            'view_conjunctive': view.conjunctive,
            'view_startLatitude': str(view.startLatitude), 'view_endLatitude': str(view.endLatitude),
            'view_startLongitude': str(view.startLongitude), 'view_endLongitude': str(view.endLongitude),
            'view_startTime': view.startTime.isoformat(), 'view_endTime': view.endTime.isoformat(),
            'view_collectionName': view.collection_name, 'view_photoCount': view.photos.count()}

    SockConsumer.broadcast(users, {
        "op": "update_view",
        "message": "View with name \"" + view.name + "\" is updated by " + request.user.username,
        "item": item,
    })
    return JsonResponse(data1)


@login_required(login_url='login')
def viewCollection(request, pk):
    myuser = request.user
    mycollection = Collection.objects.get(id=pk)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    myphotos = Photo.objects.filter(collection_id=mycollection.id)
    myviews = View.objects.filter(collection_id=mycollection.id)
    context = {'myuser': myuser, 'mycollection': mycollection, 'myphotos': myphotos, 'myviews': myviews}
    return render(request, 'photos/viewCollection.html', context)


@login_required(login_url='login')
def viewView(request, pk):
    myuser = request.user
    myview = View.objects.get(pk=pk)
    myphotos = myview.photos.all()
    for photo in myphotos:
        photo.current_view_id = pk
        photo.save()
    if request.user.id != myview.view_owner_id and request.user not in myview.shared_users.all():
        return redirect('home')
    myphotos = myview.photos.all()

    mycollection = Collection.objects.get(pk=myview.collection_id)
    context = {'myuser': myuser, 'myphotos': myphotos, 'myview': myview, 'mycollection': mycollection}
    return render(request, 'photos/viewView.html', context)


@login_required(login_url='login')
def deletePhoto(request):
    data = {'success': False}
    pk = request.POST['photo_id']
    myuser = request.user
    mycollection = Collection.objects.get(pk=Photo.objects.get(id=pk).collection_id)
    users = []
    for user in mycollection.shared_users.all():
        users.append(user.id)
    if myuser.id != mycollection.collection_owner_id:
        if myuser.id in users:
            users.remove(myuser.id)
        users.append(mycollection.collection_owner_id)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    item = {'photo_id': pk, 'photo_name': Photo.objects.get(id=pk).name}
    Photo.objects.get(id=pk).delete()
    data['success'] = True

    SockConsumer.broadcast(users, {
        "op": "delete_photo",
        "message": "Photo with name \"" + item["photo_name"] + "\" is deleted by " + request.user.username,
        "item": item,
    })
    return JsonResponse(data)


@login_required(login_url='login')
def deleteCollection(request):
    data = {'success': False}
    pk = request.POST['collection_id']
    mycollection = Collection.objects.get(pk=pk)
    users = []
    for user in mycollection.shared_users.all():
        users.append(user.id)
    item = {"collection_id": mycollection.id}
    if request.user.id != mycollection.collection_owner_id:
        return JsonResponse(data)
    Photo.objects.filter(collection_id=pk).delete()
    views = View.objects.filter(collection_id=pk).all()
    view_ids = []
    for view in views:
        view_ids.append(view.id)
    View.objects.filter(collection_id=pk).delete()
    Collection.objects.filter(pk=pk).delete()
    data['success'] = True
    data['view_ids'] = view_ids

    SockConsumer.broadcast(users, {
        "op": "delete_col",
        "message": "Collection with name \"" + mycollection.name + "\" is deleted by " + request.user.username,
        "item": item,
    })
    return JsonResponse(data)


@login_required(login_url='login')
def deleteView(request):
    data = {'success': False}
    pk = request.POST['view_id']
    myview = View.objects.get(pk=pk)
    users = []
    for user in myview.shared_users.all():
        users.append(user.id)
    item = {"view_id": myview.id}
    if request.user.id != myview.view_owner_id:
        return redirect('home')
    View.objects.filter(pk=pk).delete()
    data['success'] = True

    SockConsumer.broadcast(users, {
        "op": "delete_view",
        "message": "View with name \"" + myview.name + "\" is deleted by " + request.user.username,
        "item": item,
    })
    return JsonResponse(data)


@login_required(login_url='login')
def shareCollection(request):
    data = {'success': False, 'myusername': ""}
    pk = request.POST['collection_id']
    mycollection = Collection.objects.get(pk=pk)
    username = request.POST['username']
    if request.user.id != mycollection.collection_owner_id:
        return JsonResponse(data)
    if User.objects.filter(username=username).exists():
        shared_user = User.objects.get(username=username)
        myviews = mycollection.views.all()
        for view in myviews:
            if not view.shared_users.contains(shared_user):
                view.shared_users.add(shared_user)
        if not mycollection.shared_users.contains(shared_user):
            mycollection.shared_users.add(shared_user)
        data['myusername'] = username
        data['success'] = True
        users = [shared_user.id]
        item = {"collection_id": mycollection.id, "collection_name": mycollection.name,
                "photo_count": mycollection.photos.count(), "view_count": mycollection.views.count()}
        SockConsumer.broadcast(users, {
            "op": "share_col",
            "message": "Collection with name \"" + mycollection.name + "\" is shared by " + request.user.username,
            "item": item,
        })
    return JsonResponse(data)


@login_required(login_url='login')
def unshareCollection(request):
    data = {'success': False, 'myusername': ""}
    pk = request.POST['collection_id']
    mycollection = Collection.objects.get(pk=pk)
    if request.user.id != mycollection.collection_owner_id:
        return JsonResponse(data)
    if request.method == 'POST':
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            unshared_user = User.objects.get(username=username)
            myviews = mycollection.views.all()
            for view in myviews:
                if view.shared_users.contains(unshared_user):
                    view.shared_users.remove(unshared_user)
            if mycollection.shared_users.contains(unshared_user):
                mycollection.shared_users.remove(unshared_user)
            data['myusername'] = username
            data['success'] = True
            users = [unshared_user.id]
            item = {"collection_id": mycollection.id}
            SockConsumer.broadcast(users, {
                "op": "unshare_col",
                "message": "Collection with name \"" + mycollection.name + "\" is unshared by " + request.user.username,
                "item": item,
            })
    return JsonResponse(data)


@login_required(login_url='login')
def shareView(request):
    data1 = {'success': False, 'myusername': ""}
    pk = request.POST['view_id']
    myview = View.objects.get(id=pk)
    if request.user.id != myview.view_owner_id:
        return JsonResponse(data1)
    data = request.POST
    username = data['username']
    if User.objects.filter(username=username).exists():
        shared_user = User.objects.get(username=username)
        if not myview.shared_users.contains(shared_user):
            myview.shared_users.add(shared_user)
        data1['myusername'] = username
        data1['success'] = True
        users = [shared_user.id]
        tags = ""
        for tag in myview.tags.all():
            if tag == myview.tags.all().last():
                tags += tag.name
            else:
                tags += tag.name + ", "

        item = {'view_id': myview.id, 'view_name': myview.name, 'view_tags': tags,
                'view_conjunctive': myview.conjunctive,
                'view_startLatitude': str(myview.startLatitude), 'view_endLatitude': str(myview.endLatitude),
                'view_startLongitude': str(myview.startLongitude), 'view_endLongitude': str(myview.endLongitude),
                'view_startTime': myview.startTime.isoformat(), 'view_endTime': myview.endTime.isoformat(),
                'view_collectionName': myview.collection_name, 'view_photoCount': myview.photos.count()}
        SockConsumer.broadcast(users, {
            "op": "share_view",
            "message": "View with name \"" + myview.name + "\" is shared by " + request.user.username,
            "item": item,
        })
    return JsonResponse(data1)


@login_required(login_url='login')
def unshareView(request):
    data1 = {'success': False, 'myusername': ""}
    pk = request.POST['view_id']
    myview = View.objects.get(id=pk)
    if request.user.id != myview.view_owner_id:
        return JsonResponse(data1)
    if request.method == 'POST':
        data = request.POST
        username = data['username']
        if User.objects.filter(username=username).exists():
            unshared_user = User.objects.get(username=username)
            if myview.shared_users.contains(unshared_user):
                myview.shared_users.remove(unshared_user)
            data1['myusername'] = username
            data1['success'] = True
            users = [unshared_user.id]
            tags = ""
            for tag in myview.tags.all():
                tags += tag.name + ", "
            item = {'view_id': myview.id, }
            SockConsumer.broadcast(users, {
                "op": "unshare_view",
                "message": "View with name \"" + myview.name + "\" is unshared by " + request.user.username,
                "item": item,
            })
    return JsonResponse(data1)

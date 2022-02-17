import decimal

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .models import *
from .forms import CreateUserForm


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
    shared_collections = user.collection_set.all()
    shared_views = user.view_set.all()
    context = {'collections': collections, 'shared_collections': shared_collections, 'shared_views': shared_views}

    return render(request, 'photos/dashboard.html', context)


@login_required(login_url='login')
def addCollection(request):
    user = request.user
    if request.method == 'POST':
        data = request.POST
        mycollection = Collection.objects.create(
            name=data['collection_name'],
            collection_owner_id=user.id
        )
        return redirect('home')
    return render(request, 'photos/addCollection.html')


def addPhotoToView(myviews, photo):
    photo_tags = []
    for tag in photo.tags.all():
        photo_tags.append(tag.name)

    for view in myviews:
        view_tagList = []
        for tag in view.tags.all():
            view_tagList.append(tag.name)
        if view.conjunctive:
            if all(elem in view_tagList for elem in photo_tags):
                if (view.startTime <= photo.datetime <= view.endTime) and (
                        view.startLatitude <= photo.latitude <= view.endLatitude) and (
                        view.startLongitude <= photo.longitude <= view.endLongitude):
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
                    view.save()
        else:
            if any(x in view_tagList for x in photo_tags):
                if view.startTime <= photo.datetime <= view.endTime and view.startLatitude <= photo.latitude <= view.endLatitude and view.startLongitude <= photo.longitude <= view.endLongitude:
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
                    view.save()


@login_required(login_url='login')
def addPhoto(request, pk):
    myuser = request.user
    mycollection = Collection.objects.get(pk=pk)
    ###############################################################################################
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    ###############################################################################################
    if request.method == 'POST':
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

        return redirect('view_collection', pk)
    context = {'myuser': myuser, 'mycollection': mycollection, 'pk': pk}
    return render(request, 'photos/addPhoto.html', context)


@login_required(login_url='login')
def addView(request, pk):
    myuser = request.user
    mycollection = Collection.objects.get(pk=pk)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    if request.method == 'POST':
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
            collection_id=mycollection.id
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
                if all(elem in tagslist for elem in photo_tags):
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
        else:
            for photo in filtered_photos:
                photo_tags = []
                for tag in photo.tags.all():
                    photo_tags.append(tag.name)
                if any(x in tagslist for x in photo_tags):
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
        view.save()
        mycollection.views.add(view)
        mycollection.save()

        return redirect('view_collection', pk)
    context = {'myuser': myuser, 'mycollection': mycollection, 'pk': pk}
    return render(request, 'photos/addView.html', context)


@login_required(login_url='login')
def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    mycollection = Collection.objects.get(id=photo.collection_id)
    myviews = []
    for view in photo.view_id.all():
        if View.objects.filter(id=view.iid).exists():
            myviews.append(View.objects.get(id=view.iid))
    flag = 1
    for view in myviews:
        if request.user in view.shared_users.all():
            flag = 0
            break
    print(flag)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all() and flag:
        return redirect('home')
    context = {'photo': photo, 'mycollection': mycollection}
    return render(request, 'photos/viewPhoto.html', context)


@login_required(login_url='login')
def viewPhotoView(request, pk):
    photo = Photo.objects.get(id=pk)
    mycollection = Collection.objects.get(id=photo.collection_id)
    myviews = []
    for view in photo.view_id.all():
        if View.objects.filter(id=view.iid).exists():
            myviews.append(View.objects.get(id=view.iid))
    flag = 1
    for view in myviews:
        if request.user in view.shared_users.all():
            flag = 0
            break
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all() and flag:
        return redirect('home')
    context = {'photo': photo, 'mycollection': mycollection, 'current_view': photo.current_view_id}
    return render(request, 'photos/viewPhotoView.html', context)


@login_required(login_url='login')
def updatePhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    mycollection = Collection.objects.get(id=photo.collection_id)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    myviews = []
    for viewID in photo.view_id.all():
        if View.objects.filter(id=viewID.iid).exists():
            myviews.append(View.objects.get(id=viewID.iid))
    for view in myviews:
        view.photos.remove(photo)

    if request.method == 'POST':
        data = request.POST
        photo.name = data['photo_name']
        photo.latitude = decimal.Decimal(data['photo_latitude'])
        photo.longitude = decimal.Decimal(data['photo_longitude'])
        photo.datetime = parse_date(data['photo_datetime'])
        photo.tags.clear()
        photo.view_id.clear()
        tags = data['photo_tags']
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
        return redirect('view_collection', mycollection.id)

    context = {'mycollection': mycollection, 'photo': photo}
    return render(request, 'photos/updatePhoto.html', context)


@login_required(login_url='login')
def updateView(request, pk):
    view = View.objects.get(id=pk)
    if request.user.id != view.view_owner_id:
        return redirect('home')
    mycollection = Collection.objects.get(id=view.collection_id)
    myphotos = view.photos.all()
    for photo in myphotos:
        photo.view_id.clear()
        photo.save()

    if request.method == 'POST':
        data = request.POST
        view.name = data['view_name']
        view.startLatitude = decimal.Decimal(data['view_startLatitude'])
        view.startLongitude = decimal.Decimal(data['view_startLongitude'])
        view.endLatitude = decimal.Decimal(data['view_endLatitude'])
        view.endLongitude = decimal.Decimal(data['view_endLongitude'])
        view.startTime = parse_date(data['view_startTime'])
        view.endTime = parse_date(data['view_endTime'])
        view.tags.clear()
        view.photos.clear()
        tags = data['view_tags']
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
                if all(elem in tagslist for elem in photo_tags):
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
        else:
            for photo in filtered_photos:
                photo_tags = []
                for tag in photo.tags.all():
                    photo_tags.append(tag.name)
                if any(x in tagslist for x in photo_tags):
                    view.photos.add(photo)
                    newViewId = View_ids_of_photo.objects.create(iid=view.id)
                    photo.view_id.add(newViewId)
                    photo.save()
        view.save()
        return redirect('dashboard_views', mycollection.id)

    context = {'mycollection': mycollection, 'view': view}
    return render(request, 'photos/updateView.html', context)


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
def dashboard_views(request, pk):
    myuser = request.user
    mycollection = Collection.objects.get(pk=pk)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    myviews = View.objects.filter(collection_id=pk)
    context = {'myviews': myviews, 'myuser': myuser, 'mycollection': mycollection}
    return render(request, 'photos/dashboard_views.html', context)


@login_required(login_url='login')
def deletePhoto(request, pk):
    mycollection = Collection.objects.get(pk=Photo.objects.get(id=pk).collection_id)
    if request.user.id != mycollection.collection_owner_id and request.user not in mycollection.shared_users.all():
        return redirect('home')
    myphotos = Photo.objects.filter(collection_id=mycollection.id)
    Photo.objects.get(id=pk).delete()
    context = {'mycollection': mycollection, 'myphotos': myphotos}
    return render(request, 'photos/viewCollection.html', context)


@login_required(login_url='login')
def deleteCollection(request, pk):
    mycollection = Collection.objects.get(pk=pk)
    if request.user.id != mycollection.collection_owner_id:
        return redirect('home')
    Photo.objects.filter(collection_id=pk).delete()
    View.objects.filter(collection_id=pk).delete()
    Collection.objects.filter(pk=pk).delete()
    return render(request, 'photos/dashboard.html')


@login_required(login_url='login')
def deleteView(request, pk):
    myview = View.objects.get(pk=pk)
    if request.user.id != myview.view_owner_id:
        return redirect('home')
    mycollection = Collection.objects.get(id=myview.collection_id)
    context = {'mycollection': mycollection}
    View.objects.filter(pk=pk).delete()
    return render(request, 'photos/dashboard_views.html', context)


@login_required(login_url='login')
def shareCollection(request, pk):
    mycollection = Collection.objects.get(id=pk)
    if request.user.id != mycollection.collection_owner_id:
        return redirect('home')
    if request.method == 'POST':
        data = request.POST
        username = data['shared_unshared_username']
        if User.objects.filter(username=username).exists():
            shared_user = User.objects.get(username=username)
            myviews = mycollection.views.all()
            for view in myviews:
                if not view.shared_users.contains(shared_user):
                    view.shared_users.add(shared_user)
            if not mycollection.shared_users.contains(shared_user):
                mycollection.shared_users.add(shared_user)
        return redirect('home')
    return render(request, 'photos/share_unshare_collection.html')


@login_required(login_url='login')
def unshareCollection(request, pk):
    mycollection = Collection.objects.get(id=pk)
    if request.user.id != mycollection.collection_owner_id:
        return redirect('home')
    if request.method == 'POST':
        data = request.POST
        username = data['shared_unshared_username']
        if User.objects.filter(username=username).exists():
            unshared_user = User.objects.get(username=username)
            myviews = mycollection.views.all()
            for view in myviews:
                if view.shared_users.contains(unshared_user):
                    view.shared_users.remove(unshared_user)
            if mycollection.shared_users.contains(unshared_user):
                mycollection.shared_users.remove(unshared_user)
        return redirect('home')
    return render(request, 'photos/share_unshare_collection.html')


@login_required(login_url='login')
def shareView(request, pk):
    myview = View.objects.get(id=pk)
    if request.user.id != myview.view_owner_id:
        return redirect('home')
    if request.method == 'POST':
        data = request.POST
        username = data['shared_unshared_username']
        if User.objects.filter(username=username).exists():
            unshared_user = User.objects.get(username=username)
            if not myview.shared_users.contains(unshared_user):
                myview.shared_users.add(unshared_user)
        return redirect('home')
    return render(request, 'photos/share_unshare_collection.html')


@login_required(login_url='login')
def unshareView(request, pk):
    myview = View.objects.get(id=pk)
    if request.user.id != myview.view_owner_id:
        return redirect('home')
    if request.method == 'POST':
        data = request.POST
        username = data['shared_unshared_username']
        if User.objects.filter(username=username).exists():
            unshared_user = User.objects.get(username=username)
            if myview.shared_users.contains(unshared_user):
                myview.shared_users.remove(unshared_user)
        return redirect('home')
    return render(request, 'photos/share_unshare_collection.html')

from flask import Flask, render_template,url_for,Response
from flask import request,flash,redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from models import User #,user_profile
from werkzeug.security import generate_password_hash, check_password_hash
from models import db,User,User_info,Blogs, User_search
from models import *
from datetime import datetime
from sqlalchemy import desc
import app
from base64 import b64encode
app=app.app
login_manager = LoginManager()
login_manager.login_view='unauthor'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()



@app.route('/', methods=['GET','POST'])
def homepage():
    user_detail=User.query.all()
    all_user=[]
    for i in user_detail:
        all_user.append(i.username)
    user_id=''
    passw=''
    if request.method=='POST':
        #print('herere')
        user_id=request.form['user_id']
        passw=request.form['pass']
        if user_id=='':
            flash('Please enter the username', category='uname')
        elif passw=='':
            flash('Please enter password' ,category='no_pass')
        
        find=User.query.filter_by(username=user_id).first()
        
        if (user_id!='' or passw!='') and find:
            
            if check_password_hash(find.password, passw):
                if request.form.get("check1"):
                    #print(request.form.get("check1"))
                    login_user(find, remember=True)

                else:
                    
                    login_user(find)
                    k="/self/"+current_user.username
                    
                    #self_profile(current_user.username)
                return redirect('/self/'+current_user.username)
                #return redirect(url_for('self_profile'))
            else:
                flash('Sorry, wrong password', category='password')
        elif(user_id!='' and passw!='') and user_id not in all_user :
            flash('User does not exist. Please ', category='signup')
    return render_template('homepage.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    a,b,c,d=0,0,0,0
    use=User.query.all()
    user_list=[]
    for us in use:
        user_list.append(us.username)
    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        username=request.form['uname']
        password=request.form['pass']
        
        
        pic=request.files['image1']
        #print(type(pic.read()))
        #print(pic.read())
        mimetype=pic.mimetype
        #print(pic.filename,'asfmaskfmaslkfas',mimetype)
        passw=generate_password_hash(password, method='SHA256')
        #print(fname,'jasfaksfjs')
        if fname=='':
            a=1
            flash('Please enter the First Name', category='error')
        elif username in user_list:
            b=1
            flash('Username already exist. Please choose a different username!',category='error')
        elif len(username)<=5:
            c=1
            flash('Username must be atleast 5 characters long', category='error')
        elif len(password)<=6:
            d=1
            flash('Please check password. Password must be atleast 6 characters long', category='error')
        elif(a!=1 and b!=1 and c!=1 and d!=1):
            try:
                
                
                new=User(first_name=fname, last_name=lname, username=username, password=passw,profile_photo=pic.read(),mimetype=mimetype)
                db.session.add(new)
                db.session.commit()
                flash('Profile created successfully! Please', category='success')

                #return redirect('/feed')
            except:
                flash('Something wrong! Please try later', category='error')


    return render_template('signup.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')
    

@app.route('/self/<string:username>', methods=['POST','GET'])
@login_required
def self_profile(username):
    #########
    #print('here')
    if username ==current_user.username:

        #print(current_user.username)
        img=b64encode(current_user.profile_photo)
        img=img.decode("UTF-8")
        #########
        images=[]
        images_with={'image':[],'title':[],'caption':[],'blogid':[]}
        nof,nofi=count_follow(current_user.username)
        #print(nofi,nof)
        

        output=Blogs.query.all()
        for i in output:
            if i.username==current_user.username:
                kk=b64encode(i.image)
                kk=kk.decode("UTF-8")
                images.append(kk)
                images_with['image'].append(kk)
                images_with['title'].append(i.title)
                images_with['caption'].append(i.caption)
                images_with['blogid'].append(i.blogid)
        if request.method=='POST':
            
            title=request.form['title']
            caption=request.form['caption']
            image=request.files['pic2']
            
            mimetype=image.mimetype
            time = datetime.now()
            #print(title,caption,mimetype,time,current_user.username)
            blog=Blogs(title=title,caption=caption,image=image.read(),time=time,username=current_user.username,mimetype=mimetype)
            try:
                db.session.add(blog)
                db.session.commit()
                bb=Blogs.query.all()
                # for i in bb:
                #     if blog.username==i.username:
                #         etc=i.blogid
                # post=Posts(post_id=etc,comment='',likes='')
                # try:
                #     db.session.add(post)
                #     db.session.commit()
                # except:
                #     return 'There has been some problem. We are working on it! Please retry'
                ab=b64encode(blog.image)
                
                ab=ab.decode("UTF-8")
                images.append(ab)
                images_with['image'].append(ab)
                images_with['title'].append(title)
                images_with['caption'].append(caption)
                images_with['blogid'].append(blog.blogid)
                # image1=b64encode(blog.image)
                # image1=image1.decode("UTF-8")
                #return render_template('profile_self.html',first_name=current_user.first_name,images=images,user=current_user.username,photo= img)
                
            except:
                return 'Something went wrong please try refreshing the page'
        
        return render_template('profile_self.html',nof=nof,nofi=nofi,
        images_with=zip(images_with['title'],images_with['caption'],images_with['image'],images_with['blogid']),
        first_name=current_user.first_name,user=current_user.username,photo= img,images=images)
    else:
        return 'You are not authorised'


@app.route('/people/<string:username>' ,methods=['POST','GET'])
def other_profile(username):
    all=User.query.all()
    id=0
    qq=User_info.query.all()

    g=0
    if current_user.username==username:
        return redirect('/self/'+username)
    for i in all:
        if i.username==username:
            id=i.id
    
    user=User.query.get(id)
    fname,lname=user.first_name,user.last_name
    uname=user.username
    img=b64encode(i.profile_photo)
    img=img.decode("UTF-8")
    #########
    nof,nofi=count_follow(username)
    images=[]
    j=1
    output=Blogs.query.all()
    idictf={}
    dictf={'title':[],'image':[],'caption':[]}
    ff=[]
    for i in qq:
        if current_user.username==i.username:
            ff.append(i.following)

    if username in ff:
        g=1
    ti,ca,im=[],[],[]
    for i in output:
        if i.username==username:
            kk=b64encode(i.image)
            kk=kk.decode("UTF-8")
            images.append(kk)
            ti.append(i.title)
            ca.append(i.caption)
            im.append(kk)
    #         dictf['caption'].append(i.caption)
    #         #dictf['image'].append(kk)
    #         dictf['title'].append(i.title)
    #         idictf[j]=(dictf)
    #         j=+1
    # print(idictf)
    # print(dictf)
    ############################
    ###CHECK FOR FOLLOWING OR NOT
    k1,k2=0,0
    following,followers=get_follow(current_user.username)
    #print(following, user.username)
    if user.username not in following:
        k1=1
    else:
        k2=1
    ############################
    ############################
    ##FOLLOW FORM
    if request.method=='POST' :
        if request.form['action'] == 'Follow':
            if user.username in (get_follow(current_user.username)):
                k2=1
                #print('outhere')
            else:    
                fol=User_info(followers='',following=username,username=current_user.username)
                fol1=User_info(followers=current_user.username,following='',username=username)
                try:
                    db.session.add(fol)
                    db.session.add(fol1)
                    db.session.commit()
                    flash('Success', category='success')
                    return redirect('/people/'+user.username)

                except:
                    return 'Something went wrong'

    if request.method=='POST':
        if request.form['action'] == 'Unfollow':
            fol=User_info.query.all()
            jj=0
            for i in fol:
                if i.username==current_user.username:
                    if i.following==username:
                        id1=i.info_id
                if i.username==username:
                    if i.followers==current_user.username:
                        id2=i.info_id

            fol1=User_info.query.get(id1)
            fol2=User_info.query.get(id2)

            try:
                db.session.delete(fol1)
                db.session.commit()
                db.session.delete(fol2)
                db.session.commit()
                return redirect('/people/'+username)
            except:
                return 'Something went wrong'
    #print(idictf[1]['title'],len(idictf))
    ############################
    return render_template('profile_other.html',g=g,idictf=zip(ti,ca,im),nof=nof,nofi=nofi,uname=uname,f1=k1,f2=k2,first_name=fname,last_name=lname,user=current_user.username,photo= img,images=images)
@app.route('/followers')
@login_required
def followers():
    followers=User_info.query.all()
    foll_list=[]
    dictf={"first_name":[],"last_name":[],"username":[]}
    user=User.query.all()
    
    for i in followers:
        if i.username==current_user.username and i.followers not in foll_list:
            foll_list.append(i.followers)
    #print(foll_list)
    for i in user:
        #print(i.username)
        for j in foll_list:
            if i.username==j:
                dictf['first_name'].append(i.first_name)
                dictf['last_name'].append(i.last_name)
                dictf['username'].append(i.username)
    #print(dictf)
    
    return render_template('your_follower.html',dictf=zip(dictf['first_name'],dictf['last_name'],dictf['username']), followers=foll_list,user=current_user.first_name)


@app.route('/following')
@login_required
def following():
    following=User_info.query.all()
    foll_list=[]
    dictf={"first_name":[],"last_name":[],"username":[]}
    user=User.query.all()
    for i in following:
        if i.username==current_user.username and i.following not in foll_list:
            foll_list.append(i.following)
    for i in user:
        #print(i.username)
        for j in foll_list:
            if i.username==j:
                dictf['first_name'].append(i.first_name)
                dictf['last_name'].append(i.last_name)
                dictf['username'].append(i.username)
    #print(dictf)
    return render_template('people_you_follow.html',dictf=zip(dictf['first_name'],dictf['last_name'],dictf['username']),usern=current_user.username, user=current_user.first_name,following1=foll_list)

@app.route('/search/<string:searchterm>',methods=['GET','POST'])
@login_required
def search(searchterm):
    searchterm=searchterm+'*'
    result1,result2,result3=None,None,None
    result1=User_search.query.filter(User_search.first_name.op("MATCH")(searchterm)).all()
    if result1 is None or result1=='':
        result2=User_search.query.filter(User_search.username.op("MATCH")(searchterm)).all()

        if result2 is None or result2=='':
            result3=User_search.query.filter(User_search.last_name.op("MATCH")(searchterm)).all()

    #print(result1.first_name,result2.first_name,result3.first_name)
    #print(result1)
    return render_template('search.html', result1=result1, result2=result2,result3=result3,user=current_user.first_name)

@app.route('/feed', methods=['POST','GET'])
@login_required
def feed():
    alu=User.query.all()
    iages={}
    for i in alu:
        ak=b64encode(i.profile_photo)
        ak=ak.decode("UTF-8")
        iages[i.username]=ak
    for i in alu:
        if i.username==current_user.username:
            abcd=i.profile_photo
    pp=b64encode(i.profile_photo)
    pp=pp.decode("UTF-8")
    ########################
    #####!!!!TO SHOW THE FOLLOWERS LIST!!!#######
    follow=User_info.query.all()
    followers=[]
    for i in follow:
        if i.username==current_user.username:
            followers.append(i.following)
    user=User.query.all()
    users_fname,users_lname=[],[]
    for i in user:
        if (i.username in followers):
            users_fname.append(i.first_name)
            users_lname.append(i.last_name)
    ########################
    ####CHECK IF BLOGS ARE FROM FOLLOWERS########
    blogs = Blogs.query.order_by(desc(Blogs.time)).all()

    blog_posts=[]
    images_feed={}
    following,followers1=get_follow(current_user.username)
    count_following=len(following)
    count_followers=len(followers1)
    for i in blogs:
        images_feed[i.blogid]=None
        if i.username in following:
            blog_posts.append(i) #List of Blog OBJECTS
            ii=b64encode(i.image)
            ii=ii.decode("UTF-8")
            images_feed[i.blogid]=ii
            #print(i.blogid)
    
    posts=Posts.query.all()
    post_blog=[]
    for i in posts:
        for j in blogs:
            if i.post_id==j.blogid:
                post_blog.append(i)
    #print()
    ########################
    posts_all=Posts.query.all()
    
    #print(blog_posts)
    ########################
    count_likes={}
    for i in blog_posts:
        count_likes[i.blogid]=0
    for i in blog_posts:
        for j in posts_all:
            if j.likes!='' and j.post_id==i.blogid:
                count_likes[i.blogid]+=1
    #print(count_likes)
    #########################
    all_users=User.query.all()
    usernames=[]
    user_info1=User_info.query.all()
    for i in user_info1:
        if i.username==current_user.username:
            usernames.append(i.following)

    users1=User.query.all()
    users2=[]
    for i in users1:
        if i.username in usernames and (i.username not in users2):
            users2.append(i)
    nof,nofi=count_follow(current_user.username)
    if request.method=='POST':
        pid=request.form['hiddenID']
        comm=request.form['texti']
        #print((pid),comm)
        pp=Posts.query.get(pid)
    jj=User.query.filter_by(username=current_user.username).first()
    jj=b64encode(current_user.profile_photo)
    js=jj.decode("UTF-8")


    months={'1':'Jan','2':'Feb','3':'Mar','4':'April','5':'May',
    '6':'June','7':'July','8':'Aug','9':'Sep','10':'Oct','11':'Nov','12':'Dec'}

    return render_template('feed.html',count_likes=count_likes,nof=nof,nofi=nofi,
    users2=users2,current_user=current_user.username,months=months,dp=iages,all_users=all_users,
    users_fname=zip(users_fname,users_lname), pp=pp,js=js,
    user_name=current_user.username, first_name=current_user.first_name,
    count_followers=count_followers,count_following=count_following,posts_all=posts_all,
    last_name=current_user.last_name,blog_posts=blog_posts,post_blog=post_blog,images_feed=images_feed)

@app.route('/post/<string:args>')
def like_comment_share(args):
    #print("ALLLLLL")
    args=args.split('_')
    var=args[0]
    id=int(args[1])
    get_post=Posts.query.filter_by(post_id=id).first()
    #print(var,id)
    all_likers=[]
    for i in Posts.query.all():
        if i.post_id==id:
            all_likers.append(i.likes)
    
    if current_user.username  in all_likers and var=='like':
        flash('Already Liked', category='error')
        return redirect('/feed')

    
    
    #print(args)
    if get_post and var=='like' and get_post.likes==current_user.username:
        flash('Already Liked', category='error')
    elif var=='like':
        if get_post and get_post.likes=='':
            get_post.likes=current_user.username
            get_post.author=current_user.username
            #print('changed', get_post.post_id,get_post.likes, get_post.author)
            db.session.commit()
            return redirect('/feed')
        else:
            pp=Posts(post_id=id,comment='', likes=current_user.username,author=current_user.username )
            db.session.add(pp)
            db.session.commit()
            return redirect('/feed')
        
    elif 'unlike'==var:
        if get_post:
            if get_post.likes!='':
                get_post.likes=''
                get_post.author=current_user.username
                db.session.commit()
                #print('HREE')
                return redirect('/feed')
            else:
                flash('You need to like first', category='error')
        else:
                flash('You need to like first', category='error')
       
                
    


    # if 'share' in args:
    #     args=args.split('_')
    #     return redirect(url_for('feed'))
    # # if 'comment'==var:
    # #     #print(args)

    return redirect('/feed')
def get_follow(username):
    following,followers=[],[]
    follow=User_info.query.all()
    for i in follow:
        if i.username==username:
            #print(i.username)
            following.append(i.following)
            followers.append(i.followers)
    return following,followers

@app.route('/comment/<string:ids>', methods=['POST', "GET"])
def add_comment(ids): 
    #ids=ids.split('_')
    blogid=int(ids)
    #pid=ids[1]
    posts=Posts.query.filter_by(post_id=blogid).first()

    if request.method=='POST':
        comm=request.form['comment_area']
        if posts and posts.comment=='':
            posts.comment=comm
            posts.author=current_user.username
            db.session.commit()
        else:
            pp=Posts(post_id=blogid, comment=comm, likes='', author=current_user.username)
            db.session.add(pp)
            db.session.commit()
    return redirect(url_for('feed'))

@app.route('/delete_comment/<int:pid>', methods=['POST','GET'])
def delete_comment(pid):
    post=Posts.query.filter_by(author=current_user.username, pid=pid).first()
    post.comment=''
    if post.likes!='':
        db.session.delete(post)
        db.session.commit()
    else:
        db.session.commit()

    return redirect(url_for('feed'))

@app.route('/edit_comment/<string:args>', methods=['POST','GET'])
def edit_comment(args):
    a=args.split('~')
    pid=a[0]
    comm=a[1]
    post=Posts.query.filter_by(author=current_user.username, pid=pid).first()
    
    if post:
        post.comment=comm
        post.author=current_user.username
        db.session.commit()
     

    return redirect(url_for('feed'))

@app.route('/edit_self_post/<string:blogid>' ,methods=['POST', "GET"])
def edit_self_post(blogid):
    blog=Blogs.query.filter_by(blogid=blogid).first()
    edit="edit_self_post/"+blogid
    self_profile1="/self/"+current_user.username
    if request.method=='POST':
        if request.form['title']!='':
            title=request.form['title']
            blog.title=title
            db.session.commit()
            return render_template('edit_self_post.html',self_profile=self_profile1,old_title=blog.title, old_caption=blog.caption )    
        if request.form['caption']!='':
            caption=request.form['caption']
            blog.caption=caption
            db.session.commit()
            return render_template('edit_self_post.html',self_profile=self_profile1,old_title=blog.title, old_caption=blog.caption )    

        if request.files['change_image']:
            blog.image=request.files['change_image'].read()
            db.session.commit()
            return render_template('edit_self_post.html',self_profile=self_profile1,old_title=blog.title, old_caption=blog.caption )    
    
    return render_template('edit_self_post.html',blogid=blogid,self_profile=self_profile1,old_title=blog.title, old_caption=blog.caption )    


@app.route('/unfollow_<string:username>')
def unfollow(username):
    all_user=User.query.all()
    abc=[]
    for i in User_info.query.all():
        if i.username==current_user.username:
            abc.append(i.following)
    if username not in abc:
        return 'You need to follow first'
    for i in all_user:
        abc.append(i.username)
    
    fol=User_info.query.all()
    jj=0
    for i in fol:
        if i.username==current_user.username:
            if i.following==username:
                id1=i.info_id
        if i.username==username:
            if i.followers==current_user.username:
                id2=i.info_id

    fol1=User_info.query.get(id1)
    fol2=User_info.query.get(id2)

    try:
        db.session.delete(fol1)
        db.session.commit()
        db.session.delete(fol2)
        db.session.commit()
        return redirect('/people/'+username)
    except:
        return 'Something went wrong'

@app.route('/follow_<string:username>')
def follow(username):
    if username==current_user.username:
        return 'You cannot follow self. Please go back'
    following1=[]
    for i in User_info.query.all():
        if i.username==current_user.username:
            following1.append(i.following)
    #print(following1,username)
    if username in following1:
        return 'You are already following, please go back'
    fol=User_info(followers='',following=username,username=current_user.username)
    fol1=User_info(followers=current_user.username,following='',username=username)
    try:
        db.session.add(fol)
        db.session.add(fol1)
        db.session.commit()
        return redirect('/people/'+username)

    except:
        return 'Something went wrong'


##############OTHER PEOPLE FOLLOWERS/FOLLOWING
@app.route('/people/<string:username>/followers')
def followers_other(username):
    dictf={"first_name":[],"last_name":[],"username":[]}
    user_info=User_info.query.all()
    followers_list=[]
    ll=[]
    for i in User.query.all():
        ll.append(i.username)
        #print(i.username)
    for i in user_info:
        if i.username==username and i.followers!='' and (i.followers in ll):
            
            followers_list.append(i.followers)
    
    list_of_followers_objects=[]
    user=User.query.all()
    #print(followers_list)

    for i in user:
        #print(i.username)
        for j in followers_list:
            if i.username==j:
                list_of_followers_objects.append(i)
    count_follow1=0
    #print(list_of_followers_objects)
    for i in list_of_followers_objects:
        #print(i.username)
        dictf['first_name'].append(i.first_name)
        dictf['last_name'].append(i.last_name)
        dictf['username'].append(i.username)
        count_follow1+=1
    ifollow=[]
    for i in user_info:
        if current_user.username==i.username and i.following!='':
            ifollow.append(i.following)

    return render_template('your_follower.html',ifollow=ifollow,dictf=zip(dictf['first_name'],dictf['last_name'],dictf['username']),username=current_user.username, user=current_user.first_name)

@app.route('/people/<string:username>/following')
def following_other(username):
    dictf={"first_name":[],"last_name":[],"username":[]}
    ll=[]
    for i in User.query.all():
        ll.append(i.username)
    user_info=User_info.query.all()
    following_list=[]
    for i in user_info:
        if i.username==username and i.following in ll:
            following_list.append(i.following)
    
    list_of_following_objects=[]
    user=User.query.all()
    for i in user:
        for j in following_list:
            if i.username==j :
                list_of_following_objects.append(i)


    
    for i in list_of_following_objects:
        dictf['first_name'].append(i.first_name)
        dictf['last_name'].append(i.last_name)
        dictf['username'].append(i.username)
    return render_template('your_follower.html',dictf=zip(dictf['first_name'],dictf['last_name'],dictf['username']),username=current_user.username, user=current_user.first_name)

##############################################


@app.route('/image/<string:blogid>')
def display_image(blogid):
    blog=Blogs.query.get(blogid)
    #print(blog.title)
    ab=b64encode(blog.image)        
    ab=ab.decode("UTF-8")
    
    
    return render_template('image.html', image_src=ab)

def count_follow(username):
    a1,a2=0,0
    uu=User_info.query.all()
    ll=[]
    for i in User.query.all():
        ll.append(i.username)
    for i in uu:
        if i.username==username and i.followers!='' and i.followers in ll:
            a1+=1
        elif i.username==username and i.following!='' and i.following in ll:
            a2+=1
    
    #print(a1,a2)
    return a1,a2

@app.route('/update_profile/<string:username>', methods=["POST","GET"])
def update_profile(username):
    user=User.query.all()
    users=[]
    main_user=None
    for i in user:
        users.append(i.username)
        if i.username==username:
            main_user=i
    
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        #uname=request.form['uname']
        dp=request.files['dp']
        mimetype=dp.mimetype
        a,b,c,d=0,0,0,0
        if fname=='':
            a=1
            flash('Firstname required', category='error')
        
        
        
        elif( a!=1 and b!=1 and c!=1):
            main_user.first_name=fname
            main_user.last_name=lname
            #main_user.username=uname
            main_user.profile_photo=dp.read()
            main_user.mimetype=mimetype

            db.session.commit()
            flash('Profile updated. Please', category='success')


    return render_template('update_profile.html', user=username)


@app.route('/change_password/<string:username>', methods=['POST', 'GET'])
def change_password(username):
    us=None
    a=0
    users=User.query.all()
    us=User.query.filter_by(username=username).first()
    #print(us.username,us.password)
    oldp=us.password
    if request.method=='POST':
        oldone=request.form['oldp']
        newp=request.form['newp']
        if len(newp)<6:
            a=1
            flash('Password too small', category='error')
        else:
            
            # print(check_password_hash(oldp,oldone))
            newp=generate_password_hash(newp,method='SHA256')
            if check_password_hash(oldp,oldone):
                #print('here')
                us.password=newp
                db.session.commit()
                
                logout()
                flash('Password change successfully', category='success')
            else:
                flash('Incorrect old password', category='error')


    return render_template('change_password.html')

@app.route('/delete_account/<string:username>', methods=['POST','GET'])
@login_required
def delete_account(username):
    abc=[]
    all_ids=[]
    pos=[]
    user=User.query.filter_by(username=current_user.username).first()
    
    for i in Blogs.query.all():
        if i.username==current_user.username:
            abc.append(i)
            all_ids.append(i.blogid)
    for i in Posts.query.all():
        if i.post_id in all_ids:
            pos.append(i)
    
    if request.method=='POST':
        
        oldp=user.password
        passw=request.form['passw']
        if (check_password_hash(oldp,passw)):
            #print(user)
            for i in pos:
                db.session.delete(i)
                db.session.commit()
            for i in abc:
                db.session.delete(i)
                db.session.commit()


            db.session.delete(User.query.filter_by(username=username).first())
            logout_user
            db.session.commit()
            return redirect('/thank_you')
        else:
            flash('Password does not match', category='error')
        
    
    return render_template('deactivate.html')

@app.route('/thank_you')
def thanks():
    return render_template('thank_you.html')

@app.route('/need_help')
def need_help():
    return render_template('need_help.html')

@app.route('/delete_post/<int:blogid>')
def delete_post(blogid):
    blog= Blogs.query.get(blogid)
    if blog:
        k=current_user.username
        db.session.delete(blog)
        db.session.commit()
        return redirect('/self/'+k)
    else:
        return 'Error, please go back'



@app.route('/edit_comment1/<int:pid>', methods=['POST',"GET"])
def edit_edit(pid):
    get_post=Posts.query.get(pid)
    old_comment=get_post.comment

    if request.method=='POST':
        newcomm=request.form['inputcomment']
        get_post.comment=newcomm
        db.session.commit()
        return redirect('/feed')
    return render_template('edit_comment.html', old_comment=old_comment)


@app.route('/liked_by/<int:blogid>')
def liked_by(blogid):
    post=Posts.query.filter_by(post_id=blogid).all()
    kk=[]
    for i in post:
        if i.likes!='':
            kk.append(i.author)
    yayuser=[]
    for i in User.query.all():
        if i.username in kk:
            yayuser.append(i)
    return render_template('those_who_like.html',likers=yayuser, current_user=current_user.username)



@app.route('/unauth')
def unauthor():

    return render_template('unauthorized.html')


from drf_yasg import openapi


class SwaggerShape:

    author_details = {
        "type": "author",
        "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "host": "http://127.0.0.1:5454/",
        "displayName": "Lara Croft",
        "url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "github": "http://github.com/laracroft",
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }

    author_list = {
        "type": "authors",
        "items": [
            {
                "type": "author",
                "id": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                "url": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                "host": "http://127.0.0.1:5454/",
                "displayName": "Greg Johnson",
                "github": "http://github.com/gjohnson",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            author_details,
        ]
    }

    follower_list = {
        "type": "followers",
        "items": [
            author_details
        ]
    }

    following_list = {
        "type": "following",
        "items": [
            author_details
        ]
    }

    post_detail = {
        "type": "post",
        "title": "A post title about a post about web dev",
        "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
        "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
        "origin": "http://whereitcamefrom.com/posts/zzzzz",
        "description": "This post discusses stuff -- brief",
        "contentType": "text/plain",
        "content": "Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge",
        "author": {
            "type": "author",
            "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "host": "http://127.0.0.1:5454/",
            "displayName": "Lara Croft",
            "url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "github": "http://github.com/laracroft",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        "categories": ["web", "tutorial"],
        "count": 1023,
        "comments": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
        "commentsSrc": {
            "type": "comments",
            "page": 1,
            "size": 5,
            "post": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
            "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
            "comments": [
                {
                    "type": "comment",
                    "author": {
                        "type": "author",
                        "id": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                        "url": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                        "host": "http://127.0.0.1:5454/",
                        "displayName": "Greg Johnson",
                        "github": "http://github.com/gjohnson",
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                    },
                    "comment": "Sick Olde English",
                    "contentType": "text/markdown",
                    "published": "2015-03-09T13:07:04+00:00",
                    "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                }
            ]
        },
        "published": "2015-03-09T13:07:04+00:00",
        "visibility": "PUBLIC",
        "unlisted": False
    }

    post_list = {
        "type": "posts",
        "items": [
            post_detail
        ]
    }

    post_detail_img = {
        "contentType": "image/png;base64",
        "content": "iVBORw0KGgoAAAANSUhEUgAAAQoAAAFmCAMAAACiIyTaAAABv1BMVEUAAAB5S0dJSkpISkpLTU3pSzzoTD3oSzzoTD3kSjvoTD1GRUbeSDpFREVCQULpSzzoTD3c3d3gSTrg4uDm5uZFRETbRznoTD3oTD1JR0iXlYXaRzncRzhBQUDnSjtNS0zUzsdnZmVLSEpMSEoyNjPm5eSZmYfm6ekzNTOloI42ODbm6Oiioo/h4eEzODbm5+eop5SiopCiopDl396hloaDg3ToTD3m5uZMS03///9RTlAAAADy8vIgICA2NzY4OzYPM0fa29qgoI7/zMnj4+PW19VGRkbqPi7v7/D6+vr09fXyTj4rKSvhSTo/Pj/oSDnlMyLsNCI0MTP0///tTT7ZRjizOi+6PDDmLRyenZ7oKRfExMT/TzvobGEVFBWGhYUAGjLW8/ToXVADLUZ8e33/2tfRRTdWVFTFQDT1u7aSkZIADib+5eFwcHHW+/z70tDwkIesPTPW6+teXV2xsbG7u7vY4+Lre3DMzM2qp6jilIxsPT7lg3kdO07m/f4AJjuwsJzftK/fpZ7woJjoVUZBWGj1zMdTaXfcvrrzq6Tby8f+8u8wSlYZNDaQRUKfr7d9j5lpf4vx5ePMsLF/o64s+PNlAAAANnRSTlMAC1IoljoZWm2yloPRGWiJfdjEEk037Esq7Pn24EKjpiX+z7rJNNWB5pGxZ1m2mZY/gXOlr43C+dBMAAAmkklEQVR42uzay86bMBAF4MnCV1kCeQFIRn6M8xZe+v1fpVECdtPSy5822Bi+JcujmfEApl3IIRhBFyIJ3Em6UMTDSKfHsOB0dhILQ2fX4+4aF0tVXC3yJJB4OrcJV1msIhJN52avslhpZOfcvyepfceIaARw5t2CWTwYRhSQTdSum1TGqE5Mr0kg6Ukj66hZ3GExaEaJQsYIWXzmd6P2KHxn6NjG4/BDMEQ6RM+oNQ6vjJyWFTNTDJlau0e1drAO+Ikan8tE1itkfC0S11iXKGyYJZFB5jpkgmY8WWoKx6Z5JI3MGyQqV1Jj80Jgm2J9xGrQSAKfcyptEfgFrxxWnUUiVEqIGjN5bAsRKyOReI9FaGxw3o0Of8I6rAbbcBR06yN+T+Uogmu2QR5ucsaXuV6w1hath9HiDWGwWrLmOoUL7/CWYLRo6/2d9zPeN6hONNEvXKiIf2fkwauDCxXwcPI0mA/4v+whvw=="
    }

    post_request_body = {
        "type": openapi.Schema(type=openapi.TYPE_STRING),
        "title": openapi.Schema(type=openapi.TYPE_STRING),
        "id": openapi.Schema(type=openapi.TYPE_STRING),
        "source": openapi.Schema(type=openapi.TYPE_STRING),
        "origin": openapi.Schema(type=openapi.TYPE_STRING),
        "description": openapi.Schema(type=openapi.TYPE_STRING),
        "contentType": openapi.Schema(type=openapi.TYPE_STRING),
        "content": openapi.Schema(type=openapi.TYPE_STRING),
        "author": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "categories": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "count": openapi.Schema(type=openapi.TYPE_NUMBER),
        "comments": openapi.Schema(type=openapi.TYPE_STRING),
        "commentsSrc": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "published": openapi.Schema(type=openapi.TYPE_STRING),
        "visibility": openapi.Schema(type=openapi.TYPE_STRING),
        "unlisted": openapi.Schema(type=openapi.TYPE_BOOLEAN)
    }

    comment_list = {
        "type": "comments",
        "page": 1,
        "size": 5,
        "post": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
        "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
        "comments": [
            {
                "type": "comment",
                "author": {
                    "type": "author",
                    "id": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                    "url": "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                    "host": "http://127.0.0.1:5454/",
                    "displayName": "Greg Johnson",
                    "github": "http://github.com/gjohnson",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                },
                "comment": "Sick Olde English",
                "contentType": "text/markdown",
                "published": "2015-03-09T13:07:04+00:00",
                "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
            }
        ]
    }

    comment_request_body = {
        "type": openapi.Schema(type=openapi.TYPE_STRING),
        "author": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "comment": openapi.Schema(type=openapi.TYPE_STRING),
        "contentType": openapi.Schema(type=openapi.TYPE_STRING),
        "published": openapi.Schema(type=openapi.TYPE_STRING),
        "id": openapi.Schema(type=openapi.TYPE_STRING),
    }

    like_detail = {
        "type": "like",
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Lara Croft Likes your comment",
        "author": {
            "type": "author",
            "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "host": "http://127.0.0.1:5454/",
            "displayName": "Lara Croft",
            "url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "github": "http://github.com/laracroft",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        "object": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e"
    }

    liked_list = {
        "type": "liked",
        "items": [
            like_detail
        ]
    }

    likes_list = {
        "type": "likes",
        "items": [
            like_detail
        ]
    }

    like_request_body = {
        "type": openapi.Schema(type=openapi.TYPE_STRING),
        "@context": openapi.Schema(type=openapi.TYPE_STRING),
        "summary": openapi.Schema(type=openapi.TYPE_STRING),
        "author": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "object": openapi.Schema(type=openapi.TYPE_STRING),
    }

    post_request_body = {
        "type": openapi.Schema(type=openapi.TYPE_STRING),
        "title": openapi.Schema(type=openapi.TYPE_STRING),
        "id": openapi.Schema(type=openapi.TYPE_STRING),
        "source": openapi.Schema(type=openapi.TYPE_STRING),
        "origin": openapi.Schema(type=openapi.TYPE_STRING),
        "description": openapi.Schema(type=openapi.TYPE_STRING),
        "contentType": openapi.Schema(type=openapi.TYPE_STRING),
        "content": openapi.Schema(type=openapi.TYPE_STRING),
        "author": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "categories": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "count": openapi.Schema(type=openapi.TYPE_NUMBER),
        "comments": openapi.Schema(type=openapi.TYPE_STRING),
        "commentsSrc": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "published": openapi.Schema(type=openapi.TYPE_STRING),
        "visibility": openapi.Schema(type=openapi.TYPE_STRING),
        "unlisted": openapi.Schema(type=openapi.TYPE_BOOLEAN)
    }

    inbox_list = {
        "type": "inbox",
        "author": "http://127.0.0.1:5454/authors/c1e3db8ccea4541a0f3d7e5c75feb3fb",
        "items": [
            {
                "type": "post",
                "title": "A Friendly post title about a post about web dev",
                "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
                "origin": "http://whereitcamefrom.com/posts/zzzzz",
                "description": "This post discusses stuff -- brief",
                "contentType": "text/plain",
                "content": "Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                "author": {
                  "type": "author",
                  "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                  "host": "http://127.0.0.1:5454/",
                  "displayName": "Lara Croft",
                  "url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                  "github": "http://github.com/laracroft",
                  "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                },
                "categories": ["web", "tutorial"],
                "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                "published":"2015-03-09T13:07:04+00:00",
                "visibility":"FRIENDS",
                "unlisted": False,
            },
            {
                "type": "post",
                "title": "DID YOU READ MY POST YET?",
                "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e",
                "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
                "origin": "http://whereitcamefrom.com/posts/zzzzz",
                "description": "Whatever",
                "contentType": "text/plain",
                "content": "Are you even reading my posts Arjun?",
                "author": {
                    "type": "author",
                    "id": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    "host": "http://127.0.0.1:5454/",
                    "displayName": "Lara Croft",
                    "url": "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    "github": "http://github.com/laracroft",
                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                },
                "categories": ["web", "tutorial"],
                "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                "published":"2015-03-09T13:07:04+00:00",
                "visibility":"FRIENDS",
                "unlisted": False,
            }
        ]
    }

    follow_request_body = {
        "type": openapi.Schema(type=openapi.TYPE_STRING),
        "summary": openapi.Schema(type=openapi.TYPE_STRING),
        "actor": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
        "object": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
    }

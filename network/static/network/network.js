function like_post(post_id) {
    fetch('like_post', {
        method: "POST",
        body: JSON.stringify({
            post_id: post_id
        })
    }).then(response => response.json())
    .then(r => {
        let likes = document.getElementById(`post-item-meta-likes-${post_id}`)
        let like_btn =  document.getElementById(`post-item-meta-like-btn-${post_id}`)
        let likes_count = r.likes
        if (r.postUpdateStatus == 'liked'){
            like_btn.innerHTML = "&#128078;"
        } else {
            like_btn.innerHTML = "&#128077;"
        }
        likes.innerHTML = likes_count
    })
}

function follow_user(profile_id) {
    fetch('follow/', {
        method: "POST",
        body: JSON.stringify({
            profile_id: profile_id
        })
    }).then(response => response.json())
    .then(r => {
        if (r.followStatus == "followed"){
            document.getElementById(`follow-profile-btn`).innerHTML = "Unfollow"
        }
    })
};

//function display_follow_stats(followType, profile_id) {
//    fetch('get_follow_stats/', {
//        method: "GET",
//        body: JSON.stringify({
//            profile_id: profile_id
//        })
//    }).then(response => response.json())
//    .then(r => {
//        if (r.status == 200) {
//                console.log('Response ok')
//                console.log(r.follower_stats)
//        } else {
//            console.log('Failed to get response')
//        }
//    })
//}

//function display_follow_stats(followType, profile_id) {
//    fetch('get_follow_stats/', {
//        method: "GET",
//    }).then(response => response.json())
//    .then(r => {
//        console.log(r.status)
//        if (r.status === 200) {
//            console.log('Response ok')
//        }
//        if (r.status == 200) {
//                console.log('Response ok')
//                console.log(r.follower_stats)
//        } else {
//            console.log('Failed to get response')
//        }
//    })
//}


function get_follow_stats(followType, profile_id) {
    fetch('get_follow_stats/')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        display_follow_stats(followType, data)
    })
    .catch(error => {
        console.error('Server error, couldn\'t fetch follower data: ', error);
    })
};

function display_follow_stats(followType, data){
    console.log(data)
    data = data['follower_stats']



    if (followType === 'followers') {
        // build the follower list
        let followerOverlay = document.getElementById("follower-overlay")
        followerOverlay.style.visibility = "visible";
        let followerList = document.createElement("div")
        followerList.id = "follower-list"
        followerList.textContent = "Followers"
        followerOverlay.appendChild(followerList)

        for (let i = 0; i < data[followType].length; i++ ){
            let followerLink = document.createElement("a")
            followerLink.href = "/profile/" + data[followType][i][0]
            let follower = document.createElement("li")
            follower.innerText = data[followType][i][1]

            followerLink.appendChild(follower)
            followerList.appendChild(followerLink)
            console.log(data[followType][i][1])
        }

    } else if (followType === 'following') {
        // build the following list
        let followingOverlay = document.getElementById("following-overlay")
        followingOverlay.style.visibility = "visible";
        let followingList = document.createElement("div")
        followingList.id = "following-list"
        followingOverlay.appendChild(followingList)

        for (let i = 0; i < data[followType].length; i++ ){
            let followingLink = document.createElement("a")
            followingLink.href = "/profile/" + data[followType][i][0]
            let following = document.createElement("li")
            following.innerText = data[followType][i][1]

            followingLink.appendChild(following)
            followingList.appendChild(followingLink)
            console.log(data[followType][i][1])
        }
    }
}

function closeFollower() {
  document.getElementById("follower-overlay").style.visibility = "hidden";

  // clear the list contents
  document.getElementById("follower-list").innerHTML = '';

  // remove the list itself
  document.getElementById("follower-list").remove();
}

function closeFollowing() {
  document.getElementById("following-overlay").style.visibility = "hidden";

  // clear the list contents
  document.getElementById("following-list").innerHTML = '';

  // remove the list itself
  document.getElementById("following-list").remove();
}
function like_post(post_id) {
    fetch('../../like_post', {
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
            count = parseInt(document.getElementById(`follower-count`).innerHTML) + 1
            document.getElementById(`follower-count`).innerHTML = count
        } else if (r.followStatus == "unfollowed"){
            document.getElementById(`follow-profile-btn`).innerHTML = "follow"
            count = parseInt(document.getElementById(`follower-count`).innerHTML) - 1
            document.getElementById(`follower-count`).innerHTML = count
        } else {
            console.log("Something went wrong with the follow/unfollow feature")
        }
    })
};


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

    // create the background of the follower/following list
    let followStatsOverlay = document.createElement("div")
    followStatsOverlay.id = "follow-stats-overlay"

    // create the list containing our follow(ers/ings)
    let followStatList = document.createElement("div")
    followStatList.id = "follow-stat-list"

    if (followType === 'followers') {
        followStatList.textContent = "Followers"
    } else if (followType == 'following') {
        followStatList.textContent = "Following"
    }
    followStatsOverlay.appendChild(followStatList)

    // build the list of follow(ers/ings)
    for (let i = 0; i < data[followType].length; i++ ){
        let followStatLink = document.createElement("a")
        followStatLink.href = "/profile/" + data[followType][i][0]
        let followStatUser = document.createElement("li")
        followStatUser.innerText = data[followType][i][1]

        followStatLink.appendChild(followStatUser)
        followStatList.appendChild(followStatLink)
    }
    document.body.appendChild(followStatsOverlay)

    // if the user clicks outside of the visible list, close the overlay
    document.addEventListener("click", function(evt) {
        target = evt.target;
        if (target == followStatsOverlay) {
            followStatList.remove();
            followStatsOverlay.remove();
        }
    })

};



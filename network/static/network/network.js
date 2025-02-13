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
}


document.addEventListener("DOMContentLoaded", () => {
    const followButton = document.querySelector("#follow-button")

    if (followButton) {
        followButton.onclick = () => {
            fetch(`/user/${followButton.dataset.userId}`, { method: "PUT" })
                .then(response => response.json())
                .then(data => {
                    document.querySelector("#follower-count").innerHTML = data.follower_count;
                    if (data.is_following) {
                        followButton.innerHTML = "Unfollow";
                        followButton.classList.replace("btn-primary", "btn-danger");
                    }
                    else {
                        followButton.innerHTML = "Follow";
                        followButton.classList.replace("btn-danger", "btn-primary");
                    }
                })
        }
    }
})